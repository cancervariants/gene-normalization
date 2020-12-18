"""Test that the gene normalizer works as intended for the HGNC source."""
import pytest
from gene.schemas import Gene, MatchType
from gene.query import Normalizer
from datetime import datetime


@pytest.fixture(scope='module')
def hgnc():
    """Build hgnc test fixture."""
    class QueryGetter:
        def __init__(self):
            self.normalizer = Normalizer()

        def normalize(self, query_str, incl='hgnc'):
            resp = self.normalizer.normalize(query_str, keyed=True, incl=incl)
            return resp['source_matches']['HGNC']

    h = QueryGetter()
    return h


@pytest.fixture(scope='module')
def a1bg_as1():
    """Create an A1BG-AS1 gene fixture."""
    params = {
        'label': 'A1BG antisense RNA 1',
        'concept_id': 'hgnc:37133',
        'symbol': 'A1BG-AS1',
        'location': '19q13.43',
        'previous_symbols': [
            'NCRNA00181',
            'A1BGAS',
            'A1BG-AS'
        ],
        'aliases': ['FLJ23569'],
        'symbol_status': 'approved',
        'xrefs': [
            'vega:OTTHUMG00000183508',
            'ucsc:uc002qse.3',
            'refseq:NR_015380',
            'ena.embl:BC040926',
            'refseq:NR_015380',
            'ena.embl:BC040926'
        ],
        'other_identifiers': [
            'ensembl:ENSG00000268895',
            'ncbigene:503538'
        ]
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def tp53():
    """Create an TP53 gene fixture."""
    params = {
        'label': 'tumor protein p53',
        'concept_id': 'hgnc:11998',
        'symbol': 'TP53',
        'location': '17p13.1',
        'previous_symbols': [],
        'aliases': [
            'p53',
            'LFS1'
        ],
        'symbol_status': 'approved',
        'xrefs': [
            'vega:OTTHUMG00000162125',
            'refseq:NM_000546',
            'cosmic:TP53',
            'omim:191170',
            'ucsc:uc060aur.1',
            'uniprot:P04637',
            'orphanet:120204',
            'ccds:CCDS73968',
            'ccds:CCDS73971',
            'ccds:CCDS73970',
            'ccds:CCDS73969',
            'ccds:CCDS73967',
            'ccds:CCDS73966',
            'ccds:CCDS73965',
            'ccds:CCDS73964',
            'ccds:CCDS73963',
            'ccds:CCDS11118',
            'ccds:CCDS45605',
            'ccds:CCDS45606',
            'ena.embl:AF307851',
            'pubmed:6396087',
            'pubmed:3456488',
            'pubmed:2047879'
        ],
        'other_identifiers': [
            'ensembl:ENSG00000141510',
            'ncbigene:7157'
        ]
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def a3galt2():
    """Create an A3GALT2 gene fixture."""
    params = {
        'label': 'alpha 1,3-galactosyltransferase 2',
        'concept_id': 'hgnc:30005',
        'symbol': 'A3GALT2',
        'location': '1p35.1',
        'previous_symbols': [
            'A3GALT2P'
        ],
        'aliases': [
            'IGBS3S',
            'IGB3S'
        ],
        'symbol_status': 'approved',
        'other_identifiers': [
            'ensembl:ENSG00000184389',
            'ncbigene:127550'
        ],
        'xrefs': [
            'vega:OTTHUMG00000004125',
            'vega:OTTHUMG00000004125',
            'ucsc:uc031plq.1',
            'uniprot:U3KPV4',
            'ccds:CCDS60080',
            'pubmed:10854427',
            'pubmed:18630988',
            'refseq:NM_001080438'
        ]
    }
    return Gene(**params)


def test_concept_id_a1bg_as1(a1bg_as1, hgnc):
    """Test that a1bg_as1 gene normalizes to correct gene concept
    as a CONCEPT_ID match.
    """
    normalizer_response = hgnc.normalize('hgnc:37133')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a1bg_as1.label
    assert normalized_gene.concept_id == a1bg_as1.concept_id
    assert set(normalized_gene.aliases) == set(a1bg_as1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a1bg_as1.other_identifiers)
    assert normalized_gene.symbol_status == a1bg_as1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a1bg_as1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a1bg_as1.xrefs)
    assert normalized_gene.symbol == a1bg_as1.symbol
    assert normalized_gene.location == a1bg_as1.location

    normalizer_response = hgnc.normalize('HGNC:37133')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a1bg_as1.label
    assert normalized_gene.concept_id == a1bg_as1.concept_id
    assert set(normalized_gene.aliases) == set(a1bg_as1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a1bg_as1.other_identifiers)
    assert normalized_gene.symbol_status == a1bg_as1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a1bg_as1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a1bg_as1.xrefs)
    assert normalized_gene.symbol == a1bg_as1.symbol
    assert normalized_gene.location == a1bg_as1.location

    normalizer_response = hgnc.normalize('Hgnc:37133')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a1bg_as1.label
    assert normalized_gene.concept_id == a1bg_as1.concept_id
    assert set(normalized_gene.aliases) == set(a1bg_as1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a1bg_as1.other_identifiers)
    assert normalized_gene.symbol_status == a1bg_as1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a1bg_as1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a1bg_as1.xrefs)
    assert normalized_gene.symbol == a1bg_as1.symbol
    assert normalized_gene.location == a1bg_as1.location


