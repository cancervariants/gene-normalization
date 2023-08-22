"""Provide utilities for test cases."""
import pytest
from gene.database import AbstractDatabase, create_db


@pytest.fixture(scope="session")
def database() -> AbstractDatabase:
    """Create database instance."""
    return create_db()


def _compare_records(normalized_gene, test_gene, match_type):
    """Check that normalized_gene and test_gene are the same."""
    assert normalized_gene.match_type == match_type
    assert normalized_gene.label == test_gene.label
    assert normalized_gene.concept_id == test_gene.concept_id
    assert set(normalized_gene.aliases) == set(test_gene.aliases)
    set_actual_xrefs = {xref.root for xref in normalized_gene.xrefs}
    set_test_xrefs = {xref.root for xref in test_gene.xrefs}
    assert set_actual_xrefs == set_test_xrefs
    assert normalized_gene.symbol_status == test_gene.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(test_gene.previous_symbols)
    set_actual_aw = {aw.root for aw in normalized_gene.associated_with}
    set_test_aw = {aw.root for aw in test_gene.associated_with}
    assert set_actual_aw == set_test_aw
    assert normalized_gene.symbol == test_gene.symbol
    assert len(normalized_gene.locations) == len(test_gene.locations)
    for loc in normalized_gene.locations:
        assert loc in test_gene.locations
    assert set(normalized_gene.location_annotations) == \
           set(test_gene.location_annotations)
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
