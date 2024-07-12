"""Provide utilities for test cases."""

import logging

import pytest

from gene.database import AbstractDatabase, create_db


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
