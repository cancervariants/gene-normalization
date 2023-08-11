"""Provide utilities for test cases."""
import pytest

from gene.database import AbstractDatabase, create_db
from gene.schemas import SymbolStatus


@pytest.fixture(scope="session")
def database() -> AbstractDatabase:
    """Create database instance."""
    return create_db()


def assertion_checks(normalized_gene, test_gene, match_type):
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
        assert loc in test_gene.locations
    assert set(normalized_gene.location_annotations) == set(
        test_gene.location_annotations
    )
    assert normalized_gene.strand == test_gene.strand
    assert normalized_gene.gene_type == test_gene.gene_type


def check_resp_single_record(resp, test_gene, match_type):
    """Check that responses with single response return expected result"""
    assert len(resp.records) == 1
    assertion_checks(resp.records[0], test_gene, match_type)


def check_ncbi_discontinued_gene(normalizer_response, concept_id, symbol, match_type):
    """Check that searches on NCBI discontinued genes are correct."""
    assert len(normalizer_response.records) == 1
    resp = normalizer_response.records[0]
    assert resp.match_type == match_type
    assert resp.concept_id == concept_id
    assert resp.symbol == symbol
    assert resp.symbol_status == SymbolStatus.DISCONTINUED
    assert resp.label is None
    assert resp.strand is None
    assert resp.location_annotations == []
    assert resp.locations == []
    assert resp.aliases == []
    assert resp.previous_symbols == []
    assert resp.xrefs == []
    assert resp.associated_with == []
