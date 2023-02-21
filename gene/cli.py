"""This module provides a CLI util to make updates to normalizer database."""
from collections.abc import Collection
import logging
from os import environ
from timeit import default_timer as timer
from typing import List

import click

from gene import SOURCES
from gene.database import AbstractDatabase, DatabaseReadException, \
    DatabaseWriteException, confirm_aws_db_use, \
    SKIP_AWS_DB_ENV_NAME, VALID_AWS_ENV_NAMES, AWS_ENV_VAR_NAME
from gene.etl import NCBI, HGNC, Ensembl  # noqa: F401
from gene.etl.merge import Merge
from gene.schemas import SourceName


logger = logging.getLogger('gene')
logger.setLevel(logging.DEBUG)


class CLI:
    """Class for updating the normalizer database via Click"""

    @staticmethod
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
        # If SKIP_AWS_CONFIRMATION is accidentally set, we should verify that the
        # aws instance should actually be used
        invalid_aws_msg = f"{AWS_ENV_VAR_NAME} must be set to one of {VALID_AWS_ENV_NAMES}"  # noqa: E501
        aws_env_var_set = False
        if AWS_ENV_VAR_NAME in environ:
            aws_env_var_set = True
            assert environ[AWS_ENV_VAR_NAME] in VALID_AWS_ENV_NAMES, invalid_aws_msg
            confirm_aws_db_use(environ[AWS_ENV_VAR_NAME].upper())

        if aws_env_var_set or aws_instance:
            assert AWS_ENV_VAR_NAME in environ, invalid_aws_msg
            environ[SKIP_AWS_DB_ENV_NAME] = "true"  # this is already checked above

            from gene.database.dynamodb import DynamoDbDatabase
            db = DynamoDbDatabase()
        else:
            if db_url:
                endpoint_url = db_url
            elif 'GENE_NORM_DB_URL' in environ.keys():
                endpoint_url = environ['GENE_NORM_DB_URL']
            else:
                endpoint_url = 'http://localhost:8000'

            # prefer DynamoDB unless connection explicitly reads like a libpq URI
            if endpoint_url.startswith("postgres"):
                from gene.database.postgresql import PostgresDatabase
                db = PostgresDatabase(endpoint_url)
            else:
                from gene.database.dynamodb import DynamoDbDatabase
                db = DynamoDbDatabase(endpoint_url)

        if update_all:
            CLI()._update_normalizers(list(SourceName), db, update_merged)
        elif not normalizer:
            if update_merged:
                CLI()._load_merge(db, [])
            else:
                CLI()._help_msg()
        else:
            normalizers = normalizer.lower().split()

            if len(normalizers) == 0:
                raise Exception("Must enter a normalizer")

            non_sources = set(normalizers) - set(SOURCES)

            if len(non_sources) != 0:
                raise Exception(f"Not valid source(s): {non_sources}")

            sources_to_update = {SourceName(SOURCES[s]) for s in normalizers}
            CLI()._update_normalizers(sources_to_update, db, update_merged)

    @staticmethod
    def _help_msg():
        """Display help message."""
        ctx = click.get_current_context()
        click.echo("Must either enter 1 or more sources, or use `--update_all` parameter")  # noqa: E501
        click.echo(ctx.get_help())
        ctx.exit()

    @staticmethod
    def _update_normalizers(
        normalizers: Collection[SourceName], db: AbstractDatabase, update_merged: bool
    ) -> None:
        """Update selected normalizer sources."""
        processed_ids = list()
        for n in normalizers:
            delete_time = CLI()._delete_source(n, db)
            CLI()._load_source(n, db, delete_time, processed_ids)

        if update_merged:
            CLI()._load_merge(db, processed_ids)

    @staticmethod
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

    @staticmethod
    def _load_source(
        n: SourceName, db: AbstractDatabase, delete_time: float,
        processed_ids: List[str]
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
        msg = f"Loaded {n} in {load_time:.5f} seconds."
        click.echo(msg)
        logger.info(msg)
        msg = f"Total time for {n}: {(delete_time + load_time):.5f} seconds."
        click.echo(msg)
        logger.info(msg)

    @staticmethod
    def _load_merge(db, processed_ids):
        """Load merged concepts"""
        start = timer()
        if not processed_ids:
            CLI()._delete_normalized_data(db)
            processed_ids = db.get_all_concept_ids()
        merge = Merge(database=db)
        click.echo("Constructing normalized records...")
        merge.create_merged_concepts(processed_ids)
        end = timer()
        click.echo(f"Merged concept generation completed in "
                   f"{(end - start):.5f} seconds")

    @staticmethod
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


if __name__ == '__main__':
    CLI().update_normalizer_db()
