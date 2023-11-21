"""Provide functions to perform Gene Normalizer updates."""
import logging
from timeit import default_timer as timer
from typing import Optional, Set, Tuple

import click

from gene.database.database import (
    AbstractDatabase,
    DatabaseReadException,
    DatabaseWriteException,
)
from gene.schemas import SourceName

_logger = logging.getLogger(__name__)


def delete_source(
    source: SourceName, db: AbstractDatabase, silent: bool = True
) -> float:
    """Delete all data for an individual source

    :param source: name of source to delete data for
    :param db: database instance
    :param silent: if True, suppress console output
    :return: time spent deleting source
    """
    msg = f"Deleting {source.value}..."
    if not silent:
        click.echo(f"\n{msg}")
    _logger.info(msg)
    start_delete = timer()
    db.delete_source(source)
    end_delete = timer()
    delete_time = end_delete - start_delete
    msg = f"Deleted {source.value} in {delete_time:.5f} seconds."
    if not silent:
        click.echo(f"{msg}\n")
    _logger.info(msg)
    return delete_time


_etl_dependency_help = "Are ETL dependencies installed? See the Installation page in the documentation for more info."


def load_source(
    source: SourceName, db: AbstractDatabase, use_existing: bool, silent: bool = True
) -> Tuple[float, Set[str]]:
    """Load data for an individual source.

    :param source: name of source to load data for
    :param db: database instance
    :param use_existing: if True, use latest available version of local data
    :param silent: if True, suppress console output
    :return: time spent loading data, and set of processed IDs from that source
    """
    msg = f"Loading {source.value}..."
    if not silent:
        click.echo(msg)
    _logger.info(msg)
    start_load = timer()

    # used to get source class name from string
    try:
        from gene.etl import HGNC, NCBI, Ensembl  # noqa: F401
        from gene.etl.exceptions import GeneNormalizerEtlError
    except ModuleNotFoundError as e:
        click.echo(
            f"Encountered ModuleNotFoundError attempting to import {e.name}. {_etl_dependency_help}"
        )
        click.get_current_context().exit()
    sources_table = {
        SourceName.HGNC: HGNC,
        SourceName.ENSEMBL: Ensembl,
        SourceName.NCBI: NCBI,
    }

    source_class = sources_table[source](database=db)
    try:
        processed_ids = source_class.perform_etl(use_existing)
    except GeneNormalizerEtlError as e:
        _logger.error(e)
        click.echo(f"Encountered error while loading {source}: {e}.")
        click.get_current_context().exit()
    end_load = timer()
    load_time = end_load - start_load
    msg = f"Loaded {source.value} in {load_time:.5f} seconds."
    if not silent:
        click.echo(msg)
    _logger.info(msg)

    return (load_time, set(processed_ids))


def update_source(
    source: SourceName, db: AbstractDatabase, use_existing: bool, silent: bool = True
) -> Set[str]:
    """Refresh data for an individual gene data source

    :param source: name of source to update
    :param db: database instance
    :param use_existing: if True, use latest available local data
    :param silent: if True, suppress console output
    :return: IDs for records created from source
    """
    delete_time = delete_source(source, db, silent)
    load_time, processed_ids = load_source(source, db, use_existing, silent)
    msg = f"Total time for {source.value}: {(delete_time + load_time):.5f} seconds."
    if not silent:
        click.echo(msg)
    _logger.info(msg)
    return processed_ids


def update_all_sources(
    db: AbstractDatabase, use_existing: bool, silent: bool = True
) -> Set[str]:
    """Refresh data for all gene record sources

    :param db: database instance
    :param use_existing: if True, use latest available local data for all sources
    :param silent: if True, suppress console output
    :return: IDs processed from all sources
    """
    processed_ids = []
    for source in SourceName:
        source_ids = update_source(source, db, use_existing, silent)
        processed_ids.append(list(source_ids))
    return set(processed_ids)


def delete_normalized(database: AbstractDatabase, silent: bool = True) -> None:
    """Delete normalized concepts

    :param database: DB instance
    :param silent: if True, suppress console output
    """
    msg = "\nDeleting normalized records..."
    _logger.info(msg)
    if not silent:
        click.echo(msg)
    start_delete = timer()
    try:
        database.delete_normalized_concepts()
    except (DatabaseReadException, DatabaseWriteException) as e:
        click.echo(f"Encountered exception during normalized data deletion: {e}")
        raise e
    end_delete = timer()
    delete_time = end_delete - start_delete
    msg = f"Deleted normalized records in {delete_time:.5f} seconds."
    if not silent:
        click.echo(msg)
    _logger.info(msg)


def update_normalized(
    db: AbstractDatabase, processed_ids: Optional[Set[str]], silent: bool = True
) -> None:
    """Delete existing and update merged normalized records

    :param db: database instance
    :param processed_ids: IDs to form normalized records from. Provide if available to
        cut down on some potentially slow database calls. If unavailable, this method
        will fetch all known IDs directly.
    :param silent: if True, suppress console output
    """
    start = timer()
    delete_normalized(db, silent)
    if not processed_ids:
        processed_ids = db.get_all_concept_ids()

    try:
        from gene.etl.merge import Merge
    except ModuleNotFoundError as e:
        msg = f"Encountered ModuleNotFoundError attempting to import {e.name}. {_etl_dependency_help}"
        if not silent:
            click.echo(msg)
        _logger.error(msg)
        click.get_current_context().exit()

    merge = Merge(database=db)
    if not silent:
        click.echo("Constructing normalized records...")
    merge.create_merged_concepts(processed_ids)
    end = timer()
    msg = f"Merged concept generation completed in " f"{(end - start):.5f} seconds"
    if not silent:
        click.echo(msg)
    _logger.info(msg)


def update_all_and_normalize(
    db: AbstractDatabase, use_existing: bool, silent: bool = True
) -> None:
    """Update all sources as well as normalized records.

    :param db: database instance
    :param use_existing: if True, use latest local copy of data
    :param silent: if True, suppress console output
    """
    processed_ids = update_all_sources(db, use_existing, silent)
    update_normalized(db, processed_ids, silent)
