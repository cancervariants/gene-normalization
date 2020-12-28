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
        'location_annotations': None,
        'locations': [
            {
                'chr': '19',
                'interval': {
                    'end': 'q13.43',
                    'start': 'q13.43',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ],
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
    """Create a TP53 gene fixture."""
    params = {
        'label': 'tumor protein p53',
        'concept_id': 'hgnc:11998',
        'symbol': 'TP53',
        'location_annotations': None,
        'locations': [
            {
                'chr': '17',
                'interval': {
                    'end': 'p13.1',
                    'start': 'p13.1',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ],
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
        'location_annotations': None,
        'locations': [
            {
                'chr': '1',
                'interval': {
                    'end': 'p35.1',
                    'start': 'p35.1',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ],
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


@pytest.fixture(scope='module')
def wdhd1():
    """Create a WDHD1 gene fixture."""
    params = {
        'label': 'WD repeat and HMG-box DNA binding protein 1',
        'concept_id': 'hgnc:23170',
        'symbol': 'WDHD1',
        'location_annotations': None,
        'locations': [
            {
                'chr': '14',
                'interval': {
                    'end': 'q22.3',
                    'start': 'q22.2',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ],
        'previous_symbols': [],
        'aliases': [
            'AND-1',
            'CTF4',
            'CHTF4'
        ],
        'symbol_status': 'approved',
        'other_identifiers': [
            'ensembl:ENSG00000198554',
            'ncbigene:11169'
        ],
        'xrefs': [
            'vega:OTTHUMG00000140304',
            'refseq:NM_007086',
            'omim:608126',
            'ucsc:uc001xbm.3',
            'uniprot:O75717',
            'ccds:CCDS41955',
            'ccds:CCDS9721',
            'ena.embl:AJ006266',
            'pubmed:9175701',
            'pubmed:20028748'
        ]
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def g6pr():
    """Create a G6PR gene fixture."""
    params = {
        'label': 'glucose-6-phosphatase regulator',
        'concept_id': 'hgnc:4059',
        'symbol': 'G6PR',
        'location_annotations': {
            'annotation': 'reserved'
        },
        'locations': [],
        'previous_symbols': [],
        'aliases': [
            'GSD1aSP'
        ],
        'symbol_status': 'approved',
        'other_identifiers': [
            'ncbigene:2541'
        ],
        'xrefs': [
            'pubmed:2172641',
            'pubmed:7814621',
            'pubmed:2996501'
        ]
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def pirc24():
    """Create a PIRC24 gene fixture."""
    params = {
        'label': 'piwi-interacting RNA cluster 24',
        'concept_id': 'hgnc:37528',
        'symbol': 'PIRC24',
        'location_annotations': {
            'chr': ['6']
        },
        'locations': [],
        'previous_symbols': [],
        'aliases': [
        ],
        'symbol_status': 'approved',
        'other_identifiers': [
            'ncbigene:100313810'
        ],
        'xrefs': [
            'pubmed:17881367'
        ]
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def gage4():
    """Create a GAGE4 gene fixture."""
    params = {
        'label': 'G antigen 4',
        'concept_id': 'hgnc:4101',
        'symbol': 'GAGE4',
        'location_annotations': {
            'annotation': 'not on reference assembly'
        },
        'locations': [
            {
                'chr': 'X',
                'interval': {
                    'end': 'p11.4',
                    'start': 'p11.2',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ],
        'previous_symbols': [],
        'aliases': [
            'CT4.4'
        ],
        'symbol_status': 'approved',
        'other_identifiers': [
            'ncbigene:2576'
        ],
        'xrefs': [
            'refseq:NM_001474',
            'omim:300597',
            'uniprot:P0DSO3',
            'ena.embl:U19145',
            'pubmed:7544395'
        ]
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def mafip():
    """Create a MAFIP gene fixture."""
    params = {
        'label': 'MAFF interacting protein (pseudogene)',
        'concept_id': 'hgnc:31102',
        'symbol': 'MAFIP',
        'location_annotations': {
            'annotation': 'unplaced',
            'chr': ['14']
        },
        'locations': [],
        'previous_symbols': [],
        'aliases': [
            'FLJ35473',
            'FLJ00219',
            'FLJ39633',
            'MIP',
            'pp5644',
            'TEKT4P4'
        ],
        'symbol_status': 'approved',
        'other_identifiers': [
            'ensembl:ENSG00000274847',
            'ncbigene:727764'
        ],
        'xrefs': [
            'vega:OTTHUMG00000188065',
            'refseq:NR_046439',
            'uniprot:Q8WZ33',
            'ena.embl:AK074146',
            'ena.embl:AF289559',
            'pubmed:16549056',
            'pubmed:15881666'
        ]
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def mt_7sdna():
    """Create a MT-7SDNA gene fixture."""
    params = {
        'label': 'mitochondrially encoded 7S DNA',
        'concept_id': 'hgnc:7409',
        'symbol': 'MT-7SDNA',
        'location_annotations': {
            'chr': ['MT']
        },
        'locations': [],
        'previous_symbols': [
            'MT7SDNA'
        ],
        'aliases': [],
        'symbol_status': 'approved',
        'other_identifiers': [],
        'xrefs': [
            'pubmed:24709344',
            'pubmed:273237'
        ]
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def cecr():
    """Create a CECR gene fixture."""
    params = {
        'label': 'cat eye syndrome chromosome region',
        'concept_id': 'hgnc:1838',
        'symbol': 'CECR',
        'location_annotations': None,
        'locations': [
            {
                'chr': '22',
                'interval': {
                    'end': 'q11',
                    'start': 'pter',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ],
        'previous_symbols': [],
        'aliases': [
        ],
        'symbol_status': 'approved',
        'other_identifiers': [
            'ncbigene:1055'
        ],
        'xrefs': []
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def csf2ra():
    """Create a CSF2RA gene fixture."""
    params = {
        'label': 'colony stimulating factor 2 receptor subunit alpha',
        'concept_id': 'hgnc:2435',
        'symbol': 'CSF2RA',
        'location_annotations': None,
        'locations': [
            {
                'chr': 'X',
                'interval': {
                    'end': 'p22.32',
                    'start': 'p22.32',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            },
            {
                'chr': 'Y',
                'interval': {
                    'end': 'p11.3',
                    'start': 'p11.3',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ],
        'previous_symbols': [
            'CSF2R'
        ],
        'aliases': [
            'CD116',
            'alphaGMR'
        ],
        'symbol_status': 'approved',
        'other_identifiers': [
            'ensembl:ENSG00000198223',
            'ncbigene:1438'
        ],
        'xrefs': [
            'vega:OTTHUMG00000012533',
            'refseq:NM_001161529',
            'orphanet:209477',
            'iuphar:1707',
            'hcdmdb:CD116',
            'omim:306250',
            'omim:425000',
            'ucsc:uc010nvv.3',
            'uniprot:P15509',
            'ena.embl:M64445',
            'ccds:CCDS35190',
            'ccds:CCDS55360',
            'ccds:CCDS35191',
            'ccds:CCDS55361',
            'ccds:CCDS55359',
            'ccds:CCDS35192',
            'ccds:CCDS35193',
            'pubmed:1702217'
        ]
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def rps24p5():
    """Create a RPS24P5 gene fixture."""
    params = {
        'label': 'ribosomal protein S24 pseudogene 5',
        'concept_id': 'hgnc:36026',
        'symbol': 'RPS24P5',
        'location_annotations': None,
        'locations': [
            {
                'chr': '1',
                'interval': {
                    'end': 'q41',
                    'start': 'p36.13',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ],
        'previous_symbols': [
        ],
        'aliases': [
        ],
        'symbol_status': 'approved',
        'other_identifiers': [
            'ncbigene:100271094'
        ],
        'xrefs': [
            'refseq:NG_011274',
            'pubmed:19123937'
        ]
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def trl_cag2_1():
    """Create a TRL-CAG2-1 gene fixture."""
    params = {
        'label': 'tRNA-Leu (anticodon CAG) 2-1',
        'concept_id': 'hgnc:34692',
        'symbol': 'TRL-CAG2-1',
        'location_annotations': None,
        'locations': [
            {
                'chr': '16',
                'interval': {
                    'end': 'q21',
                    'start': 'q13',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ],
        'previous_symbols': [
            'TRNAL13'
        ],
        'aliases': [
            'tRNA-Leu-CAG-2-1'
        ],
        'symbol_status': 'approved',
        'other_identifiers': [
            'ncbigene:100189130'
        ],
        'xrefs': [
            'ena.embl:HG983896'
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
    assert normalized_gene.locations == a1bg_as1.locations
    assert normalized_gene.location_annotations == \
           a1bg_as1.location_annotations

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
    assert normalized_gene.locations == a1bg_as1.locations
    assert normalized_gene.location_annotations == \
           a1bg_as1.location_annotations

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
    assert normalized_gene.locations == a1bg_as1.locations
    assert normalized_gene.location_annotations == \
           a1bg_as1.location_annotations


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
    assert normalized_gene.locations == a1bg_as1.locations
    assert normalized_gene.location_annotations == \
           a1bg_as1.location_annotations

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
    assert normalized_gene.locations == a1bg_as1.locations
    assert normalized_gene.location_annotations == \
           a1bg_as1.location_annotations


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
    assert normalized_gene.locations == a1bg_as1.locations
    assert normalized_gene.location_annotations == \
           a1bg_as1.location_annotations

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
    assert normalized_gene.locations == a1bg_as1.locations
    assert normalized_gene.location_annotations == \
           a1bg_as1.location_annotations

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
    assert normalized_gene.locations == a1bg_as1.locations
    assert normalized_gene.location_annotations == \
           a1bg_as1.location_annotations


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
    assert normalized_gene.locations == a1bg_as1.locations
    assert normalized_gene.location_annotations == \
           a1bg_as1.location_annotations

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
    assert normalized_gene.locations == a1bg_as1.locations
    assert normalized_gene.location_annotations == \
           a1bg_as1.location_annotations


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
    assert normalized_gene.locations == a3galt2.locations
    assert normalized_gene.location_annotations == a3galt2.location_annotations

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
    assert normalized_gene.locations == a3galt2.locations
    assert normalized_gene.location_annotations == a3galt2.location_annotations

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
    assert normalized_gene.locations == a3galt2.locations
    assert normalized_gene.location_annotations == a3galt2.location_annotations


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
    assert normalized_gene.locations == a3galt2.locations
    assert normalized_gene.location_annotations == a3galt2.location_annotations

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
    assert normalized_gene.locations == a3galt2.locations
    assert normalized_gene.location_annotations == a3galt2.location_annotations


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
    assert normalized_gene.locations == a3galt2.locations
    assert normalized_gene.location_annotations == a3galt2.location_annotations

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
    assert normalized_gene.locations == a3galt2.locations
    assert normalized_gene.location_annotations == a3galt2.location_annotations


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
    assert normalized_gene.locations == a3galt2.locations
    assert normalized_gene.location_annotations == a3galt2.location_annotations

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
    assert normalized_gene.locations == a3galt2.locations
    assert normalized_gene.location_annotations == a3galt2.location_annotations


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
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations

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
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations

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
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations


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
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations

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
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations


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
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations

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
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations


def test_wdhd1(wdhd1, hgnc):
    """Test that wdhd1 gene normalizes to correct gene concept."""
    normalizer_response = hgnc.normalize('hgnc:23170')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == wdhd1.label
    assert normalized_gene.concept_id == wdhd1.concept_id
    assert set(normalized_gene.aliases) == set(wdhd1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(wdhd1.other_identifiers)
    assert normalized_gene.symbol_status == wdhd1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(wdhd1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(wdhd1.xrefs)
    assert normalized_gene.symbol == wdhd1.symbol
    assert normalized_gene.locations == wdhd1.locations
    assert normalized_gene.location_annotations == wdhd1.location_annotations

    normalizer_response = hgnc.normalize('WDHD1')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == wdhd1.label
    assert normalized_gene.concept_id == wdhd1.concept_id
    assert set(normalized_gene.aliases) == set(wdhd1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(wdhd1.other_identifiers)
    assert normalized_gene.symbol_status == wdhd1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(wdhd1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(wdhd1.xrefs)
    assert normalized_gene.symbol == wdhd1.symbol
    assert normalized_gene.locations == wdhd1.locations
    assert normalized_gene.location_annotations == wdhd1.location_annotations


def test_g6pr(g6pr, hgnc):
    """Test that g6pr gene normalizes to correct gene concept."""
    normalizer_response = hgnc.normalize('hgnc:4059')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == g6pr.label
    assert normalized_gene.concept_id == g6pr.concept_id
    assert set(normalized_gene.aliases) == set(g6pr.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(g6pr.other_identifiers)
    assert normalized_gene.symbol_status == g6pr.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(g6pr.previous_symbols)
    assert set(normalized_gene.xrefs) == set(g6pr.xrefs)
    assert normalized_gene.symbol == g6pr.symbol
    assert normalized_gene.locations == g6pr.locations
    assert normalized_gene.location_annotations == g6pr.location_annotations

    normalizer_response = hgnc.normalize('G6PR')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == g6pr.label
    assert normalized_gene.concept_id == g6pr.concept_id
    assert set(normalized_gene.aliases) == set(g6pr.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(g6pr.other_identifiers)
    assert normalized_gene.symbol_status == g6pr.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(g6pr.previous_symbols)
    assert set(normalized_gene.xrefs) == set(g6pr.xrefs)
    assert normalized_gene.symbol == g6pr.symbol
    assert normalized_gene.locations == g6pr.locations
    assert normalized_gene.location_annotations == g6pr.location_annotations


def test_pirc24(pirc24, hgnc):
    """Test that pirc24 gene normalizes to correct gene concept."""
    normalizer_response = hgnc.normalize('hgnc:37528')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == pirc24.label
    assert normalized_gene.concept_id == pirc24.concept_id
    assert set(normalized_gene.aliases) == set(pirc24.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(pirc24.other_identifiers)
    assert normalized_gene.symbol_status == pirc24.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(pirc24.previous_symbols)
    assert set(normalized_gene.xrefs) == set(pirc24.xrefs)
    assert normalized_gene.symbol == pirc24.symbol
    assert normalized_gene.locations == pirc24.locations
    assert normalized_gene.location_annotations == pirc24.location_annotations

    normalizer_response = hgnc.normalize('PIRC24')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == pirc24.label
    assert normalized_gene.concept_id == pirc24.concept_id
    assert set(normalized_gene.aliases) == set(pirc24.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(pirc24.other_identifiers)
    assert normalized_gene.symbol_status == pirc24.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(pirc24.previous_symbols)
    assert set(normalized_gene.xrefs) == set(pirc24.xrefs)
    assert normalized_gene.symbol == pirc24.symbol
    assert normalized_gene.locations == pirc24.locations
    assert normalized_gene.location_annotations == pirc24.location_annotations


def test_gage4(gage4, hgnc):
    """Test that gage4 gene normalizes to correct gene concept."""
    normalizer_response = hgnc.normalize('hgnc:4101')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == gage4.label
    assert normalized_gene.concept_id == gage4.concept_id
    assert set(normalized_gene.aliases) == set(gage4.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(gage4.other_identifiers)
    assert normalized_gene.symbol_status == gage4.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(gage4.previous_symbols)
    assert set(normalized_gene.xrefs) == set(gage4.xrefs)
    assert normalized_gene.symbol == gage4.symbol
    assert normalized_gene.locations == gage4.locations
    assert normalized_gene.location_annotations == gage4.location_annotations

    normalizer_response = hgnc.normalize('GAGE4')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == gage4.label
    assert normalized_gene.concept_id == gage4.concept_id
    assert set(normalized_gene.aliases) == set(gage4.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(gage4.other_identifiers)
    assert normalized_gene.symbol_status == gage4.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(gage4.previous_symbols)
    assert set(normalized_gene.xrefs) == set(gage4.xrefs)
    assert normalized_gene.symbol == gage4.symbol
    assert normalized_gene.locations == gage4.locations
    assert normalized_gene.location_annotations == gage4.location_annotations


def test_mafip(mafip, hgnc):
    """Test that mafip gene normalizes to correct gene concept."""
    normalizer_response = hgnc.normalize('hgnc:31102')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == mafip.label
    assert normalized_gene.concept_id == mafip.concept_id
    assert set(normalized_gene.aliases) == set(mafip.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(mafip.other_identifiers)
    assert normalized_gene.symbol_status == mafip.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(mafip.previous_symbols)
    assert set(normalized_gene.xrefs) == set(mafip.xrefs)
    assert normalized_gene.symbol == mafip.symbol
    assert normalized_gene.locations == mafip.locations
    assert normalized_gene.location_annotations == \
           mafip.location_annotations

    normalizer_response = hgnc.normalize('MAFIP')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == mafip.label
    assert normalized_gene.concept_id == mafip.concept_id
    assert set(normalized_gene.aliases) == set(mafip.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(mafip.other_identifiers)
    assert normalized_gene.symbol_status == mafip.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(mafip.previous_symbols)
    assert set(normalized_gene.xrefs) == set(mafip.xrefs)
    assert normalized_gene.symbol == mafip.symbol
    assert normalized_gene.locations == mafip.locations
    assert normalized_gene.location_annotations == mafip.location_annotations


def test_mt_7sdna(mt_7sdna, hgnc):
    """Test that mt_7sdna gene normalizes to correct gene concept."""
    normalizer_response = hgnc.normalize('hgnc:7409')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == mt_7sdna.label
    assert normalized_gene.concept_id == mt_7sdna.concept_id
    assert set(normalized_gene.aliases) == set(mt_7sdna.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(mt_7sdna.other_identifiers)
    assert normalized_gene.symbol_status == mt_7sdna.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(mt_7sdna.previous_symbols)
    assert set(normalized_gene.xrefs) == set(mt_7sdna.xrefs)
    assert normalized_gene.symbol == mt_7sdna.symbol
    assert normalized_gene.locations == mt_7sdna.locations
    assert normalized_gene.location_annotations == \
           mt_7sdna.location_annotations

    normalizer_response = hgnc.normalize('MT-7SDNA')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == mt_7sdna.label
    assert normalized_gene.concept_id == mt_7sdna.concept_id
    assert set(normalized_gene.aliases) == set(mt_7sdna.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(mt_7sdna.other_identifiers)
    assert normalized_gene.symbol_status == mt_7sdna.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(mt_7sdna.previous_symbols)
    assert set(normalized_gene.xrefs) == set(mt_7sdna.xrefs)
    assert normalized_gene.symbol == mt_7sdna.symbol
    assert normalized_gene.locations == mt_7sdna.locations
    assert normalized_gene.location_annotations == \
           mt_7sdna.location_annotations


def test_cecr(cecr, hgnc):
    """Test that cecr gene normalizes to correct gene concept."""
    normalizer_response = hgnc.normalize('hgnc:1838')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == cecr.label
    assert normalized_gene.concept_id == cecr.concept_id
    assert set(normalized_gene.aliases) == set(cecr.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(cecr.other_identifiers)
    assert normalized_gene.symbol_status == cecr.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(cecr.previous_symbols)
    assert set(normalized_gene.xrefs) == set(cecr.xrefs)
    assert normalized_gene.symbol == cecr.symbol
    assert normalized_gene.locations == cecr.locations
    assert normalized_gene.location_annotations == cecr.location_annotations

    normalizer_response = hgnc.normalize('CECR')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == cecr.label
    assert normalized_gene.concept_id == cecr.concept_id
    assert set(normalized_gene.aliases) == set(cecr.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(cecr.other_identifiers)
    assert normalized_gene.symbol_status == cecr.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(cecr.previous_symbols)
    assert set(normalized_gene.xrefs) == set(cecr.xrefs)
    assert normalized_gene.symbol == cecr.symbol
    assert normalized_gene.locations == cecr.locations
    assert normalized_gene.location_annotations == cecr.location_annotations


def test_csf2ra(csf2ra, hgnc):
    """Test that csf2ra gene normalizes to correct gene concept."""
    normalizer_response = hgnc.normalize('hgnc:2435')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == csf2ra.label
    assert normalized_gene.concept_id == csf2ra.concept_id
    assert set(normalized_gene.aliases) == set(csf2ra.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(csf2ra.other_identifiers)
    assert normalized_gene.symbol_status == csf2ra.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(csf2ra.previous_symbols)
    assert set(normalized_gene.xrefs) == set(csf2ra.xrefs)
    assert normalized_gene.symbol == csf2ra.symbol
    assert len(normalized_gene.locations) == len(csf2ra.locations)
    for loc in csf2ra.locations:
        assert loc in normalized_gene.locations
    assert normalized_gene.location_annotations == csf2ra.location_annotations

    normalizer_response = hgnc.normalize('CSF2RA')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == csf2ra.label
    assert normalized_gene.concept_id == csf2ra.concept_id
    assert set(normalized_gene.aliases) == set(csf2ra.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(csf2ra.other_identifiers)
    assert normalized_gene.symbol_status == csf2ra.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(csf2ra.previous_symbols)
    assert set(normalized_gene.xrefs) == set(csf2ra.xrefs)
    assert normalized_gene.symbol == csf2ra.symbol
    assert len(normalized_gene.locations) == len(csf2ra.locations)
    for loc in csf2ra.locations:
        assert loc in normalized_gene.locations
    assert normalized_gene.location_annotations == csf2ra.location_annotations


def test_rps24p5(rps24p5, hgnc):
    """Test that RPS24P5 gene normalizes to correct gene concept."""
    normalizer_response = hgnc.normalize('hgnc:36026')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == rps24p5.label
    assert normalized_gene.concept_id == rps24p5.concept_id
    assert set(normalized_gene.aliases) == set(rps24p5.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(rps24p5.other_identifiers)
    assert normalized_gene.symbol_status == rps24p5.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(rps24p5.previous_symbols)
    assert set(normalized_gene.xrefs) == set(rps24p5.xrefs)
    assert normalized_gene.symbol == rps24p5.symbol
    assert normalized_gene.locations == rps24p5.locations
    assert normalized_gene.location_annotations == rps24p5.location_annotations

    normalizer_response = hgnc.normalize('rpS24P5')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == rps24p5.label
    assert normalized_gene.concept_id == rps24p5.concept_id
    assert set(normalized_gene.aliases) == set(rps24p5.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(rps24p5.other_identifiers)
    assert normalized_gene.symbol_status == rps24p5.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(rps24p5.previous_symbols)
    assert set(normalized_gene.xrefs) == set(rps24p5.xrefs)
    assert normalized_gene.symbol == rps24p5.symbol
    assert normalized_gene.locations == rps24p5.locations
    assert normalized_gene.location_annotations == rps24p5.location_annotations


def test_trl_cag2_1(trl_cag2_1, hgnc):
    """Test that TRL-CAG2-1 gene normalizes to correct gene concept."""
    normalizer_response = hgnc.normalize('hgnc:34692')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == trl_cag2_1.label
    assert normalized_gene.concept_id == trl_cag2_1.concept_id
    assert set(normalized_gene.aliases) == set(trl_cag2_1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(trl_cag2_1.other_identifiers)
    assert normalized_gene.symbol_status == trl_cag2_1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(trl_cag2_1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(trl_cag2_1.xrefs)
    assert normalized_gene.symbol == trl_cag2_1.symbol
    assert normalized_gene.locations == trl_cag2_1.locations
    assert normalized_gene.location_annotations == \
           trl_cag2_1.location_annotations

    normalizer_response = hgnc.normalize('TRL-CAG2-1')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == trl_cag2_1.label
    assert normalized_gene.concept_id == trl_cag2_1.concept_id
    assert set(normalized_gene.aliases) == set(trl_cag2_1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(trl_cag2_1.other_identifiers)
    assert normalized_gene.symbol_status == trl_cag2_1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(trl_cag2_1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(trl_cag2_1.xrefs)
    assert normalized_gene.symbol == trl_cag2_1.symbol
    assert len(normalized_gene.locations) == len(trl_cag2_1.locations)
    for loc in trl_cag2_1.locations:
        assert loc in normalized_gene.locations
    assert normalized_gene.location_annotations == \
           trl_cag2_1.location_annotations


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
    assert normalizer_response['meta_'].genome_assemblies is None
    assert normalizer_response['meta_'].data_license_attributes == {
        "non_commercial": False,
        "share_alike": False,
        "attribution": False
    }
