"""Test that the gene normalizer works as intended for the HGNC source."""
import pytest
from gene.schemas import Gene, MatchType
from gene.query import QueryHandler
from datetime import datetime


@pytest.fixture(scope='module')
def hgnc():
    """Build hgnc test fixture."""
    class QueryGetter:
        def __init__(self):
            self.query_handler = QueryHandler()

        def search(self, query_str, incl='hgnc'):
            resp = self.query_handler.search_sources(query_str, keyed=True,
                                                     incl=incl)
            return resp['source_matches']['HGNC']

    h = QueryGetter()
    return h


# Test Non Alt Loci Set


@pytest.fixture(scope='module')
def a1bg_as1():
    """Create an A1BG-AS1 gene fixture."""
    params = {
        'label': 'A1BG antisense RNA 1',
        'concept_id': 'hgnc:37133',
        'symbol': 'A1BG-AS1',
        'location_annotations': [],
        'strand': None,
        'locations': [
            {
                '_id': 'ga4gh:VCL.3Zdz1Stgx8HdWf1cT1KaUHFUQjoKTTcD',
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
        'location_annotations': [],
        'strand': None,
        'locations': [
            {
                '_id': 'ga4gh:VCL._Cl_XG2bfBUVG6uwi-jHtCHavOAyfPXN',
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
        'location_annotations': [],
        'strand': None,
        'locations': [
            {
                '_id': 'ga4gh:VCL.Rs8bogwClWoTYjhY9vI9J3wnPEXlao-U',
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
        'location_annotations': [],
        'strand': None,
        'locations': [
            {
                '_id': 'ga4gh:VCL.R_izmPbRVtPQ2HwflIVh1XLXvRtVi-a7',
                'chr': '14',
                'interval': {
                    'end': 'q22.2',
                    'start': 'q22.3',
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
        'location_annotations': [
            'reserved'
        ],
        'locations': [],
        'strand': None,
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
        'location_annotations': [
            '6'
        ],
        'locations': [],
        'strand': None,
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
        'location_annotations': [
            'not on reference assembly'
        ],
        'strand': None,
        'locations': [
            {
                '_id': 'ga4gh:VCL.AlwtARlUTZiNX3NEEKab-X5eeayXd8v8',
                'chr': 'X',
                'interval': {
                    'end': 'p11.2',
                    'start': 'p11.4',
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
        'location_annotations': ['unplaced', '14'],
        'locations': [],
        'strand': None,
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
        'location_annotations': ['MT'],
        'locations': [],
        'strand': None,
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
        'location_annotations': [],
        'strand': None,
        'locations': [
            {
                '_id': 'ga4gh:VCL.-hT6Cp6B32GmZTD8BXh1xf6SJeLM1uN7',
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
        'location_annotations': [],
        'strand': None,
        'locations': [
            {
                '_id': 'ga4gh:VCL.B5KOWxL8BQRpM2MOHP-RUmGlmm4ZtMAC',
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
                '_id': 'ga4gh:VCL.QzbpRniVtZz8V-7B7vKhGeX3A3huKacK',
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
        'location_annotations': [],
        'strand': None,
        'locations': [
            {
                '_id': 'ga4gh:VCL.dLLTOKtFTnVd3ope5gTii1Gbdj7FxSfa',
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
        'location_annotations': [],
        'strand': None,
        'locations': [
            {
                '_id': 'ga4gh:VCL.r_iXu-FjXuJjmeNhmDEputf6tgjXRQIr',
                'chr': '16',
                'interval': {
                    'end': 'q13',
                    'start': 'q21',
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


@pytest.fixture(scope='module')
def myo5b():
    """Create a MYO5B gene fixture."""
    params = {
        'label': 'myosin VB',
        'concept_id': 'hgnc:7603',
        'symbol': 'MYO5B',
        'location_annotations': [],
        'strand': None,
        'locations': [
            {
                '_id': 'ga4gh:VCL.1vd9qlPiSSaDZC5X4jIKpapokxvKrITd',
                'chr': '18',
                'interval': {
                    'end': 'qter',
                    'start': 'cen',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ],
        'previous_symbols': [],
        'aliases': [
            'KIAA1119'
        ],
        'symbol_status': 'approved',
        'other_identifiers': [
            'ensembl:ENSG00000167306',
            'ncbigene:4645'
        ],
        'xrefs': [
            'vega:OTTHUMG00000179843',
            'refseq:NM_001080467',
            'omim:606540',
            'ucsc:uc002leb.3',
            'uniprot:Q9ULV0',
            'orphanet:171089',
            'ccds:CCDS42436',
            'ena.embl:AB032945',
            'pubmed:8884266',
            'pubmed:17462998'
        ]
    }
    return Gene(**params)


# Test Alt Loci Set


@pytest.fixture(scope='module')
def gstt1():
    """Create an GSTT1 gene fixture."""
    params = {
        'label': 'glutathione S-transferase theta 1',
        'concept_id': 'hgnc:4641',
        'symbol': 'GSTT1',
        'location_annotations': ['alternate reference locus'],
        'strand': None,
        'locations': [
            {
                '_id': 'ga4gh:VCL.EfA-UFrmtjncDxutoiP6PWxu32UtH1Zu',
                'chr': '22',
                'interval': {
                    'end': 'q11.23',
                    'start': 'q11.23',
                    'type': 'CytobandInterval'
                },
                'species_id': 'taxonomy:9606',
                'type': 'ChromosomeLocation'
            }
        ],
        'previous_symbols': [],
        'aliases': ['2.5.1.18'],
        'symbol_status': 'approved',
        'xrefs': [
            'refseq:NM_000853',
            'omim:600436',
            'ucsc:uc002zze.4',
            'uniprot:P30711',
            'orphanet:470418',
            'ena.embl:KI270879',
            'pubmed:8617495'
        ],
        'other_identifiers': [
            'ensembl:ENSG00000277656',
            'ncbigene:2952'
        ]
    }
    return Gene(**params)


def assertion_checks(normalizer_response, test_gene, n_records, match_type):
    """Check that normalizer_response and test_gene are the same."""
    assert normalizer_response['match_type'] == match_type
    assert len(normalizer_response['records']) == n_records
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == test_gene.label
    assert normalized_gene.concept_id == test_gene.concept_id
    assert set(normalized_gene.aliases) == set(test_gene.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(test_gene.other_identifiers)
    assert normalized_gene.symbol_status == test_gene.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(test_gene.previous_symbols)
    assert set(normalized_gene.xrefs) == set(test_gene.xrefs)
    assert normalized_gene.symbol == test_gene.symbol
    assert normalized_gene.locations == test_gene.locations
    assert set(normalized_gene.location_annotations) == \
           set(test_gene.location_annotations)
    assert normalized_gene.strand == test_gene.strand


def test_a1bg_as1(a1bg_as1, hgnc):
    """Test that a1bg_as1 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:37133')
    assertion_checks(normalizer_response, a1bg_as1, 1, MatchType.CONCEPT_ID)

    normalizer_response = hgnc.search('HGNC:37133')
    assertion_checks(normalizer_response, a1bg_as1, 1, MatchType.CONCEPT_ID)

    normalizer_response = hgnc.search('Hgnc:37133')
    assertion_checks(normalizer_response, a1bg_as1, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('A1BG-AS1')
    assertion_checks(normalizer_response, a1bg_as1, 1, MatchType.SYMBOL)

    normalizer_response = hgnc.search('A1BG-as1')
    assertion_checks(normalizer_response, a1bg_as1, 1, MatchType.SYMBOL)

    # Previous Symbol
    normalizer_response = hgnc.search('NCRNA00181')
    assertion_checks(normalizer_response, a1bg_as1, 1, MatchType.PREV_SYMBOL)

    normalizer_response = hgnc.search('A1BGAS')
    assertion_checks(normalizer_response, a1bg_as1, 1, MatchType.PREV_SYMBOL)

    normalizer_response = hgnc.search('A1BG-AS')
    assertion_checks(normalizer_response, a1bg_as1, 1, MatchType.PREV_SYMBOL)

    # Alias
    normalizer_response = hgnc.search('FLJ23569')
    assertion_checks(normalizer_response, a1bg_as1, 1, MatchType.ALIAS)

    normalizer_response = hgnc.search('flj23569')
    assertion_checks(normalizer_response, a1bg_as1, 1, MatchType.ALIAS)


def test_a3galt2(a3galt2, hgnc):
    """Test that a3galt2 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:30005')
    assertion_checks(normalizer_response, a3galt2, 1, MatchType.CONCEPT_ID)

    normalizer_response = hgnc.search('HGNC:30005')
    assertion_checks(normalizer_response, a3galt2, 1, MatchType.CONCEPT_ID)

    normalizer_response = hgnc.search('Hgnc:30005')
    assertion_checks(normalizer_response, a3galt2, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('A3GALT2')
    assertion_checks(normalizer_response, a3galt2, 1, MatchType.SYMBOL)

    normalizer_response = hgnc.search('a3galt2')
    assertion_checks(normalizer_response, a3galt2, 1, MatchType.SYMBOL)

    # Previous Symbol
    normalizer_response = hgnc.search('A3GALT2P')
    assertion_checks(normalizer_response, a3galt2, 1, MatchType.PREV_SYMBOL)

    normalizer_response = hgnc.search('A3GALT2p')
    assertion_checks(normalizer_response, a3galt2, 1, MatchType.PREV_SYMBOL)

    # Alias
    normalizer_response = hgnc.search('IGBS3S')
    assertion_checks(normalizer_response, a3galt2, 1, MatchType.ALIAS)

    normalizer_response = hgnc.search('igB3s')
    assertion_checks(normalizer_response, a3galt2, 1, MatchType.ALIAS)


def test_tp53(tp53, hgnc):
    """Test that tp53 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:11998')
    assertion_checks(normalizer_response, tp53, 1, MatchType.CONCEPT_ID)

    normalizer_response = hgnc.search('HGNC:11998')
    assertion_checks(normalizer_response, tp53, 1, MatchType.CONCEPT_ID)

    normalizer_response = hgnc.search('Hgnc:11998')
    assertion_checks(normalizer_response, tp53, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('tp53')
    assertion_checks(normalizer_response, tp53, 1, MatchType.SYMBOL)

    normalizer_response = hgnc.search('TP53')
    assertion_checks(normalizer_response, tp53, 1, MatchType.SYMBOL)

    # Alias
    normalizer_response = hgnc.search('LFS1')
    assertion_checks(normalizer_response, tp53, 1, MatchType.ALIAS)

    normalizer_response = hgnc.search('p53')
    assertion_checks(normalizer_response, tp53, 1, MatchType.ALIAS)


def test_wdhd1(wdhd1, hgnc):
    """Test that a1bg_as1 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:23170')
    assertion_checks(normalizer_response, wdhd1, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('WDHD1')
    assertion_checks(normalizer_response, wdhd1, 1, MatchType.SYMBOL)


def test_g6pr(g6pr, hgnc):
    """Test that g6pr normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:4059')
    assertion_checks(normalizer_response, g6pr, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('G6PR')
    assertion_checks(normalizer_response, g6pr, 1, MatchType.SYMBOL)


def test_pirc24(pirc24, hgnc):
    """Test that pirc24 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:37528')
    assertion_checks(normalizer_response, pirc24, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('PIRC24')
    assertion_checks(normalizer_response, pirc24, 1, MatchType.SYMBOL)


def test_gage4(gage4, hgnc):
    """Test that gage4 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:4101')
    assertion_checks(normalizer_response, gage4, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('GAGE4')
    assertion_checks(normalizer_response, gage4, 1, MatchType.SYMBOL)


def test_mafip(mafip, hgnc):
    """Test that mafip normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:31102')
    assertion_checks(normalizer_response, mafip, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('MAFIP')
    assertion_checks(normalizer_response, mafip, 1, MatchType.SYMBOL)


def test_mt_7sdna(mt_7sdna, hgnc):
    """Test that mt_7sdna normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:7409')
    assertion_checks(normalizer_response, mt_7sdna, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('MT-7SDNA')
    assertion_checks(normalizer_response, mt_7sdna, 1, MatchType.SYMBOL)


def test_cecr(cecr, hgnc):
    """Test that cecr normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:1838')
    assertion_checks(normalizer_response, cecr, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('CECR')
    assertion_checks(normalizer_response, cecr, 1, MatchType.SYMBOL)


def test_csf2ra(csf2ra, hgnc):
    """Test that csf2ra normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:2435')
    assertion_checks(normalizer_response, csf2ra, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('CSF2RA')
    assertion_checks(normalizer_response, csf2ra, 1, MatchType.SYMBOL)


def test_rps24p5(rps24p5, hgnc):
    """Test that rps24p5 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:36026')
    assertion_checks(normalizer_response, rps24p5, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('rpS24P5')
    assertion_checks(normalizer_response, rps24p5, 1, MatchType.SYMBOL)


def test_trl_cag2_1(trl_cag2_1, hgnc):
    """Test that trl_cag2_1 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:34692')
    assertion_checks(normalizer_response, trl_cag2_1, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('TRL-CAG2-1')
    assertion_checks(normalizer_response, trl_cag2_1, 1, MatchType.SYMBOL)


def test_myo5b(myo5b, hgnc):
    """Test that myo5b normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:7603')
    assertion_checks(normalizer_response, myo5b, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('MYO5B')
    assertion_checks(normalizer_response, myo5b, 1, MatchType.SYMBOL)

    # Xref
    normalizer_response = hgnc.search('refseq:NM_001080467')
    assertion_checks(normalizer_response, myo5b, 1, MatchType.XREF)


def test_gstt1(gstt1, hgnc):
    """Test that gstt1 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = hgnc.search('hgnc:4641')
    assertion_checks(normalizer_response, gstt1, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = hgnc.search('GSTT1')
    assertion_checks(normalizer_response, gstt1, 1, MatchType.SYMBOL)

    # Xref
    normalizer_response = hgnc.search('omim:600436')
    assertion_checks(normalizer_response, gstt1, 1, MatchType.XREF)


def test_no_match(hgnc):
    """Test that a term normalizes to correct gene concept as a NO match."""
    normalizer_response = hgnc.search('A1BG - AS1')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0

    normalizer_response = hgnc.search('hnc:5')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH

    # Test empty query
    normalizer_response = hgnc.search('')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0

    # Do not search on label
    normalizer_response = hgnc.search('A1BG antisense RNA 1')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0


def test_meta_info(a1bg_as1, hgnc):
    """Test that the meta field is correct."""
    normalizer_response = hgnc.search('HGNC:37133')
    assert normalizer_response['source_meta_'].data_license == 'custom'
    assert normalizer_response['source_meta_'].data_license_url == \
           'https://www.genenames.org/about/'
    assert datetime.strptime(normalizer_response['source_meta_'].version, "%Y%m%d")  # noqa: E501
    assert normalizer_response['source_meta_'].data_url == \
           'ftp://ftp.ebi.ac.uk/pub/databases/genenames/hgnc/'
    assert normalizer_response['source_meta_'].rdp_url is None
    assert normalizer_response['source_meta_'].genome_assemblies == []
    assert normalizer_response['source_meta_'].data_license_attributes == {
        "non_commercial": False,
        "share_alike": False,
        "attribution": False
    }
