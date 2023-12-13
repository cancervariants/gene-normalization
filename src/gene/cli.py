"""Provides a CLI util to make updates to normalizer database."""
import logging
import os
from pathlib import Path
from typing import Optional, Tuple

import click

from gene.database import create_db
from gene.database.database import DatabaseException
from gene.etl.update import update_all_sources, update_normalized, update_source
from gene.schemas import SourceName

logger = logging.getLogger("gene")
logger.setLevel(logging.DEBUG)


url_description = 'URL endpoint for the application database. Can either be a URL to a local DynamoDB server (e.g. "http://localhost:8001") or a libpq-compliant PostgreSQL connection description (e.g. "postgresql://postgres:password@localhost:5432/gene_normalizer").'


@click.group()
def cli() -> None:
    """Manage Gene Normalizer data."""


@cli.command()
@click.argument("sources", nargs=-1)
@click.option("--all", is_flag=True, help="Update records for all sources.")
@click.option("--normalize", is_flag=True, help="Create normalized records.")
@click.option("--db_url", help=url_description)
@click.option("--aws_instance", is_flag=True, help="Use cloud DynamodDB instance.")
@click.option(
    "--use_existing",
    is_flag=True,
    default=False,
    help="Use most recent local source data instead of fetching latest version",
)
@click.option(
    "--silent", "-s", is_flag=True, default=False, help="Suppress console output."
)
def update(
    sources: Tuple[str],
    aws_instance: bool,
    db_url: str,
    all: bool,
    normalize: bool,
    use_existing: bool,
    silent: bool,
) -> None:
    """Update provided normalizer SOURCES in the gene database.

    Valid SOURCES are "HGNC", "NCBI", and "Ensembl" (case is irrelevant). SOURCES are
    optional, but if not provided, either --all or --normalize must be used.

    For example, the following command will update NCBI and HGNC source records:

        $ gene-normalizer update HGNC NCBI

    To completely reload all source records and construct normalized concepts, use the
    --all and --normalize options:

        $ gene-normalizer update --all --normalize

    The Gene Normalizer will fetch the latest available data from all sources if local
    data is out-of-date. To suppress this and force usage of local files only, use the
    --use_existing flag:

        $ gene-normalizer update --all --use_existing

    \f
    :param sources: tuple of raw names of sources to update
    :param aws_instance: if true, use cloud instance
    :param db_url: URI pointing to database
    :param all: if True, update all sources (ignore ``sources``)
    :param normalize: if True, update normalized records
    :param use_existing: if True, use most recent local data instead of fetching latest version
    """  # noqa: D301
    if (not sources) and (not all) and (not normalize):
        click.echo(
            "Error: must provide SOURCES or at least one of --all, --normalize\n"
        )
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit(1)

    db = create_db(db_url, aws_instance)

    processed_ids = None
    if all:
        processed_ids = update_all_sources(db, use_existing, silent=silent)
    elif sources:
        parsed_sources = []
        failed_source_names = []
        for source in sources:
            try:
                parsed_sources.append(SourceName[source.upper()])
            except KeyError:
                failed_source_names.append(source)
        if len(failed_source_names) != 0:
            click.echo(f"Error: unrecognized sources: {failed_source_names}")
            click.echo(f"Valid source options are {list(SourceName)}")
            click.get_current_context().exit(1)

        parsed_sources = list(set(parsed_sources))
        working_processed_ids = set()
        for source_name in parsed_sources:
            working_processed_ids |= update_source(
                source_name, db, use_existing=use_existing, silent=silent
            )
        if len(sources) == len(SourceName):
            processed_ids = working_processed_ids

    if normalize:
        update_normalized(db, processed_ids, silent=silent)


@cli.command()
@click.option("--data_url", help="URL to data dump")
@click.option("--db_url", help=url_description)
def update_from_remote(data_url: Optional[str], db_url: str) -> None:
    """Update data from remotely-hosted DB dump. By default, fetches from latest
    available dump on VICC S3 bucket; specific URLs can be provided instead by
    command line option or GENE_NORM_REMOTE_DB_URL environment variable.

    \f
    :param data_url: user-specified location to pull DB dump from
    :param db_url: URL to normalizer database
    """  # noqa: D301
    if not click.confirm("Are you sure you want to overwrite existing data?"):
        click.get_current_context().exit()
    if not data_url:
        data_url = os.environ.get("GENE_NORM_REMOTE_DB_URL")
    db = create_db(db_url, False)
    try:
        db.load_from_remote(data_url)
    except NotImplementedError:
        click.echo(
            f"Error: Fetching remote data dump not supported for {db.__class__.__name__}"
        )  # noqa: E501
        click.get_current_context().exit(1)
    except DatabaseException as e:
        click.echo(f"Encountered exception during update: {str(e)}")
        click.get_current_context().exit(1)


@cli.command()
@click.option("--db_url", help=url_description)
@click.option("--verbose", "-v", is_flag=True, help="Print result to console if set.")
def check_db(db_url: str, verbose: bool = False) -> None:
    """Perform basic checks on DB health and population. Exits with status code 1
    if DB schema is uninitialized or if critical tables appear to be empty.

        $ gene-normalizer check-db
        $ echo $?
        1  # indicates failure

    This command is equivalent to the combination of the database classes'
    ``check_schema_initialized()`` and ``check_tables_populated()`` methods:

    >>> from gene.database import create_db
    >>> db = create_db()
    >>> db.check_schema_initialized() and db.check_tables_populated()
    True  # DB passes checks

    \f
    :param db_url: URL to normalizer database
    :param verbose: if true, print result to console
    """  # noqa: D301
    db = create_db(db_url, False)
    if not db.check_schema_initialized():
        if verbose:
            click.echo("Health check failed: DB schema uninitialized.")
        click.get_current_context().exit(1)

    if not db.check_tables_populated():
        if verbose:
            click.echo("Health check failed: DB is incompletely populated.")
        click.get_current_context().exit(1)

    if verbose:
        click.echo("DB health check successful: tables appear complete.")


@cli.command()
@click.option(
    "--output_directory",
    "-o",
    help="Output location to write to",
    type=click.Path(exists=True, path_type=Path),
)
@click.option("--db_url", help=url_description)
def dump_database(output_directory: Path, db_url: str) -> None:
    """Dump data from database into file.

    \f
    :param output_directory: path to existing directory
    :param db_url: URL to normalizer database
    """  # noqa: D301
    if not output_directory:
        output_directory = Path(".")

    db = create_db(db_url, False)
    try:
        db.export_db(output_directory)
    except NotImplementedError:
        click.echo(
            f"Error: Dumping data to file not supported for {db.__class__.__name__}"
        )  # noqa: E501
        click.get_current_context().exit(1)
    except DatabaseException as e:
        click.echo(f"Encountered exception during update: {str(e)}")
        click.get_current_context().exit(1)


if __name__ == "__main__":
    cli()
