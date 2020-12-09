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
        'symbol_status': None,
        'seqid': '1',
        'start': '11869',
        'stop': '14409',
        'strand': '+',
        'location': None
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def tp53():
    """Create a TP53 fixutre."""
    params = {
        'concept_id': 'ensembl:ENSG00000141510',
        'symbol': 'TP53',
        'label': None,
        'previous_symbols': [],
        'aliases': [],
        'other_identifiers': [],
        'symbol_status': None,
        'seqid': '17',
        'start': '7661779',
        'stop': '7687538',
        'strand': '-',
        'location': None
    }
    return Gene(**params)


def test_concept_id_ddx11l1(ddx11l1, ensembl):
    """Test that ddx11l1 drug normalizes to correct drug concept
    as a CONCEPT_ID match.
    """
    normalizer_response = ensembl.normalize('ensembl:ENSG00000223972')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == ddx11l1.label
    assert normalized_drug.concept_id == ddx11l1.concept_id
    assert set(normalized_drug.aliases) == set(ddx11l1.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_drug.symbol_status == ddx11l1.symbol_status
    assert set(normalized_drug.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert normalized_drug.symbol == ddx11l1.symbol
    assert normalized_drug.start == ddx11l1.start
    assert normalized_drug.stop == ddx11l1.stop
    assert normalized_drug.strand == ddx11l1.strand
    assert normalized_drug.seqid == ddx11l1.seqid
    assert normalized_drug.location == ddx11l1.location

    normalizer_response = ensembl.normalize('ENSG00000223972')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == ddx11l1.label
    assert normalized_drug.concept_id == ddx11l1.concept_id
    assert set(normalized_drug.aliases) == set(ddx11l1.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_drug.symbol_status == ddx11l1.symbol_status
    assert set(normalized_drug.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert normalized_drug.symbol == ddx11l1.symbol
    assert normalized_drug.start == ddx11l1.start
    assert normalized_drug.stop == ddx11l1.stop
    assert normalized_drug.strand == ddx11l1.strand
    assert normalized_drug.seqid == ddx11l1.seqid
    assert normalized_drug.location == ddx11l1.location

    normalizer_response = ensembl.normalize('ENSEMBL:ENSG00000223972')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == ddx11l1.label
    assert normalized_drug.concept_id == ddx11l1.concept_id
    assert set(normalized_drug.aliases) == set(ddx11l1.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_drug.symbol_status == ddx11l1.symbol_status
    assert set(normalized_drug.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert normalized_drug.symbol == ddx11l1.symbol
    assert normalized_drug.start == ddx11l1.start
    assert normalized_drug.stop == ddx11l1.stop
    assert normalized_drug.strand == ddx11l1.strand
    assert normalized_drug.seqid == ddx11l1.seqid
    assert normalized_drug.location == ddx11l1.location


def test_ddx11l1_symbol(ddx11l1, ensembl):
    """Test that ddx11l1 drug normalizes to correct drug concept
    as an symbol match.
    """
    normalizer_response = ensembl.normalize('ddx11l1')
    assert normalizer_response['match_type'] == MatchType.APPROVED_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == ddx11l1.label
    assert normalized_drug.concept_id == ddx11l1.concept_id
    assert set(normalized_drug.aliases) == set(ddx11l1.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_drug.symbol_status == ddx11l1.symbol_status
    assert set(normalized_drug.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert normalized_drug.symbol == ddx11l1.symbol
    assert normalized_drug.start == ddx11l1.start
    assert normalized_drug.stop == ddx11l1.stop
    assert normalized_drug.strand == ddx11l1.strand
    assert normalized_drug.seqid == ddx11l1.seqid
    assert normalized_drug.location == ddx11l1.location

    normalizer_response = ensembl.normalize('DDX11L1')
    assert normalizer_response['match_type'] == MatchType.APPROVED_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == ddx11l1.label
    assert normalized_drug.concept_id == ddx11l1.concept_id
    assert set(normalized_drug.aliases) == set(ddx11l1.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_drug.symbol_status == ddx11l1.symbol_status
    assert set(normalized_drug.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert normalized_drug.symbol == ddx11l1.symbol
    assert normalized_drug.start == ddx11l1.start
    assert normalized_drug.stop == ddx11l1.stop
    assert normalized_drug.strand == ddx11l1.strand
    assert normalized_drug.seqid == ddx11l1.seqid
    assert normalized_drug.location == ddx11l1.location


def test_concept_id_tp53(tp53, ensembl):
    """Test that tp53 drug normalizes to correct drug concept
    as a CONCEPT_ID match.
    """
    normalizer_response = ensembl.normalize('ENSG00000141510')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == tp53.label
    assert normalized_drug.concept_id == tp53.concept_id
    assert set(normalized_drug.aliases) == set(tp53.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_drug.symbol_status == tp53.symbol_status
    assert set(normalized_drug.previous_symbols) == \
           set(tp53.previous_symbols)
    assert normalized_drug.symbol == tp53.symbol
    assert normalized_drug.start == tp53.start
    assert normalized_drug.stop == tp53.stop
    assert normalized_drug.strand == tp53.strand
    assert normalized_drug.seqid == tp53.seqid
    assert normalized_drug.location == tp53.location

    normalizer_response = ensembl.normalize('ensembl:ENSG00000141510')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == tp53.label
    assert normalized_drug.concept_id == tp53.concept_id
    assert set(normalized_drug.aliases) == set(tp53.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_drug.symbol_status == tp53.symbol_status
    assert set(normalized_drug.previous_symbols) == \
           set(tp53.previous_symbols)
    assert normalized_drug.symbol == tp53.symbol
    assert normalized_drug.start == tp53.start
    assert normalized_drug.stop == tp53.stop
    assert normalized_drug.strand == tp53.strand
    assert normalized_drug.seqid == tp53.seqid
    assert normalized_drug.location == tp53.location

    normalizer_response = ensembl.normalize('ENSEMBL:ENSG00000141510')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == tp53.label
    assert normalized_drug.concept_id == tp53.concept_id
    assert set(normalized_drug.aliases) == set(tp53.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_drug.symbol_status == tp53.symbol_status
    assert set(normalized_drug.previous_symbols) == \
           set(tp53.previous_symbols)
    assert normalized_drug.symbol == tp53.symbol
    assert normalized_drug.start == tp53.start
    assert normalized_drug.stop == tp53.stop
    assert normalized_drug.strand == tp53.strand
    assert normalized_drug.seqid == tp53.seqid
    assert normalized_drug.location == tp53.location


def test_tp53_symbol(tp53, ensembl):
    """Test that tp53 drug normalizes to correct drug concept
    as an symbol match.
    """
    normalizer_response = ensembl.normalize('tp53')
    assert normalizer_response['match_type'] == MatchType.APPROVED_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == tp53.label
    assert normalized_drug.concept_id == tp53.concept_id
    assert set(normalized_drug.aliases) == set(tp53.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_drug.symbol_status == tp53.symbol_status
    assert set(normalized_drug.previous_symbols) == \
           set(tp53.previous_symbols)
    assert normalized_drug.symbol == tp53.symbol
    assert normalized_drug.start == tp53.start
    assert normalized_drug.stop == tp53.stop
    assert normalized_drug.strand == tp53.strand
    assert normalized_drug.seqid == tp53.seqid
    assert normalized_drug.location == tp53.location

    normalizer_response = ensembl.normalize('tp53')
    assert normalizer_response['match_type'] == MatchType.APPROVED_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_drug = normalizer_response['records'][0]
    assert normalized_drug.label == tp53.label
    assert normalized_drug.concept_id == tp53.concept_id
    assert set(normalized_drug.aliases) == set(tp53.aliases)
    assert set(normalized_drug.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_drug.symbol_status == tp53.symbol_status
    assert set(normalized_drug.previous_symbols) == \
           set(tp53.previous_symbols)
    assert normalized_drug.symbol == tp53.symbol
    assert normalized_drug.start == tp53.start
    assert normalized_drug.stop == tp53.stop
    assert normalized_drug.strand == tp53.strand
    assert normalized_drug.seqid == tp53.seqid
    assert normalized_drug.location == tp53.location


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
    assert normalizer_response['meta_'].assembly == 'GRCh38'