def test_a1bg_as1_symbol(a1bg_as1, hgnc):
    """Test that a1bg_as1 gene normalizes to correct gene concept
    as an symbol match.
    """
    normalizer_response = hgnc.normalize('A1BG-AS1')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a1bg_as1.label
    assert normalized_gene.concept_id == a1bg_as1.concept_id
    assert set(normalized_gene.aliases) == set(a1bg_as1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a1bg_as1.other_identifiers)
    assert normalized_gene.symbol_status == a1bg_as1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a1bg_as1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a1bg_as1.xrefs)
    assert normalized_gene.symbol == a1bg_as1.symbol
    assert normalized_gene.location == a1bg_as1.location

    normalizer_response = hgnc.normalize('A1BG-as1')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a1bg_as1.label
    assert normalized_gene.concept_id == a1bg_as1.concept_id
    assert set(normalized_gene.aliases) == set(a1bg_as1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a1bg_as1.other_identifiers)
    assert normalized_gene.symbol_status == a1bg_as1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a1bg_as1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a1bg_as1.xrefs)
    assert normalized_gene.symbol == a1bg_as1.symbol
    assert normalized_gene.location == a1bg_as1.location


def test_a1bg_as1_prev_symbol(a1bg_as1, hgnc):
    """Test that a1bg_as1 gene normalizes to correct gene concept
    as an PREV_SYMBOL match.
    """
    normalizer_response = hgnc.normalize('NCRNA00181')
    assert normalizer_response['match_type'] == MatchType.PREV_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a1bg_as1.label
    assert normalized_gene.concept_id == a1bg_as1.concept_id
    assert set(normalized_gene.aliases) == set(a1bg_as1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a1bg_as1.other_identifiers)
    assert normalized_gene.symbol_status == a1bg_as1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a1bg_as1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a1bg_as1.xrefs)
    assert normalized_gene.symbol == a1bg_as1.symbol
    assert normalized_gene.location == a1bg_as1.location

    normalizer_response = hgnc.normalize('A1BGAS')
    assert normalizer_response['match_type'] == MatchType.PREV_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a1bg_as1.label
    assert normalized_gene.concept_id == a1bg_as1.concept_id
    assert set(normalized_gene.aliases) == set(a1bg_as1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a1bg_as1.other_identifiers)
    assert normalized_gene.symbol_status == a1bg_as1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a1bg_as1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a1bg_as1.xrefs)
    assert normalized_gene.symbol == a1bg_as1.symbol
    assert normalized_gene.location == a1bg_as1.location

    normalizer_response = hgnc.normalize('A1BG-AS')
    assert normalizer_response['match_type'] == MatchType.PREV_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a1bg_as1.label
    assert normalized_gene.concept_id == a1bg_as1.concept_id
    assert set(normalized_gene.aliases) == set(a1bg_as1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a1bg_as1.other_identifiers)
    assert normalized_gene.symbol_status == a1bg_as1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a1bg_as1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a1bg_as1.xrefs)
    assert normalized_gene.symbol == a1bg_as1.symbol
    assert normalized_gene.location == a1bg_as1.location


