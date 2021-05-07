"""Provide utilities for test cases."""


def assertion_checks(normalizer_response, test_gene, n_records, match_type):
    """Check that normalizer_response and test_gene are the same."""
    assert normalizer_response['match_type'] == match_type
    assert len(normalizer_response['records']) == n_records
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == test_gene.label
    assert normalized_gene.concept_id == test_gene.concept_id
    assert set(normalized_gene.aliases) == set(test_gene.aliases)
    assert set(normalized_gene.xrefs) == \
           set(test_gene.xrefs)
    assert normalized_gene.symbol_status == test_gene.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(test_gene.previous_symbols)
    assert set(normalized_gene.associated_with) == \
           set(test_gene.associated_with)
    assert normalized_gene.symbol == test_gene.symbol
    assert normalized_gene.locations == test_gene.locations
    assert set(normalized_gene.location_annotations) == \
           set(test_gene.location_annotations)
    assert normalized_gene.strand == test_gene.strand
