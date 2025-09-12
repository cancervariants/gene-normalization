"""Provide utilities for test cases."""

import logging
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from gene.database import AbstractDatabase, create_db
from gene.schemas import RecordType, RefType, SourceMeta, SourceName


@pytest.fixture(scope="session")
def database() -> AbstractDatabase:
    """Create database instance."""
    return create_db()


def pytest_addoption(parser):
    """Add custom commands to pytest invocation.
    See https://docs.pytest.org/en/7.1.x/reference/reference.html#parser
    """
    parser.addoption(
        "--verbose-logs",
        action="store_true",
        default=False,
        help="show noisy module logs",
    )


def pytest_configure(config):
    """Configure pytest setup."""
    if not config.getoption("--verbose-logs"):
        logging.getLogger("botocore").setLevel(logging.ERROR)
        logging.getLogger("boto3").setLevel(logging.ERROR)
        logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)


def _compare_records(normalized_gene, test_gene, match_type):
    """Check that normalized_gene and test_gene are the same."""
    assert normalized_gene.match_type == match_type
    assert normalized_gene.label == test_gene.label
    assert normalized_gene.concept_id == test_gene.concept_id
    assert set(normalized_gene.aliases) == set(test_gene.aliases)
    assert set(normalized_gene.xrefs) == set(test_gene.xrefs)
    assert normalized_gene.symbol_status == test_gene.symbol_status
    assert set(normalized_gene.previous_symbols) == set(test_gene.previous_symbols)
    assert set(normalized_gene.associated_with) == set(test_gene.associated_with)
    assert normalized_gene.symbol == test_gene.symbol
    assert len(normalized_gene.locations) == len(test_gene.locations)
    for loc in normalized_gene.locations:
        assert loc.id.split("ga4gh:SL.")[-1] == loc.digest
        loc.id = None
        loc.digest = None
        assert loc in test_gene.locations
    assert set(normalized_gene.location_annotations) == set(
        test_gene.location_annotations
    )
    assert normalized_gene.strand == test_gene.strand
    assert normalized_gene.gene_type == test_gene.gene_type


@pytest.fixture(scope="session")
def compare_records():
    """Provide record(s) comparison function"""
    return _compare_records


def _check_resp_single_record(resp, test_gene, match_type):
    """Check that responses with single response return expected result"""
    assert len(resp.records) == 1
    _compare_records(resp.records[0], test_gene, match_type)


@pytest.fixture(scope="session")
def check_resp_single_record():
    """Provide record comparison function for single record"""
    return _check_resp_single_record


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide Path instance pointing to test data directory"""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def null_database_class():
    """Quote-unquote 'in-memory database' used like a mock for testing.
    Parameters for specific methods enabled as needed. See `tests/unit/test_utils.py`
    for example usage.
    """

    class _Database(AbstractDatabase):
        def __init__(self, db_url: str | None = None, **db_args) -> None:  # noqa: ARG002
            self._get_all_records_values = db_args.get("get_all_records", {})

        def list_tables(self) -> list[str]:
            raise NotImplementedError

        def drop_db(self) -> None:
            raise NotImplementedError

        def check_schema_initialized(self) -> bool:
            raise NotImplementedError

        def check_tables_populated(self) -> bool:
            raise NotImplementedError

        def initialize_db(self) -> None:
            raise NotImplementedError

        def get_source_metadata(self, src_name: str | SourceName) -> dict:
            raise NotImplementedError

        def get_record_by_id(
            self, concept_id: str, case_sensitive: bool = True, merge: bool = False
        ) -> dict | None:
            raise NotImplementedError

        def get_refs_by_type(self, search_term: str, ref_type: RefType) -> list[str]:
            raise NotImplementedError

        def get_all_concept_ids(self, source: SourceName | None = None) -> set[str]:
            raise NotImplementedError

        def get_all_records(
            self, record_type: RecordType
        ) -> Generator[dict, None, None]:
            yield from self._get_all_records_values[record_type]

        def add_source_metadata(self, src_name: SourceName, data: SourceMeta) -> None:
            raise NotImplementedError

        def add_record(self, record: dict, src_name: SourceName) -> None:
            raise NotImplementedError

        def add_merged_record(self, record: dict) -> None:
            raise NotImplementedError

        def update_merge_ref(self, concept_id: str, merge_ref: Any) -> None:  # noqa: ANN401
            raise NotImplementedError

        def delete_normalized_concepts(self) -> None:
            raise NotImplementedError

        def delete_source(self, src_name: SourceName) -> None:
            raise NotImplementedError

        def complete_write_transaction(self) -> None:
            raise NotImplementedError

        def close_connection(self) -> None:
            raise NotImplementedError

        def load_from_remote(self, url: str | None = None) -> None:
            raise NotImplementedError

        def export_db(self, export_location: Path) -> None:
            raise NotImplementedError

    return _Database
