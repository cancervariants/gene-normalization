"""Test that the gene normalizer works as intended for the Ensembl source."""
import pytest
from gene.schemas import Gene, MatchType
from gene.query import QueryHandler


@pytest.fixture(scope='module')
def ensembl():
    """Build ensembl test fixture."""
    class QueryGetter:
        def __init__(self):
            self.query_handler = QueryHandler()

        def search(self, query_str, incl='ensembl'):
            resp = self.query_handler.search_sources(query_str, keyed=True,
                                                     incl=incl)
            return resp['source_matches']['Ensembl']

    e = QueryGetter()
    return e


@pytest.fixture(scope='module')
def ddx11l1():
    """Create a DDX11L1 fixutre."""
    params = {
        'concept_id': 'ensembl:ENSG00000223972',
        'symbol': 'DDX11L1',
        'label': 'DEAD/H-box helicase 11 like 1 (pseudogene)',
        'previous_symbols': [],
        'aliases': [],
        'other_identifiers': ['hgnc:37102'],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.iTXYEeSmSj73q-lpxtKLlnp_1OlX658F',
                'interval': {
                    'end': 14409,
                    'start': 11869,
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:SQ.Ya6Rs7DHhDeg7YaOSg1EoNi3U_nQ9SvO',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '+',
        'xrefs': []
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def tp53():
    """Create a TP53 fixture."""
    params = {
        'concept_id': 'ensembl:ENSG00000141510',
        'symbol': 'TP53',
        'label': 'tumor protein p53',
        'previous_symbols': [],
        'aliases': [],
        'other_identifiers': ['hgnc:11998'],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.FfERYK71L10OLwk6QGoG8OPLgl7PItgK',
                'interval': {
                    'end': 7687538,
                    'start': 7661779,
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '-',
        'xrefs': []
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def u6():
    """Create a U6 test fixture."""
    params = {
        'concept_id': 'ensembl:ENSG00000278757',
        'symbol': 'U6',
        'label': 'U6 spliceosomal RNA',
        'previous_symbols': [],
        'aliases': [],
        'other_identifiers': [],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.7Gh2fIORi69Fm1UMai49Ek-6HQNzuyqv',
                'interval': {
                    'end': 516479,
                    'start': 516376,
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:SQ.Ya6Rs7DHhDeg7YaOSg1EoNi3U_nQ9SvO',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '-',
        'xrefs': ['rfam:RF00026']
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def CH17_340M24_3():
    """Create a CH17-340M24.3 test fixture."""
    params = {
        'concept_id': 'ensembl:ENSG00000197180',
        'symbol': 'CH17-340M24.3',
        'label': 'uncharacterized protein BC009467',
        'previous_symbols': [],
        'aliases': [],
        'other_identifiers': ['ncbigene:158960'],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.L5PJ5tioPr5ozAj1Ad0VIG-qHrGXnMUh',
                'interval': {
                    'end': 154428479,
                    'start': 154424380,
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:SQ.w0WZEvgJF0zf_P4yyTzjjv9oW1z61HHP',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '-',
        'xrefs': []
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def AC091057_5():
    """Create a AC091057.5 test fixture."""
    params = {
        'concept_id': 'ensembl:ENSG00000284906',
        'symbol': 'AC091057.5',
        'label': 'Rho GTPase-activating protein 11B',
        'previous_symbols': [],
        'aliases': [],
        'other_identifiers': [],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.UJx3xHRkDuoALaGxyic-cPQNQnXYiAM8',
                'interval': {
                    'end': 30685606,
                    'start': 30624548,
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:SQ.AsXvWL1-2i5U_buw6_niVIxD6zTbAuS6',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '+',
        'xrefs': ['uniprot:Q3KRB8']
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def hsa_mir_1253():
    """Create a AC091057.5 test fixture."""
    params = {
        'concept_id': 'ensembl:ENSG00000272920',
        'symbol': 'hsa-mir-1253',
        'label': 'hsa-mir-1253',
        'previous_symbols': [],
        'aliases': [],
        'other_identifiers': [],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.hS8fW7o0qqy15qOnQOKv1VqOZQDBswNI',
                'interval': {
                    'end': 2748182,
                    'start': 2748078,
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '+',
        'xrefs': ['mirbase:MI0006387']
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def spry3():
    """Create a SPRY3 test fixture."""
    params = {
        'concept_id': 'ensembl:ENSG00000168939',
        'symbol': 'SPRY3',
        'label': 'sprouty RTK signaling antagonist 3',
        'previous_symbols': [],
        'aliases': [],
        'other_identifiers': ['hgnc:11271'],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.h8YcFZq0v-Vwj6aGarOvh1R3LFNGD0YU',
                'interval': {
                    'end': 155782459,
                    'start': 155612572,
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:SQ.w0WZEvgJF0zf_P4yyTzjjv9oW1z61HHP',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '+',
        'xrefs': []
    }
    return Gene(**params)


@pytest.fixture(scope='module')
def bx004987_1():
    """Create a BX004987.1 test fixture."""
    params = {
        'concept_id': 'ensembl:ENSG00000278704',
        'symbol': 'BX004987.1',
        'label': None,
        'previous_symbols': [],
        'aliases': [],
        'other_identifiers': [],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.0JJsYiFwwNH2-7rYKj1ZitEcFRxIGwdQ',
                'interval': {
                    'end': 58376,
                    'start': 56140,
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:SQ.K_ieIfNIy1Ktulg8QSlhvJvm_1uQOtjD',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '-',
        'xrefs': []
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
    assert len(normalized_gene.locations) == len(test_gene.locations)
    for loc in test_gene.locations:
        assert loc in normalized_gene.locations
    assert set(normalized_gene.location_annotations) == \
           set(test_gene.location_annotations)
    assert normalized_gene.strand == test_gene.strand


def test_ddx11l1(ensembl, ddx11l1):
    """Test that DDX11L1 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = ensembl.search('ensembl:ENSG00000223972')
    assertion_checks(normalizer_response, ddx11l1, 1, MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSEMBL:ENSG00000223972')
    assertion_checks(normalizer_response, ddx11l1, 1, MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSG00000223972')
    assertion_checks(normalizer_response, ddx11l1, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = ensembl.search('ddx11l1')
    assertion_checks(normalizer_response, ddx11l1, 1, MatchType.SYMBOL)

    normalizer_response = ensembl.search('DDX11L1')
    assertion_checks(normalizer_response, ddx11l1, 1, MatchType.SYMBOL)


def test_tp53(ensembl, tp53):
    """Test that tp53 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = ensembl.search('ensembl:ENSG00000141510')
    assertion_checks(normalizer_response, tp53, 1, MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSEMBL:ENSG00000141510')
    assertion_checks(normalizer_response, tp53, 1, MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSG00000141510')
    assertion_checks(normalizer_response, tp53, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = ensembl.search('tp53')
    assertion_checks(normalizer_response, tp53, 1, MatchType.SYMBOL)

    normalizer_response = ensembl.search('TP53')
    assertion_checks(normalizer_response, tp53, 1, MatchType.SYMBOL)


def test_CH17_340M24_3(ensembl, CH17_340M24_3):
    """Test that CH17-340M24.3 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = ensembl.search('ensembl:ENSG00000197180')
    assertion_checks(normalizer_response, CH17_340M24_3, 1,
                     MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSEMBL:ENSG00000197180')
    assertion_checks(normalizer_response, CH17_340M24_3, 1,
                     MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSG00000197180')
    assertion_checks(normalizer_response, CH17_340M24_3, 1,
                     MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = ensembl.search('CH17-340M24.3')
    assertion_checks(normalizer_response, CH17_340M24_3, 1,
                     MatchType.SYMBOL)


def test_AC091057_5(ensembl, AC091057_5):
    """Test that AC091057.5 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = ensembl.search('ensembl:ENSG00000284906')
    assertion_checks(normalizer_response, AC091057_5, 1, MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSEMBL:ENSG00000284906')
    assertion_checks(normalizer_response, AC091057_5, 1, MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSG00000284906')
    assertion_checks(normalizer_response, AC091057_5, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = ensembl.search('AC091057.5')
    assertion_checks(normalizer_response, AC091057_5, 1, MatchType.SYMBOL)

    # Xref
    normalizer_response = ensembl.search('uniprot:Q3KRB8')
    assertion_checks(normalizer_response, AC091057_5, 1, MatchType.XREF)


def test_hsa_mir_1253(ensembl, hsa_mir_1253):
    """Test that hsa-mir-1253 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = ensembl.search('ensembl:ENSG00000272920')
    assertion_checks(normalizer_response, hsa_mir_1253, 1,
                     MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSEMBL:ENSG00000272920')
    assertion_checks(normalizer_response, hsa_mir_1253, 1,
                     MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSG00000272920')
    assertion_checks(normalizer_response, hsa_mir_1253, 1,
                     MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = ensembl.search('hsa-mir-1253')
    assertion_checks(normalizer_response, hsa_mir_1253, 1,
                     MatchType.SYMBOL)

    # Xref
    normalizer_response = ensembl.search('mirbase:MI0006387')
    assertion_checks(normalizer_response, hsa_mir_1253, 1,
                     MatchType.XREF)


def test_spry3(ensembl, spry3):
    """Test that spry3 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = ensembl.search('ensembl:EnSG00000168939')
    assertion_checks(normalizer_response, spry3, 1, MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSEMBL:EnSG00000168939')
    assertion_checks(normalizer_response, spry3, 1, MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('EnSG00000168939')
    assertion_checks(normalizer_response, spry3, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = ensembl.search('spry3')
    assertion_checks(normalizer_response, spry3, 1, MatchType.SYMBOL)


def test_bx004987_1(ensembl, bx004987_1):
    """Test that tp53 normalizes to correct gene concept."""
    # Concept ID
    normalizer_response = ensembl.search('ensembl:ENSG00000278704')
    assertion_checks(normalizer_response, bx004987_1, 1, MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSEMBL:ENSG00000278704')
    assertion_checks(normalizer_response, bx004987_1, 1, MatchType.CONCEPT_ID)

    normalizer_response = ensembl.search('ENSG00000278704')
    assertion_checks(normalizer_response, bx004987_1, 1, MatchType.CONCEPT_ID)

    # Symbol
    normalizer_response = ensembl.search('BX004987.1')
    assertion_checks(normalizer_response, bx004987_1, 1, MatchType.SYMBOL)


def test_no_match(ensembl):
    """Test that a term normalizes to correct gene concept as a NO match."""
    normalizer_response = ensembl.search('A1BG - AS1')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0

    normalizer_response = ensembl.search('hnc:5')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH

    # Test empty query
    normalizer_response = ensembl.search('')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0

    # Do not search on label
    normalizer_response = ensembl.search('A1BG antisense RNA 1')
    assert normalizer_response['match_type'] == MatchType.NO_MATCH
    assert len(normalizer_response['records']) == 0


def test_meta_info(ddx11l1, ensembl):
    """Test that the meta field is correct."""
    normalizer_response = ensembl.search('chromosome:1')
    assert normalizer_response['source_meta_'].data_license == 'custom'
    assert normalizer_response['source_meta_'].data_license_url ==\
           'https://useast.ensembl.org/info/about/legal/disclaimer.html'
    assert normalizer_response['source_meta_'].version == '102'
    assert normalizer_response['source_meta_'].data_url == \
           'ftp://ftp.ensembl.org/pub/'
    assert normalizer_response['source_meta_'].rdp_url is None
    assert normalizer_response['source_meta_'].genome_assemblies == ['GRCh38']
    assert normalizer_response['source_meta_'].data_license_attributes == {
        "non_commercial": False,
        "share_alike": False,
        "attribution": False
    }
