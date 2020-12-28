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
        'location_annotations': None,
        'locations': [
            {
                'chr': '19',
                'interval': {
                    'end': 'q13.2',
                    'start': 'q13.2',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ]
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
        'location_annotations': None,
        'locations': [
            {
                'chr': '8',
                'interval': {
                    'end': 'q22.1',
                    'start': 'q22.1',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ]

    }
    return Gene(**params)


# X and Y chromosomes
@pytest.fixture(scope='module')
def spry3():
    """Create gene fixture for SPRY3."""
    params = {
        'label': 'sprouty RTK signaling antagonist 3',
        'concept_id': 'ncbigene:10251',
        'symbol': 'SPRY3',
        'aliases': ['spry-3'],
        'other_identifiers': ['hgnc:11271', 'ensembl:ENSG00000168939'],
        'previous_symbols': ['LOC170187', 'LOC253479'],
        'xrefs': ['omim:300531'],
        'symbol_status': None,
        'location_annotations': None,
        'locations': [
            {
                'chr': 'Y',
                'interval': {
                    'end': 'q12',
                    'start': 'q12',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            },
            {
                'chr': 'X',
                'interval': {
                    'end': 'q28',
                    'start': 'q28',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ]
    }
    return Gene(**params)


# chromosome but no map locations
@pytest.fixture(scope='module')
def adcp1():
    """Create gene fixture for ADCP1."""
    params = {
        'label': 'adenosine deaminase complexing protein 1',
        'concept_id': 'ncbigene:106',
        'symbol': 'ADCP1',
        'aliases': [],
        'other_identifiers': ['hgnc:229'],
        'previous_symbols': [],
        'xrefs': [],
        'symbol_status': None,
        'location_annotations': {
            'chr': ['6']
        },
        'locations': []
    }
    return Gene(**params)


# no chromosome or map locations
@pytest.fixture(scope='module')
def afa():
    """Create gene fixture for AFA."""
    params = {
        'label': 'ankyloblepharon filiforme adnatum',
        'concept_id': 'ncbigene:170',
        'symbol': 'AFA',
        'aliases': [],
        'other_identifiers': [],
        'previous_symbols': [],
        'xrefs': ['omim:106250'],
        'symbol_status': None,
        'location_annotations': None,
        'locations': []
    }
    return Gene(**params)


# Contains non cytogenic locations (i.e. "map from Rosati....")
@pytest.fixture(scope='module')
def znf84():
    """Create gene fixture for ZNF84."""
    params = {
        'label': 'zinc finger protein 84',
        'concept_id': 'ncbigene:7637',
        'symbol': 'ZNF84',
        'aliases': ['HPF2'],
        'other_identifiers': ['hgnc:13159', 'ensembl:ENSG00000198040'],
        'previous_symbols': ["LOC100287429"],
        'xrefs': ['omim:618554'],
        'symbol_status': None,
        'location_annotations': {
            'invalid_locations': ['map from Rosati ref via FISH [AFS]']
        },
        'locations': [
            {
                'chr': '12',
                'interval': {
                    'end': 'q24.33',
                    'start': 'q24.33',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ]
    }
    return Gene(**params)


# No arm or sub band
@pytest.fixture(scope='module')
def slc25a6():
    """Create gene fixture for SLC25A6."""
    params = {
        'label': 'solute carrier family 25 member 6',
        'concept_id': 'ncbigene:293',
        'symbol': 'SLC25A6',
        'aliases': ['AAC3', 'ANT', 'ANT 2', 'ANT 3', 'ANT3', 'ANT3Y'],
        'other_identifiers': ['hgnc:10992', 'ensembl:ENSG00000169100'],
        'previous_symbols': ["ANT3Y"],
        'xrefs': ['omim:300151', 'omim:403000'],
        'symbol_status': None,
        'location_annotations': {
            'chr': ['X', 'Y']
        },
        'locations': []
    }
    return Gene(**params)


# Contains arm but no sub band
@pytest.fixture(scope='module')
def loc106783576():
    """Create gene fixture for ."""
    params = {
        'label': 'nonconserved acetylation island sequence 68 enhancer',
        'concept_id': 'ncbigene:106783576',
        'symbol': 'LOC106783576',
        'aliases': [],
        'other_identifiers': [],
        'previous_symbols': [],
        'xrefs': [],
        'symbol_status': None,
        'location_annotations': None,
        'locations': [
            {
                'chr': '10',
                'interval': {
                    'end': 'p',
                    'start': 'p',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ]
    }
    return Gene(**params)


# Contain 3 different map locations on diff chromosomes --> locations = []
@pytest.fixture(scope='module')
def oms():
    """Create gene fixture for OMS."""
    params = {
        'label': 'otitis media, susceptibility to',
        'concept_id': 'ncbigene:619538',
        'symbol': 'OMS',
        'aliases': ['COME/ROM'],
        'other_identifiers': [],
        'previous_symbols': [],
        'xrefs': ['omim:166760'],
        'symbol_status': None,
        'location_annotations': None,
        'locations': []
    }
    return Gene(**params)


# Testing for cen
@pytest.fixture(scope='module')
def glc1b():
    """Create gene fixture for GLC1B."""
    params = {
        'label': 'glaucoma 1, open angle, B (adult-onset)',
        'concept_id': 'ncbigene:2722',
        'symbol': 'GLC1B',
        'aliases': [],
        'other_identifiers': [],
        'previous_symbols': [],
        'xrefs': ['omim:606689'],
        'symbol_status': None,
        'location_annotations': None,
        'locations': [
            {
                'chr': '2',
                'interval': {
                    'end': 'q13',
                    'start': 'cen',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ]
    }
    return Gene(**params)


# Testing for ter ranges
@pytest.fixture(scope='module')
def hdpa():
    """Create gene fixture for HDPA."""
    params = {
        'label': 'Hodgkin disease, susceptibility, pseudoautosomal',
        'concept_id': 'ncbigene:50829',
        'symbol': 'HDPA',
        'aliases': [],
        'other_identifiers': [],
        'previous_symbols': [],
        'xrefs': ['omim:300221'],
        'symbol_status': None,
        'location_annotations': None,
        'locations': [
            {
                'chr': 'X',
                'interval': {
                    'end': 'pter',
                    'start': 'p22.32',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ]
    }
    return Gene(**params)


# Testing for annotation
@pytest.fixture(scope='module')
def prkrap1():
    """Create gene fixture for PRKRAP1."""
    params = {
        'label': 'protein activator of interferon induced protein kinase '
                 'EIF2AK2 pseudogene 1',
        'concept_id': 'ncbigene:731716',
        'symbol': 'PRKRAP1',
        'aliases': [],
        'other_identifiers': ['hgnc:33447'],
        'previous_symbols': ['LOC100289695'],
        'xrefs': [],
        'symbol_status': None,
        'location_annotations': {
            'annotation': 'alternate reference locus'
        },
        'locations': [
            {
                'chr': '6',
                'interval': {
                    'end': 'p21.3',
                    'start': 'p21.3',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ]
    }
    return Gene(**params)


# start > end
@pytest.fixture(scope='module')
def mhb():
    """Create gene fixture for MHB."""
    params = {
        'label': 'myopathy, hyaline body, autosomal recessive',
        'concept_id': 'ncbigene:619511',
        'symbol': 'MHB',
        'aliases': [],
        'other_identifiers': [],
        'previous_symbols': [],
        'xrefs': ['omim:255160'],
        'symbol_status': None,
        'location_annotations': None,
        'locations': [
            {
                'chr': '3',
                'interval': {
                    'end': 'p22.2',
                    'start': 'p21.32',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ]
    }
    return Gene(**params)


# Different arms
@pytest.fixture(scope='module')
def spg37():
    """Create gene fixture for SPG37."""
    params = {
        'label': 'spastic paraplegia 37 (autosomal dominant)',
        'concept_id': 'ncbigene:100049159',
        'symbol': 'SPG37',
        'aliases': [],
        'other_identifiers': [],
        'previous_symbols': [],
        'xrefs': ['omim:611945'],
        'symbol_status': None,
        'location_annotations': None,
        'locations': [
            {
                'chr': '8',
                'interval': {
                    'end': 'q13.3',
                    'start': 'p21.2',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ]
    }
    return Gene(**params)


def test_concept_id(ncbi, dpf1, pdp1, spry3):
    """Test query normalizing on gene concept ID."""
    response = ncbi.normalize('ncbigene:8193')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert len(record.aliases) == len(dpf1.aliases)
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.previous_symbols) == set(dpf1.previous_symbols)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.strand == dpf1.strand
    assert record.locations == dpf1.locations
    assert record.location_annotations == dpf1.location_annotations

    response = ncbi.normalize('ncbigene:54704')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == pdp1.label
    assert record.concept_id == pdp1.concept_id
    assert record.symbol == pdp1.symbol
    assert len(record.aliases) == len(pdp1.aliases)
    assert set(record.aliases) == set(pdp1.aliases)
    assert set(record.previous_symbols) == set(pdp1.previous_symbols)
    assert set(record.xrefs) == set(pdp1.xrefs)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.strand == pdp1.strand
    assert record.locations == pdp1.locations
    assert record.location_annotations == pdp1.location_annotations
    assert record.location_annotations == pdp1.location_annotations

    response = ncbi.normalize('NCBIGENE:54704')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == pdp1.label
    assert record.concept_id == pdp1.concept_id
    assert record.symbol == pdp1.symbol
    assert len(record.aliases) == len(pdp1.aliases)
    assert set(record.aliases) == set(pdp1.aliases)
    assert set(record.previous_symbols) == set(pdp1.previous_symbols)
    assert set(record.xrefs) == set(pdp1.xrefs)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.strand == pdp1.strand
    assert record.locations == pdp1.locations
    assert record.location_annotations == pdp1.location_annotations
    assert record.location_annotations == pdp1.location_annotations

    response = ncbi.normalize('ncbIgene:8193')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.previous_symbols) == set(dpf1.previous_symbols)
    assert set(record.xrefs) == set(dpf1.xrefs)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.strand == dpf1.strand
    assert record.locations == dpf1.locations
    assert record.location_annotations == dpf1.location_annotations

    response = ncbi.normalize('NCBIgene:10251')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == spry3.label
    assert record.concept_id == spry3.concept_id
    assert record.symbol == spry3.symbol
    assert set(record.aliases) == set(spry3.aliases)
    assert set(record.previous_symbols) == set(spry3.previous_symbols)
    assert set(record.xrefs) == set(spry3.xrefs)
    assert set(record.other_identifiers) == set(spry3.other_identifiers)
    assert record.symbol_status == spry3.symbol_status
    assert record.strand == spry3.strand
    assert len(record.locations) == len(spry3.locations)
    for loc in spry3.locations:
        assert loc in record.locations
    assert record.location_annotations == spry3.location_annotations

    response = ncbi.normalize('ncblgene:8193')
    assert response['match_type'] == 0

    response = ncbi.normalize('NCBIGENE54704')
    assert response['match_type'] == 0

    response = ncbi.normalize('54704')
    assert response['match_type'] == 0

    response = ncbi.normalize('ncbigene;54704')
    assert response['match_type'] == 0


def test_symbol(ncbi, dpf1, pdp1, spry3):
    """Test query normalizing on gene symbol."""
    response = ncbi.normalize('DPF1')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.previous_symbols) == set(dpf1.previous_symbols)
    assert set(record.xrefs) == set(dpf1.xrefs)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.strand == dpf1.strand
    assert record.locations == dpf1.locations
    assert record.location_annotations == dpf1.location_annotations

    response = ncbi.normalize('PDP1')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == pdp1.label
    assert record.concept_id == pdp1.concept_id
    assert record.symbol == pdp1.symbol
    assert set(record.aliases) == set(pdp1.aliases)
    assert set(record.previous_symbols) == set(pdp1.previous_symbols)
    assert set(record.xrefs) == set(pdp1.xrefs)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.strand == pdp1.strand
    assert record.locations == pdp1.locations
    assert record.location_annotations == pdp1.location_annotations

    response = ncbi.normalize('pdp1')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == pdp1.label
    assert record.concept_id == pdp1.concept_id
    assert record.symbol == pdp1.symbol
    assert set(record.aliases) == set(pdp1.aliases)
    assert set(record.previous_symbols) == set(pdp1.previous_symbols)
    assert set(record.xrefs) == set(pdp1.xrefs)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.strand == pdp1.strand
    assert record.locations == pdp1.locations

    response = ncbi.normalize('DpF1')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.previous_symbols) == set(dpf1.previous_symbols)
    assert set(record.xrefs) == set(dpf1.xrefs)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.strand == dpf1.strand
    assert record.locations == dpf1.locations
    assert record.location_annotations == dpf1.location_annotations

    response = ncbi.normalize('sprY3')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == spry3.label
    assert record.concept_id == spry3.concept_id
    assert record.symbol == spry3.symbol
    assert set(record.aliases) == set(spry3.aliases)
    assert set(record.previous_symbols) == set(spry3.previous_symbols)
    assert set(record.xrefs) == set(spry3.xrefs)
    assert set(record.other_identifiers) == set(spry3.other_identifiers)
    assert record.symbol_status == spry3.symbol_status
    assert record.strand == spry3.strand
    assert len(record.locations) == len(spry3.locations)
    for loc in spry3.locations:
        assert loc in record.locations
    assert record.location_annotations == spry3.location_annotations

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
    assert set(record.previous_symbols) == set(pdp1.previous_symbols)
    assert set(record.xrefs) == set(pdp1.xrefs)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.strand == pdp1.strand
    assert record.locations == pdp1.locations
    assert record.location_annotations == pdp1.location_annotations

    response2 = ncbi.normalize('PPM2C')
    assert response == response2
    response3 = ncbi.normalize('loc157663')
    assert response == response3


def test_alias(ncbi, dpf1, pdp1, spry3):
    """Test that query term normalizes for gene aliases."""
    response = ncbi.normalize('BAF45b')
    assert response['match_type'] == 60
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.previous_symbols) == set(dpf1.previous_symbols)
    assert set(record.xrefs) == set(dpf1.xrefs)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.strand == dpf1.strand
    assert record.locations == dpf1.locations
    assert record.location_annotations == dpf1.location_annotations

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
    assert set(record.previous_symbols) == set(pdp1.previous_symbols)
    assert set(record.xrefs) == set(pdp1.xrefs)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.strand == pdp1.strand
    assert record.locations == pdp1.locations
    assert record.location_annotations == pdp1.location_annotations

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
    assert set(record.previous_symbols) == set(pdp1.previous_symbols)
    assert set(record.xrefs) == set(pdp1.xrefs)
    assert set(record.other_identifiers) == set(pdp1.other_identifiers)
    assert record.symbol_status == pdp1.symbol_status
    assert record.strand == pdp1.strand
    assert record.locations == pdp1.locations
    assert record.location_annotations == pdp1.location_annotations

    response = ncbi.normalize('BAF45B')
    assert response['match_type'] == 60
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == dpf1.label
    assert record.concept_id == dpf1.concept_id
    assert record.symbol == dpf1.symbol
    assert set(record.aliases) == set(dpf1.aliases)
    assert set(record.previous_symbols) == set(dpf1.previous_symbols)
    assert set(record.xrefs) == set(dpf1.xrefs)
    assert set(record.other_identifiers) == set(dpf1.other_identifiers)
    assert record.symbol_status == dpf1.symbol_status
    assert record.strand == dpf1.strand
    assert record.locations == dpf1.locations
    assert record.location_annotations == dpf1.location_annotations

    response = ncbi.normalize('SPRY-3')
    assert response['match_type'] == 60
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == spry3.label
    assert record.concept_id == spry3.concept_id
    assert record.symbol == spry3.symbol
    assert set(record.aliases) == set(spry3.aliases)
    assert set(record.previous_symbols) == set(spry3.previous_symbols)
    assert set(record.xrefs) == set(spry3.xrefs)
    assert set(record.other_identifiers) == set(spry3.other_identifiers)
    assert record.symbol_status == spry3.symbol_status
    assert record.strand == spry3.strand
    assert len(record.locations) == len(spry3.locations)
    for loc in spry3.locations:
        assert loc in record.locations
    assert record.location_annotations == spry3.location_annotations


def test_adcp1(ncbi, adcp1):
    """Test that ADCP1 matches to correct gene concept."""
    response = ncbi.normalize('NCBIgene:106')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == adcp1.label
    assert record.concept_id == adcp1.concept_id
    assert record.symbol == adcp1.symbol
    assert set(record.aliases) == set(adcp1.aliases)
    assert set(record.previous_symbols) == set(adcp1.previous_symbols)
    assert set(record.xrefs) == set(adcp1.xrefs)
    assert set(record.other_identifiers) == set(adcp1.other_identifiers)
    assert record.symbol_status == adcp1.symbol_status
    assert record.strand == adcp1.strand
    assert len(record.locations) == len(adcp1.locations)
    assert record.locations == adcp1.locations
    assert record.location_annotations == adcp1.location_annotations

    response = ncbi.normalize('ADCP1')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == adcp1.label
    assert record.concept_id == adcp1.concept_id
    assert record.symbol == adcp1.symbol
    assert set(record.aliases) == set(adcp1.aliases)
    assert set(record.previous_symbols) == set(adcp1.previous_symbols)
    assert set(record.xrefs) == set(adcp1.xrefs)
    assert set(record.other_identifiers) == set(adcp1.other_identifiers)
    assert record.symbol_status == adcp1.symbol_status
    assert record.strand == adcp1.strand
    assert len(record.locations) == len(adcp1.locations)
    for loc in adcp1.locations:
        assert loc in record.locations
    assert record.location_annotations == adcp1.location_annotations


def test_afa(ncbi, afa):
    """Test that AFA matches to correct gene concept."""
    response = ncbi.normalize('NCBIgene:170')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == afa.label
    assert record.concept_id == afa.concept_id
    assert record.symbol == afa.symbol
    assert set(record.aliases) == set(afa.aliases)
    assert set(record.previous_symbols) == set(afa.previous_symbols)
    assert set(record.xrefs) == set(afa.xrefs)
    assert set(record.other_identifiers) == set(afa.other_identifiers)
    assert record.symbol_status == afa.symbol_status
    assert record.strand == afa.strand
    assert record.locations == afa.locations
    assert record.location_annotations == afa.location_annotations

    response = ncbi.normalize('AFA')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == afa.label
    assert record.concept_id == afa.concept_id
    assert record.symbol == afa.symbol
    assert set(record.aliases) == set(afa.aliases)
    assert set(record.previous_symbols) == set(afa.previous_symbols)
    assert set(record.xrefs) == set(afa.xrefs)
    assert set(record.other_identifiers) == set(afa.other_identifiers)
    assert record.symbol_status == afa.symbol_status
    assert record.strand == afa.strand
    assert record.locations == afa.locations
    assert record.location_annotations == afa.location_annotations


def test_znf84(ncbi, znf84):
    """Test that ZNF84 matches to correct gene concept."""
    response = ncbi.normalize('NCBIgene:7637')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == znf84.label
    assert record.concept_id == znf84.concept_id
    assert record.symbol == znf84.symbol
    assert set(record.aliases) == set(znf84.aliases)
    assert set(record.previous_symbols) == set(znf84.previous_symbols)
    assert set(record.xrefs) == set(znf84.xrefs)
    assert set(record.other_identifiers) == set(znf84.other_identifiers)
    assert record.symbol_status == znf84.symbol_status
    assert record.strand == znf84.strand
    assert len(record.locations) == len(znf84.locations)
    for loc in znf84.locations:
        assert loc in record.locations
    assert record.location_annotations == znf84.location_annotations

    response = ncbi.normalize('ZNF84')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == znf84.label
    assert record.concept_id == znf84.concept_id
    assert record.symbol == znf84.symbol
    assert set(record.aliases) == set(znf84.aliases)
    assert set(record.previous_symbols) == set(znf84.previous_symbols)
    assert set(record.xrefs) == set(znf84.xrefs)
    assert set(record.other_identifiers) == set(znf84.other_identifiers)
    assert record.symbol_status == znf84.symbol_status
    assert record.strand == znf84.strand
    assert len(record.locations) == len(znf84.locations)
    for loc in znf84.locations:
        assert loc in record.locations
    assert record.location_annotations == znf84.location_annotations


def test_slc25a6(ncbi, slc25a6):
    """Test that SLC25A6 matches to correct gene concept."""
    response = ncbi.normalize('NCBIgene:293')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == slc25a6.label
    assert record.concept_id == slc25a6.concept_id
    assert record.symbol == slc25a6.symbol
    assert set(record.aliases) == set(slc25a6.aliases)
    assert set(record.previous_symbols) == set(slc25a6.previous_symbols)
    assert set(record.xrefs) == set(slc25a6.xrefs)
    assert set(record.other_identifiers) == set(slc25a6.other_identifiers)
    assert record.symbol_status == slc25a6.symbol_status
    assert record.strand == slc25a6.strand
    assert len(record.locations) == len(slc25a6.locations)
    for loc in slc25a6.locations:
        assert loc in record.locations
    assert record.location_annotations == slc25a6.location_annotations

    response = ncbi.normalize('SLC25A6')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == slc25a6.label
    assert record.concept_id == slc25a6.concept_id
    assert record.symbol == slc25a6.symbol
    assert set(record.aliases) == set(slc25a6.aliases)
    assert set(record.previous_symbols) == set(slc25a6.previous_symbols)
    assert set(record.xrefs) == set(slc25a6.xrefs)
    assert set(record.other_identifiers) == set(slc25a6.other_identifiers)
    assert record.symbol_status == slc25a6.symbol_status
    assert record.strand == slc25a6.strand
    assert len(record.locations) == len(slc25a6.locations)
    for loc in slc25a6.locations:
        assert loc in record.locations
    assert record.location_annotations == slc25a6.location_annotations


def test_loc106783576(ncbi, loc106783576):
    """Test that LOC106783576 matches to correct gene concept."""
    response = ncbi.normalize('NCBIgene:106783576')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == loc106783576.label
    assert record.concept_id == loc106783576.concept_id
    assert record.symbol == loc106783576.symbol
    assert set(record.aliases) == set(loc106783576.aliases)
    assert set(record.previous_symbols) == set(loc106783576.previous_symbols)
    assert set(record.xrefs) == set(loc106783576.xrefs)
    assert set(record.other_identifiers) == set(loc106783576.other_identifiers)
    assert record.symbol_status == loc106783576.symbol_status
    assert record.strand == loc106783576.strand
    assert len(record.locations) == len(loc106783576.locations)
    assert record.locations == loc106783576.locations
    assert record.location_annotations == loc106783576.location_annotations

    response = ncbi.normalize('LOC106783576')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == loc106783576.label
    assert record.concept_id == loc106783576.concept_id
    assert record.symbol == loc106783576.symbol
    assert set(record.aliases) == set(loc106783576.aliases)
    assert set(record.previous_symbols) == set(loc106783576.previous_symbols)
    assert set(record.xrefs) == set(loc106783576.xrefs)
    assert set(record.other_identifiers) == set(loc106783576.other_identifiers)
    assert record.symbol_status == loc106783576.symbol_status
    assert record.strand == loc106783576.strand
    assert len(record.locations) == len(loc106783576.locations)
    assert record.locations == loc106783576.locations
    assert record.location_annotations == loc106783576.location_annotations


def test_oms(ncbi, oms):
    """Test that OMS matches to correct gene concept."""
    response = ncbi.normalize('NCBIgene:619538')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == oms.label
    assert record.concept_id == oms.concept_id
    assert record.symbol == oms.symbol
    assert set(record.aliases) == set(oms.aliases)
    assert set(record.previous_symbols) == set(oms.previous_symbols)
    assert set(record.xrefs) == set(oms.xrefs)
    assert set(record.other_identifiers) == set(oms.other_identifiers)
    assert record.symbol_status == oms.symbol_status
    assert record.strand == oms.strand
    assert len(record.locations) == len(oms.locations)
    for loc in oms.locations:
        assert loc in record.locations
    assert record.location_annotations == oms.location_annotations

    response = ncbi.normalize('OMS')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == oms.label
    assert record.concept_id == oms.concept_id
    assert record.symbol == oms.symbol
    assert set(record.aliases) == set(oms.aliases)
    assert set(record.previous_symbols) == set(oms.previous_symbols)
    assert set(record.xrefs) == set(oms.xrefs)
    assert set(record.other_identifiers) == set(oms.other_identifiers)
    assert record.symbol_status == oms.symbol_status
    assert record.strand == oms.strand
    assert len(record.locations) == len(oms.locations)
    for loc in oms.locations:
        assert loc in record.locations
    assert record.location_annotations == oms.location_annotations


def test_glc1b(ncbi, glc1b):
    """Test that GLC1B matches to correct gene concept."""
    response = ncbi.normalize('NCBIgene:2722')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == glc1b.label
    assert record.concept_id == glc1b.concept_id
    assert record.symbol == glc1b.symbol
    assert set(record.aliases) == set(glc1b.aliases)
    assert set(record.previous_symbols) == set(glc1b.previous_symbols)
    assert set(record.xrefs) == set(glc1b.xrefs)
    assert set(record.other_identifiers) == set(glc1b.other_identifiers)
    assert record.symbol_status == glc1b.symbol_status
    assert record.strand == glc1b.strand
    assert len(record.locations) == len(glc1b.locations)
    assert record.locations == glc1b.locations
    assert record.location_annotations == glc1b.location_annotations

    response = ncbi.normalize('GLC1B')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == glc1b.label
    assert record.concept_id == glc1b.concept_id
    assert record.symbol == glc1b.symbol
    assert set(record.aliases) == set(glc1b.aliases)
    assert set(record.previous_symbols) == set(glc1b.previous_symbols)
    assert set(record.xrefs) == set(glc1b.xrefs)
    assert set(record.other_identifiers) == set(glc1b.other_identifiers)
    assert record.symbol_status == glc1b.symbol_status
    assert record.strand == glc1b.strand
    assert len(record.locations) == len(glc1b.locations)
    assert record.locations == glc1b.locations
    assert record.location_annotations == glc1b.location_annotations


def test_hdpa(ncbi, hdpa):
    """Test that HDPA matches to correct gene concept."""
    response = ncbi.normalize('NCBIgene:50829')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == hdpa.label
    assert record.concept_id == hdpa.concept_id
    assert record.symbol == hdpa.symbol
    assert set(record.aliases) == set(hdpa.aliases)
    assert set(record.previous_symbols) == set(hdpa.previous_symbols)
    assert set(record.xrefs) == set(hdpa.xrefs)
    assert set(record.other_identifiers) == set(hdpa.other_identifiers)
    assert record.symbol_status == hdpa.symbol_status
    assert record.strand == hdpa.strand
    assert len(record.locations) == len(hdpa.locations)
    assert record.locations == hdpa.locations
    assert record.location_annotations == hdpa.location_annotations

    response = ncbi.normalize('HDPA')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == hdpa.label
    assert record.concept_id == hdpa.concept_id
    assert record.symbol == hdpa.symbol
    assert set(record.aliases) == set(hdpa.aliases)
    assert set(record.previous_symbols) == set(hdpa.previous_symbols)
    assert set(record.xrefs) == set(hdpa.xrefs)
    assert set(record.other_identifiers) == set(hdpa.other_identifiers)
    assert record.symbol_status == hdpa.symbol_status
    assert record.strand == hdpa.strand
    assert len(record.locations) == len(hdpa.locations)
    assert record.locations == hdpa.locations
    assert record.location_annotations == hdpa.location_annotations


def test_prkrap1(ncbi, prkrap1):
    """Test that PRKRAP1 matches to correct gene concept."""
    response = ncbi.normalize('NCBIgene:731716')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == prkrap1.label
    assert record.concept_id == prkrap1.concept_id
    assert record.symbol == prkrap1.symbol
    assert set(record.aliases) == set(prkrap1.aliases)
    assert set(record.previous_symbols) == set(prkrap1.previous_symbols)
    assert set(record.xrefs) == set(prkrap1.xrefs)
    assert set(record.other_identifiers) == set(prkrap1.other_identifiers)
    assert record.symbol_status == prkrap1.symbol_status
    assert record.strand == prkrap1.strand
    assert len(record.locations) == len(prkrap1.locations)
    for loc in prkrap1.locations:
        assert loc in record.locations
    assert record.location_annotations == prkrap1.location_annotations

    response = ncbi.normalize('PRKRAP1')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == prkrap1.label
    assert record.concept_id == prkrap1.concept_id
    assert record.symbol == prkrap1.symbol
    assert set(record.aliases) == set(prkrap1.aliases)
    assert set(record.previous_symbols) == set(prkrap1.previous_symbols)
    assert set(record.xrefs) == set(prkrap1.xrefs)
    assert set(record.other_identifiers) == set(prkrap1.other_identifiers)
    assert record.symbol_status == prkrap1.symbol_status
    assert record.strand == prkrap1.strand
    assert len(record.locations) == len(prkrap1.locations)
    for loc in prkrap1.locations:
        assert loc in record.locations
    assert record.location_annotations == prkrap1.location_annotations


def test_mhb(ncbi, mhb):
    """Test that MHB matches to correct gene concept."""
    response = ncbi.normalize('NCBIgene:619511')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == mhb.label
    assert record.concept_id == mhb.concept_id
    assert record.symbol == mhb.symbol
    assert set(record.aliases) == set(mhb.aliases)
    assert set(record.previous_symbols) == set(mhb.previous_symbols)
    assert set(record.xrefs) == set(mhb.xrefs)
    assert set(record.other_identifiers) == set(mhb.other_identifiers)
    assert record.symbol_status == mhb.symbol_status
    assert record.strand == mhb.strand
    assert len(record.locations) == len(mhb.locations)
    assert record.locations == mhb.locations
    assert record.location_annotations == mhb.location_annotations

    response = ncbi.normalize('MHB')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == mhb.label
    assert record.concept_id == mhb.concept_id
    assert record.symbol == mhb.symbol
    assert set(record.aliases) == set(mhb.aliases)
    assert set(record.previous_symbols) == set(mhb.previous_symbols)
    assert set(record.xrefs) == set(mhb.xrefs)
    assert set(record.other_identifiers) == set(mhb.other_identifiers)
    assert record.symbol_status == mhb.symbol_status
    assert record.strand == mhb.strand
    assert len(record.locations) == len(mhb.locations)
    assert record.locations == mhb.locations
    assert record.location_annotations == mhb.location_annotations


def test_spg37(ncbi, spg37):
    """Test that SPG37 matches to correct gene concept."""
    response = ncbi.normalize('NCBIgene:100049159')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == spg37.label
    assert record.concept_id == spg37.concept_id
    assert record.symbol == spg37.symbol
    assert set(record.aliases) == set(spg37.aliases)
    assert set(record.previous_symbols) == set(spg37.previous_symbols)
    assert set(record.xrefs) == set(spg37.xrefs)
    assert set(record.other_identifiers) == set(spg37.other_identifiers)
    assert record.symbol_status == spg37.symbol_status
    assert record.strand == spg37.strand
    assert len(record.locations) == len(spg37.locations)
    assert record.locations == spg37.locations
    assert record.location_annotations == spg37.location_annotations

    response = ncbi.normalize('SPG37')
    assert response['match_type'] == 100
    assert len(response['records']) == 1
    record = response['records'][0]
    assert record.label == spg37.label
    assert record.concept_id == spg37.concept_id
    assert record.symbol == spg37.symbol
    assert set(record.aliases) == set(spg37.aliases)
    assert set(record.previous_symbols) == set(spg37.previous_symbols)
    assert set(record.xrefs) == set(spg37.xrefs)
    assert set(record.other_identifiers) == set(spg37.other_identifiers)
    assert record.symbol_status == spg37.symbol_status
    assert record.strand == spg37.strand
    assert len(record.locations) == len(spg37.locations)
    assert record.locations == spg37.locations
    assert record.location_annotations == spg37.location_annotations


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
        'ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/'
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
        'ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/'
    assert response['meta_'].rdp_url == \
        'https://reusabledata.org/ncbi-gene.html'
    assert not response['meta_'].non_commercial
    assert not response['meta_'].share_alike
    assert not response['meta_'].attribution
    assert response['meta_'].genome_assemblies == ['GRCh38.p13']
