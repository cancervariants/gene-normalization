"""Test import of NCBI source data"""
import pytest
from gene.schemas import Gene
from gene.query import Normalizer
from datetime import datetime


@pytest.fixture(scope='module')
def ncbi():
    """Build ncbi test fixture."""
    class QueryGetter:
        def __init__(self):
            self.normalizer = Normalizer()

        def normalize(self, query_str, incl='ncbi'):
            resp = self.normalizer.normalize(query_str, keyed=True, incl=incl)
            return resp['source_matches']['NCBI']

    n = QueryGetter()
    return n


@pytest.fixture(scope='module')
def dpf1():
    """Create gene fixture for DPF1."""
    params = {
        'label': 'double PHD fingers 1',
        'concept_id': 'ncbigene:8193',
        'symbol': 'DPF1',
        'aliases': ['BAF45b', 'NEUD4', 'neuro-d4'],
        'other_identifiers': ['hgnc:20225', 'ensembl:ENSG00000011332'],
        'previous_symbols': [],
        'xrefs': ['omim:601670'],
        'symbol_status': None,
        'seqid': '19',
        'location': '19q13.2'
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def pdp1():
    """Create gene fixture for PDP1."""
    params = {
        'label': 'pyruvate dehyrogenase phosphatase catalytic subunit 1',
        'concept_id': 'ncbigene:54704',
        'symbol': 'PDP1',
        'aliases': ['PDH', 'PDP', 'PDPC', 'PPM2A', 'PPM2C'],
        'other_identifiers': ['hgnc:9279', 'ensembl:ENSG00000164951'],
        'previous_symbols': ['LOC157663', 'PPM2C'],
        'xrefs': ['omim:605993'],
        'symbol_status': None,
        'seqid': '8',
        'location': '8q22.1'
    }
    return Gene(**params)


def test_concept_id(ncbi, dpf1, pdp1):
    """Test query normalizing on gene concept ID."""
    response = ncbi.normalize('ncbigene:8193')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.seqid == dpf1.seqid
    assert record.start == dpf1.start
    assert record.stop == dpf1.stop
    assert record.strand == dpf1.strand
    assert record.location == dpf1.location

    response = ncbi.normalize('ncbigene:54704')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == pdp1.label
    assert record.concept_id == pdp1.concept_id
    assert record.symbol == pdp1.symbol
    assert len(record.aliases) == len(pdp1.aliases)
    assert set(record.aliases) == set(pdp1.aliases)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.seqid == pdp1.seqid
    assert record.start == pdp1.start
    assert record.stop == pdp1.stop
    assert record.strand == pdp1.strand
    assert record.location == pdp1.location

    response = ncbi.normalize('NCBIGENE:54704')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == pdp1.label
    assert record.concept_id == pdp1.concept_id
    assert record.symbol == pdp1.symbol
    assert len(record.aliases) == len(pdp1.aliases)
    assert set(record.aliases) == set(pdp1.aliases)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.seqid == pdp1.seqid
    assert record.start == pdp1.start
    assert record.stop == pdp1.stop
    assert record.strand == pdp1.strand
    assert record.location == pdp1.location

    response = ncbi.normalize('ncbIgene:8193')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.seqid == dpf1.seqid
    assert record.start == dpf1.start
    assert record.stop == dpf1.stop
    assert record.strand == dpf1.strand
    assert record.location == dpf1.location

    response = ncbi.normalize('ncblgene:8193')
    assert response['match_type'] == 0

    response = ncbi.normalize('NCBIGENE54704')
    assert response['match_type'] == 0

    response = ncbi.normalize('54704')
    assert response['match_type'] == 0

    response = ncbi.normalize('ncbigene;54704')
    assert response['match_type'] == 0


def test_symbol(ncbi, dpf1, pdp1):
    """Test query normalizing on gene symbol."""
    response = ncbi.normalize('DPF1')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.seqid == dpf1.seqid
    assert record.start == dpf1.start
    assert record.stop == dpf1.stop
    assert record.strand == dpf1.strand
    assert record.location == dpf1.location

    response = ncbi.normalize('PDP1')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == pdp1.label
    assert record.concept_id == pdp1.concept_id
    assert record.symbol == pdp1.symbol
    assert set(record.aliases) == set(pdp1.aliases)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.seqid == pdp1.seqid
    assert record.start == pdp1.start
    assert record.stop == pdp1.stop
    assert record.strand == pdp1.strand
    assert record.location == pdp1.location

    response = ncbi.normalize('pdp1')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == pdp1.label
    assert record.concept_id == pdp1.concept_id
    assert record.symbol == pdp1.symbol
    assert set(record.aliases) == set(pdp1.aliases)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.seqid == pdp1.seqid
    assert record.start == pdp1.start
    assert record.stop == pdp1.stop
    assert record.strand == pdp1.strand
    assert record.location == pdp1.location

    response = ncbi.normalize('DpF1')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.seqid == dpf1.seqid
    assert record.start == dpf1.start
    assert record.stop == dpf1.stop
    assert record.strand == dpf1.strand
    assert record.location == dpf1.location

    response = ncbi.normalize('DPF 1')
    assert response['match_type'] == 0

    response = ncbi.normalize('DPG1')
    assert response['match_type'] == 0

    response = ncbi.normalize(
        'pyruvate dehyrogenase phosphatase catalytic subunit 1'
    )
    assert response['match_type'] != 100

    response = ncbi.normalize('PDP')
    assert response['match_type'] != 100


def test_prev_symbol(ncbi, pdp1):
    """Test that query term normalizes for gene aliases."""
    response = ncbi.normalize('LOC157663')
    assert response['match_type'] == 80
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == pdp1.label
    assert record.concept_id == pdp1.concept_id
    assert record.symbol == pdp1.symbol
    assert set(record.aliases) == set(pdp1.aliases)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.seqid == pdp1.seqid
    assert record.start == pdp1.start
    assert record.stop == pdp1.stop
    assert record.strand == pdp1.strand
    assert record.location == pdp1.location

    response2 = ncbi.normalize('PPM2C')
    assert response == response2
    response3 = ncbi.normalize('loc157663')
    assert response == response3


def test_alias(ncbi, dpf1, pdp1):
    """Test that query term normalizes for gene aliases."""
    response = ncbi.normalize('BAF45b')
    assert response['match_type'] == 60
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.seqid == dpf1.seqid
    assert record.start == dpf1.start
    assert record.stop == dpf1.stop
    assert record.strand == dpf1.strand
    assert record.location == dpf1.location

    # check that different aliases return equivalent object
    response2 = ncbi.normalize('NEUD4')
    assert response == response2
    response2 = ncbi.normalize('neuro-d4')
    assert response == response2

    response = ncbi.normalize('PDH')
    assert response['match_type'] == 60
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == pdp1.label
    assert record.concept_id == pdp1.concept_id
    assert record.symbol == pdp1.symbol
    assert set(record.aliases) == set(pdp1.aliases)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.seqid == pdp1.seqid
    assert record.start == pdp1.start
    assert record.stop == pdp1.stop
    assert record.strand == pdp1.strand
    assert record.location == pdp1.location

    # check that different aliases return equivalent object
    response2 = ncbi.normalize('PDP')
    assert response == response2
    response2 = ncbi.normalize('PDPC')
    assert response == response2
    response2 = ncbi.normalize('PPM2A')
    assert response == response2
    response2 = ncbi.normalize('PPM2C')
    assert response2['match_type'] == 80  # should match as prev_symbol

    # check correct case handling
    response = ncbi.normalize('pdh')
    assert response['match_type'] == 60
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == pdp1.label
    assert record.concept_id == pdp1.concept_id
    assert record.symbol == pdp1.symbol
    assert set(record.aliases) == set(pdp1.aliases)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.seqid == pdp1.seqid
    assert record.start == pdp1.start
    assert record.stop == pdp1.stop
    assert record.strand == pdp1.strand
    assert record.location == pdp1.location

    response = ncbi.normalize('BAF45B')
    assert response['match_type'] == 60
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.seqid == dpf1.seqid
    assert record.start == dpf1.start
    assert record.stop == dpf1.stop
    assert record.strand == dpf1.strand
    assert record.location == dpf1.location


def test_no_match(ncbi):
    """Test that nonexistent query doesn't normalize to a match."""
    response = ncbi.normalize('cisplatin')
    assert response['match_type'] == 0
    assert len(response['records']) == 0
    # double-check that meta still populates
    assert response['meta_'].data_license == 'custom'
    assert response['meta_'].data_license_url == \
           'https://www.ncbi.nlm.nih.gov/home/about/policies/'
    assert datetime.strptime(response['meta_'].version, "%Y%m%d")
    assert response['meta_'].data_url == \
        'https://ftp.ncbi.nlm.nih.gov/gene/DATA/'
    assert response['meta_'].rdp_url == \
        'https://reusabledata.org/ncbi-gene.html'
    assert not response['meta_'].non_commercial
    assert not response['meta_'].share_alike
    assert not response['meta_'].attribution

    # check blank
    response = ncbi.normalize('')
    assert response['match_type'] == 0

    # check some strange characters
    response = ncbi.normalize('----')
    assert response['match_type'] == 0

    response = ncbi.normalize('""')
    assert response['match_type'] == 0

    response = ncbi.normalize('~~~')
    assert response['match_type'] == 0

    response = ncbi.normalize(' ')
    assert response['match_type'] == 0


def test_meta(ncbi, pdp1):
    """Test NCBI source metadata."""
    response = ncbi.normalize('PDP1')
    assert response['meta_'].data_license == 'custom'
    assert response['meta_'].data_license_url == \
        'https://www.ncbi.nlm.nih.gov/home/about/policies/'
    assert datetime.strptime(response['meta_'].version, "%Y%m%d")
    assert response['meta_'].data_url == \
        'https://ftp.ncbi.nlm.nih.gov/gene/DATA/'
    assert response['meta_'].rdp_url == \
        'https://reusabledata.org/ncbi-gene.html'
    assert not response['meta_'].non_commercial
    assert not response['meta_'].share_alike
    assert not response['meta_'].attribution
    assert not response['meta_'].assembly
