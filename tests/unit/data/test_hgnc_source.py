"""Test that the therapy normalizer works as intended for the HGNC source."""
import pytest
from gene.schemas import Gene, MatchType
from gene import query


@pytest.fixture(scope='module')
def hgnc():
    """Build hgnc test fixture."""
    class QueryGetter:
        def normalize(self, query_str, incl='hgnc'):
            resp = query.normalize(query_str, keyed=True, incl=incl)
            return resp['source_matches']['HGNC']

    h = QueryGetter()
    return h


@pytest.fixture(scope='module')
def hgnc37133():
    """Create an A1BG antisense RNA 1 gene fixture."""
    params = {
        'label': 'A1BG antisense RNA 1',
        'concept_id': 'hgnc:37133',
        'approved_symbol': 'A1BG-AS1',
        'previous_symbols': [
            'NCRNA00181',
            'A1BGAS',
            'A1BG-AS'
        ],
        'aliases': ['FLJ23569'],
        'approval_status': 'approved',
        'other_identifiers': [
            'vega:OTTHUMG00000183508',
            'ensembl:ENSG00000268895',
            'ucsc:uc002qse.3',
        ],
        'trade_names': []
    }
    return Gene(**params)


def test_concept_id_hgnc37133(hgnc37133, hgnc):
    """Test that hgnc37133 drug normalizes to correct drug concept
    as a CONCEPT_ID match.
    """
    normalizer_response = hgnc.normalize('hgnc:37133')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol

    normalizer_response = hgnc.normalize('HGNC:37133')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol

    normalizer_response = hgnc.normalize('Hgnc:37133')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol


def test_hgnc37133_symbol(hgnc37133, hgnc):
    """Test that hgnc37133 drug normalizes to correct drug concept
    as an APPROVED_SYMBOL match.
    """
    normalizer_response = hgnc.normalize('A1BG-AS1')
    assert normalizer_response['match_type'] == MatchType.APPROVED_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol

    normalizer_response = hgnc.normalize('A1BG-as1')
    assert normalizer_response['match_type'] == MatchType.APPROVED_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol


def test_hgnc37133_label(hgnc37133, hgnc):
    """Test that hgnc37133 drug normalizes to correct drug concept
    as a PRIMARY_LABEL match.
    """
    normalizer_response = hgnc.normalize('A1BG antisense RNA 1')
    assert normalizer_response['match_type'] == MatchType.PRIMARY_LABEL
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol

    normalizer_response = hgnc.normalize('A1bg antisense RNA 1')
    assert normalizer_response['match_type'] ==\
           MatchType.PRIMARY_LABEL
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol


def test_hgnc37133_prev_symbol(hgnc37133, hgnc):
    """Test that hgnc37133 drug normalizes to correct drug concept
    as an PREVIOUS_SYMBOL match.
    """
    normalizer_response = hgnc.normalize('NCRNA00181')
    assert normalizer_response['match_type'] == MatchType.PREVIOUS_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol

    normalizer_response = hgnc.normalize('A1BGAS')
    assert normalizer_response['match_type'] == MatchType.PREVIOUS_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol

    normalizer_response = hgnc.normalize('A1BG-AS')
    assert normalizer_response['match_type'] == MatchType.PREVIOUS_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol


def test_hgnc37133_alias(hgnc37133, hgnc):
    """Test that alias term normalizes to correct drug concept as an
    ALIAS match.
    """
    normalizer_response = hgnc.normalize('FLJ23569')
    assert normalizer_response['match_type'] == MatchType.ALIAS
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol

    normalizer_response = hgnc.normalize('flj23569')
    assert normalizer_response['match_type'] == MatchType.ALIAS
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == hgnc37133.label
    assert normalized_drug.concept_id == hgnc37133.concept_id
    assert set(normalized_drug.aliases) == set(hgnc37133.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(hgnc37133.other_identifiers)
    assert set(normalized_drug.trade_names) == set(hgnc37133.trade_names)
    assert normalized_drug.approval_status == hgnc37133.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(hgnc37133.previous_symbols)
    assert normalized_drug.approved_symbol == hgnc37133.approved_symbol


def test_no_match(hgnc):
    """Test that a term normalizes to correct drug concept as a NO match."""
    normalizer_response = hgnc.normalize('A1BG - AS1')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0

    normalizer_response = hgnc.normalize('hnc:5')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH

    # Test empty query
    normalizer_response = hgnc.normalize('')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0


def test_meta_info(hgnc37133, hgnc):
    """Test that the meta field is correct."""
    normalizer_response = hgnc.normalize('HGNC:37133')
    # assert normalizer_response['meta_'].data_license == ''
    # assert normalizer_response['meta_'].data_license_url == ''
    assert normalizer_response['meta_'].version == '20201130'
    assert normalizer_response['meta_'].data_url == \
           'http://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/'