def test_a1bg_as1_alias(a1bg_as1, hgnc):
    """Test that alias term normalizes to correct gene concept as an
    ALIAS match.
    """
    normalizer_response = hgnc.normalize('FLJ23569')
    assert normalizer_response['match_type'] == MatchType.ALIAS
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a1bg_as1.label
    assert normalized_gene.concept_id == a1bg_as1.concept_id
    assert set(normalized_gene.aliases) == set(a1bg_as1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a1bg_as1.other_identifiers)
    assert normalized_gene.symbol_status == a1bg_as1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a1bg_as1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a1bg_as1.xrefs)
    assert normalized_gene.symbol == a1bg_as1.symbol
    assert normalized_gene.location == a1bg_as1.location

    normalizer_response = hgnc.normalize('flj23569')
    assert normalizer_response['match_type'] == MatchType.ALIAS
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a1bg_as1.label
    assert normalized_gene.concept_id == a1bg_as1.concept_id
    assert set(normalized_gene.aliases) == set(a1bg_as1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a1bg_as1.other_identifiers)
    assert normalized_gene.symbol_status == a1bg_as1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a1bg_as1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a1bg_as1.xrefs)
    assert normalized_gene.symbol == a1bg_as1.symbol
    assert normalized_gene.location == a1bg_as1.location


def test_concept_id_a3galt2(a3galt2, hgnc):
    """Test that a3galt2 gene normalizes to correct gene concept
    as a CONCEPT_ID match.
    """
    normalizer_response = hgnc.normalize('hgnc:30005')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a3galt2.label
    assert normalized_gene.concept_id == a3galt2.concept_id
    assert set(normalized_gene.aliases) == set(a3galt2.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a3galt2.other_identifiers)
    assert normalized_gene.symbol_status == a3galt2.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a3galt2.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a3galt2.xrefs)
    assert normalized_gene.symbol == a3galt2.symbol
    assert normalized_gene.location == a3galt2.location

    normalizer_response = hgnc.normalize('HGNC:30005')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a3galt2.label
    assert normalized_gene.concept_id == a3galt2.concept_id
    assert set(normalized_gene.aliases) == set(a3galt2.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a3galt2.other_identifiers)
    assert normalized_gene.symbol_status == a3galt2.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a3galt2.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a3galt2.xrefs)
    assert normalized_gene.symbol == a3galt2.symbol
    assert normalized_gene.location == a3galt2.location

    normalizer_response = hgnc.normalize('Hgnc:30005')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a3galt2.label
    assert normalized_gene.concept_id == a3galt2.concept_id
    assert set(normalized_gene.aliases) == set(a3galt2.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a3galt2.other_identifiers)
    assert normalized_gene.symbol_status == a3galt2.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a3galt2.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a3galt2.xrefs)
    assert normalized_gene.symbol == a3galt2.symbol
    assert normalized_gene.location == a3galt2.location


def test_a3galt2_symbol(a3galt2, hgnc):
    """Test that a3galt2 gene normalizes to correct gene concept
    as an symbol match.
    """
    normalizer_response = hgnc.normalize('A3GALT2')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a3galt2.label
    assert normalized_gene.concept_id == a3galt2.concept_id
    assert set(normalized_gene.aliases) == set(a3galt2.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a3galt2.other_identifiers)
    assert normalized_gene.symbol_status == a3galt2.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a3galt2.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a3galt2.xrefs)
    assert normalized_gene.symbol == a3galt2.symbol
    assert normalized_gene.location == a3galt2.location

    normalizer_response = hgnc.normalize('a3galt2')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a3galt2.label
    assert normalized_gene.concept_id == a3galt2.concept_id
    assert set(normalized_gene.aliases) == set(a3galt2.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a3galt2.other_identifiers)
    assert normalized_gene.symbol_status == a3galt2.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a3galt2.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a3galt2.xrefs)
    assert normalized_gene.symbol == a3galt2.symbol
    assert normalized_gene.location == a3galt2.location


