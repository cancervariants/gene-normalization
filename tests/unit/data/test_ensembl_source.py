"""Test that the gene normalizer works as intended for the Ensembl source."""
import pytest
from gene.schemas import Gene, MatchType
from gene.query import Normalizer


@pytest.fixture(scope='module')
def ensembl():
    """Build ensembl test fixture."""
    class QueryGetter:
        def __init__(self):
            self.normalizer = Normalizer()

        def normalize(self, query_str, incl='ensembl'):
            resp = self.normalizer.normalize(query_str, keyed=True, incl=incl)
            return resp['source_matches']['Ensembl']

    e = QueryGetter()
    return e


@pytest.fixture(scope='module')
def ddx11l1():
    """Create a DDX11L1 fixutre."""
    params = {
        'concept_id': 'ensembl:ENSG00000223972',
        'symbol': 'DDX11L1',
        'label': None,
        'previous_symbols': [],
        'aliases': [],
        'other_identifiers': [],
        'approval_status': None,
        'start': '11869',
        'stop': '14409',
        'strand': '+'
    }
    return Gene(**params)


def test_concept_id_ddx11l1(ddx11l1, ensembl):
    """Test that ddx11l1 drug normalizes to correct drug concept
    as a CONCEPT_ID match.
    """
    normalizer_response = ensembl.normalize('ENSG00000223972')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == ddx11l1.label
    assert normalized_drug.concept_id == ddx11l1.concept_id
    assert set(normalized_drug.aliases) == set(ddx11l1.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_drug.approval_status == ddx11l1.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert normalized_drug.symbol == ddx11l1.symbol

    normalizer_response = ensembl.normalize('ENSG00000223972')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == ddx11l1.label
    assert normalized_drug.concept_id == ddx11l1.concept_id
    assert set(normalized_drug.aliases) == set(ddx11l1.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_drug.approval_status == ddx11l1.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert normalized_drug.symbol == ddx11l1.symbol

    normalizer_response = ensembl.normalize('ENSG00000223972')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == ddx11l1.label
    assert normalized_drug.concept_id == ddx11l1.concept_id
    assert set(normalized_drug.aliases) == set(ddx11l1.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_drug.approval_status == ddx11l1.approval_status
    assert set(normalized_drug.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert normalized_drug.symbol == ddx11l1.symbol


def test_no_match(ensembl):
    """Test that a term normalizes to correct drug concept as a NO match."""
    normalizer_response = ensembl.normalize('A1BG - AS1')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0

    normalizer_response = ensembl.normalize('hnc:5')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH

    # Test empty query
    normalizer_response = ensembl.normalize('')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0

    # Do not search on label
    normalizer_response = ensembl.normalize('A1BG antisense RNA 1')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0


def test_meta_info(ddx11l1, ensembl):
    """Test that the meta field is correct."""
    normalizer_response = ensembl.normalize('chromosome:1')
    # assert normalizer_response['meta_'].data_license == ''
    # assert normalizer_response['meta_'].data_license_url == ''
    assert normalizer_response['meta_'].version == '102'
    assert normalizer_response['meta_'].data_url == \
           'http://ftp.ensembl.org/pub/'
