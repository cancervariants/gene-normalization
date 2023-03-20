"""This module provides a CLI util to make updates to normalizer database."""
from collections.abc import Collection
import logging
import os
from pathlib import Path
from timeit import default_timer as timer
from typing import List, Optional

import click

from gene import SOURCES
from gene.database import AbstractDatabase, DatabaseReadException, \
    DatabaseWriteException
from gene.database import create_db
from gene.database.database import DatabaseException
from gene.etl import NCBI, HGNC, Ensembl  # noqa: F401
from gene.etl.merge import Merge
from gene.schemas import SourceName


logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


@click.command()
@click.option("--data_url", help="URL to data dump")
@click.option("--db_url", help="URL endpoint for the application database.")
def update_from_remote(data_url: Optional[str], db_url: str) -> None:
    r"""Update data from remotely-hosted DB dump. By default, fetches from latest
    available dump on VICC S3 bucket; specific URLs can be provided instead by
    command line option or GENE_NORM_REMOTE_DB_URL environment variable.

    \f
    :param data_url: user-specified location to pull DB dump from
    """
    if not click.confirm("Are you sure you want to overwrite existing data?"):
        click.get_current_context().exit()
    if not data_url:
        data_url = os.environ.get("GENE_NORM_REMOTE_DB_URL")
    db = create_db(db_url, False)
    try:
        db.load_from_remote(data_url)
    except NotImplementedError:
        click.echo(f"Error: Fetching remote data dump not supported for {db.__class__.__name__}")  # noqa: E501
        click.get_current_context().exit(1)
    except DatabaseException as e:
        click.echo(f"Encountered exception during update: {str(e)}")
        click.get_current_context().exit(1)


@click.command()
@click.option(
    "--output_directory", "-o",
    help="Output location to write to",
    type=click.Path(exists=True, path_type=Path)
)
@click.option("--db_url", help="URL endpoint for the application database.")
def dump_database(output_directory: Path, db_url: str):
    r"""Dump data from database into file.

    \f
    :param output_directory: path to existing directory
    """
    if not output_directory:
        output_directory = Path(".")

    db = create_db(db_url, False)
    try:
        db.export_db(output_directory)
    except NotImplementedError:
        click.echo(f"Error: Dumping data to file not supported for {db.__class__.__name__}")  # noqa: E501
        click.get_current_context().exit(1)
    except DatabaseException as e:
        click.echo(f"Encountered exception during update: {str(e)}")
        click.get_current_context().exit(1)


def _help_msg():
    """Display help message."""
    ctx = click.get_current_context()
    click.echo("Must either enter 1 or more sources, or use `--update_all` parameter")  # noqa: E501
    click.echo(ctx.get_help())
    ctx.exit()


def _update_normalizers(
    normalizers: Collection[SourceName], db: AbstractDatabase, update_merged: bool
) -> None:
    """Update selected normalizer sources."""
    processed_ids = list()
    for n in normalizers:
        delete_time = _delete_source(n, db)
        _load_source(n, db, delete_time, processed_ids)

    if update_merged:
        _load_merge(db, processed_ids)


def _delete_source(n: SourceName, db: AbstractDatabase) -> float:
    """Delete individual source data."""
    msg = f"Deleting {n.value}..."
    click.echo(f"\n{msg}")
    logger.info(msg)
    start_delete = timer()
    db.delete_source(n)
    end_delete = timer()
    delete_time = end_delete - start_delete
    msg = f"Deleted {n.value} in {delete_time:.5f} seconds."
    click.echo(f"{msg}\n")
    logger.info(msg)
    return delete_time


def _load_source(
    n: SourceName, db: AbstractDatabase, delete_time: float, processed_ids: List[str]
) -> None:
    """Load individual source data."""
    msg = f"Loading {n.value}..."
    click.echo(msg)
    logger.info(msg)
    start_load = timer()

    # used to get source class name from string
    # TODO hm
    SourceClass = eval(n.value)
    # SOURCES_CLASS = \
    #     {s.value.lower(): eval(s.value) for s in SourceName.__members__.values()}

    source = SourceClass(database=db)
    processed_ids += source.perform_etl()
    end_load = timer()
    load_time = end_load - start_load
    msg = f"Loaded {n.value} in {load_time:.5f} seconds."
    click.echo(msg)
    logger.info(msg)
    msg = f"Total time for {n.value}: {(delete_time + load_time):.5f} seconds."
    click.echo(msg)
    logger.info(msg)


def _delete_normalized_data(database):
    """Delete normalized concepts"""
    click.echo("\nDeleting normalized records...")
    start_delete = timer()
    try:
        database.delete_normalized_concepts()
    except (DatabaseReadException, DatabaseWriteException) as e:
        click.echo(f"Encountered exception during normalized data deletion: {e}")
    end_delete = timer()
    delete_time = end_delete - start_delete
    click.echo(f"Deleted normalized records in {delete_time:.5f} seconds.")


def _load_merge(db, processed_ids):
    """Load merged concepts"""
    start = timer()
    _delete_normalized_data(db)
    if not processed_ids:
        processed_ids = db.get_all_concept_ids()
    merge = Merge(database=db)
    click.echo("Constructing normalized records...")
    merge.create_merged_concepts(processed_ids)
    end = timer()
    click.echo(f"Merged concept generation completed in "
               f"{(end - start):.5f} seconds")


@click.command()
@click.option(
    '--normalizer',
    help="The normalizer(s) you wish to update separated by spaces."
)
@click.option(
    '--aws_instance',
    is_flag=True,
    help="Using AWS DynamodDB instance."
)
@click.option(
    '--db_url',
    help="URL endpoint for the application database."
)
@click.option(
    '--update_all',
    is_flag=True,
    help='Update all normalizer sources.'
)
@click.option(
    '--update_merged',
    is_flag=True,
    help='Update concepts for normalize endpoint from accepted sources.'
)
def update_normalizer_db(normalizer, aws_instance, db_url, update_all,
                         update_merged):
    """Update selected normalizer source(s) in the gene database."""
    db = create_db(db_url, aws_instance)

    if update_all:
        _update_normalizers(list(SourceName), db, update_merged)
    elif not normalizer:
        if update_merged:
            _load_merge(db, [])
        else:
            _help_msg()
    else:
        normalizers = normalizer.lower().split()

        if len(normalizers) == 0:
            raise Exception("Must enter a normalizer")

        non_sources = set(normalizers) - set(SOURCES)

        if len(non_sources) != 0:
            raise Exception(f"Not valid source(s): {non_sources}")

        sources_to_update = {SourceName(SOURCES[s]) for s in normalizers}
        _update_normalizers(sources_to_update, db, update_merged)


if __name__ == '__main__':
    update_normalizer_db()