def test_a3galt2_prev_symbol(a3galt2, hgnc):
    """Test that a3galt2 gene normalizes to correct gene concept
    as an PREV_SYMBOL match.
    """
    normalizer_response = hgnc.normalize('A3GALT2P')
    assert normalizer_response['match_type'] == MatchType.PREV_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a3galt2.label
    assert normalized_gene.concept_id == a3galt2.concept_id
    assert set(normalized_gene.aliases) == set(a3galt2.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a3galt2.other_identifiers)
    assert normalized_gene.symbol_status == a3galt2.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a3galt2.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a3galt2.xrefs)
    assert normalized_gene.symbol == a3galt2.symbol
    assert normalized_gene.location == a3galt2.location

    normalizer_response = hgnc.normalize('A3GALT2p')
    assert normalizer_response['match_type'] == MatchType.PREV_SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a3galt2.label
    assert normalized_gene.concept_id == a3galt2.concept_id
    assert set(normalized_gene.aliases) == set(a3galt2.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a3galt2.other_identifiers)
    assert normalized_gene.symbol_status == a3galt2.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a3galt2.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a3galt2.xrefs)
    assert normalized_gene.symbol == a3galt2.symbol
    assert normalized_gene.location == a3galt2.location


def test_a3galt2_alias(a3galt2, hgnc):
    """Test that alias term normalizes to correct gene concept as an
    ALIAS match.
    """
    normalizer_response = hgnc.normalize('IGBS3S')
    assert normalizer_response['match_type'] == MatchType.ALIAS
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a3galt2.label
    assert normalized_gene.concept_id == a3galt2.concept_id
    assert set(normalized_gene.aliases) == set(a3galt2.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a3galt2.other_identifiers)
    assert normalized_gene.symbol_status == a3galt2.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a3galt2.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a3galt2.xrefs)
    assert normalized_gene.symbol == a3galt2.symbol
    assert normalized_gene.location == a3galt2.location

    normalizer_response = hgnc.normalize('igB3s')
    assert normalizer_response['match_type'] == MatchType.ALIAS
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == a3galt2.label
    assert normalized_gene.concept_id == a3galt2.concept_id
    assert set(normalized_gene.aliases) == set(a3galt2.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(a3galt2.other_identifiers)
    assert normalized_gene.symbol_status == a3galt2.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(a3galt2.previous_symbols)
    assert set(normalized_gene.xrefs) == set(a3galt2.xrefs)
    assert normalized_gene.symbol == a3galt2.symbol
    assert normalized_gene.location == a3galt2.location


def test_concept_id_tp53(tp53, hgnc):
    """Test that tp53 gene normalizes to correct gene concept
    as a CONCEPT_ID match.
    """
    normalizer_response = hgnc.normalize('hgnc:11998')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == tp53.label
    assert normalized_gene.concept_id == tp53.concept_id
    assert set(normalized_gene.aliases) == set(tp53.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_gene.symbol_status == tp53.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(tp53.previous_symbols)
    assert set(normalized_gene.xrefs) == set(tp53.xrefs)
    assert normalized_gene.symbol == tp53.symbol
    assert normalized_gene.location == tp53.location

    normalizer_response = hgnc.normalize('HGNC:11998')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == tp53.label
    assert normalized_gene.concept_id == tp53.concept_id
    assert set(normalized_gene.aliases) == set(tp53.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_gene.symbol_status == tp53.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(tp53.previous_symbols)
    assert set(normalized_gene.xrefs) == set(tp53.xrefs)
    assert normalized_gene.symbol == tp53.symbol
    assert normalized_gene.location == tp53.location

    normalizer_response = hgnc.normalize('Hgnc:11998')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == tp53.label
    assert normalized_gene.concept_id == tp53.concept_id
    assert set(normalized_gene.aliases) == set(tp53.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_gene.symbol_status == tp53.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(tp53.previous_symbols)
    assert set(normalized_gene.xrefs) == set(tp53.xrefs)
    assert normalized_gene.symbol == tp53.symbol
    assert normalized_gene.location == tp53.location


def test_tp53_symbol(tp53, hgnc):
    """Test that tp53 gene normalizes to correct gene concept
    as an symbol match.
    """
    normalizer_response = hgnc.normalize('tp53')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == tp53.label
    assert normalized_gene.concept_id == tp53.concept_id
    assert set(normalized_gene.aliases) == set(tp53.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_gene.symbol_status == tp53.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(tp53.previous_symbols)
    assert set(normalized_gene.xrefs) == set(tp53.xrefs)
    assert normalized_gene.symbol == tp53.symbol
    assert normalized_gene.location == tp53.location

    normalizer_response = hgnc.normalize('TP53')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == tp53.label
    assert normalized_gene.concept_id == tp53.concept_id
    assert set(normalized_gene.aliases) == set(tp53.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_gene.symbol_status == tp53.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(tp53.previous_symbols)
    assert set(normalized_gene.xrefs) == set(tp53.xrefs)
    assert normalized_gene.symbol == tp53.symbol
    assert normalized_gene.location == tp53.location


def test_tp53_alias(tp53, hgnc):
    """Test that alias term normalizes to correct gene concept as an
    ALIAS match.
    """
    normalizer_response = hgnc.normalize('LFS1')
    assert normalizer_response['match_type'] == MatchType.ALIAS
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == tp53.label
    assert normalized_gene.concept_id == tp53.concept_id
    assert set(normalized_gene.aliases) == set(tp53.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_gene.symbol_status == tp53.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(tp53.previous_symbols)
    assert set(normalized_gene.xrefs) == set(tp53.xrefs)
    assert normalized_gene.symbol == tp53.symbol
    assert normalized_gene.location == tp53.location

    normalizer_response = hgnc.normalize('p53')
    assert normalizer_response['match_type'] == MatchType.ALIAS
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == tp53.label
    assert normalized_gene.concept_id == tp53.concept_id
    assert set(normalized_gene.aliases) == set(tp53.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(tp53.other_identifiers)
    assert normalized_gene.symbol_status == tp53.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(tp53.previous_symbols)
    assert set(normalized_gene.xrefs) == set(tp53.xrefs)
    assert normalized_gene.symbol == tp53.symbol
    assert normalized_gene.location == tp53.location


def test_no_match(hgnc):
    """Test that a term normalizes to correct gene concept as a NO match."""
    normalizer_response = hgnc.normalize('A1BG - AS1')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0

    normalizer_response = hgnc.normalize('hnc:5')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH

    # Test empty query
    normalizer_response = hgnc.normalize('')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0

    # Do not search on label
    normalizer_response = hgnc.normalize('A1BG antisense RNA 1')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0


def test_meta_info(a1bg_as1, hgnc):
    """Test that the meta field is correct."""
    normalizer_response = hgnc.normalize('HGNC:37133')
    assert normalizer_response['meta_'].data_license == 'custom'
    assert normalizer_response['meta_'].data_license_url == \
           'https://www.genenames.org/about/'
    assert datetime.strptime(normalizer_response['meta_'].version, "%Y%m%d")
    assert normalizer_response['meta_'].data_url == \
           'ftp://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/'
    assert normalizer_response['meta_'].rdp_url is None
    assert normalizer_response['meta_'].assembly is None
    assert normalizer_response['meta_'].non_commercial is False
    assert normalizer_response['meta_'].share_alike is False
    assert normalizer_response['meta_'].attribution is False
