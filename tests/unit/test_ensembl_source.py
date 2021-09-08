"""Test that the gene normalizer works as intended for the Ensembl source."""
import pytest
from gene.schemas import Gene, MatchType, SourceName
from gene.query import QueryHandler
from tests.conftest import assertion_checks


@pytest.fixture(scope='module')
def ensembl():
    """Build ensembl test fixture."""
    class QueryGetter:
        def __init__(self):
            self.query_handler = QueryHandler()

        def search(self, query_str, incl='ensembl'):
            resp = self.query_handler.search(query_str, keyed=True, incl=incl)
            return resp.source_matches[SourceName.ENSEMBL]

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
        'xrefs': ['hgnc:37102'],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.naD2_Q0JKCEKkGj8FvMzerePKnNNcF5N',
                'interval': {
                    'end': {'value': 14409, 'type': 'Number'},
                    'start': {'value': 11868, 'type': 'Number'},
                    'type': 'SequenceInterval'
                },
                'sequence_id': 'ga4gh:SQ.Ya6Rs7DHhDeg7YaOSg1EoNi3U_nQ9SvO',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '+',
        'associated_with': []
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
        'xrefs': ['hgnc:11998'],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.7q-vAjxSYARaPbbUjhDng2oay795NfbE',
                'interval': {
                    'end': {'value': 7687538, 'type': 'Number'},
                    'start': {'value': 7661778, 'type': 'Number'},
                    'type': 'SequenceInterval'
                },
                'sequence_id': 'ga4gh:SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '-',
        'associated_with': []
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
        'xrefs': [],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.mtPBK609IiOFy0gztyTnEGdWM_k_e85C',
                'interval': {
                    'end': {'value': 516479, 'type': 'Number'},
                    'start': {'value': 516375, 'type': 'Number'},
                    'type': 'SequenceInterval'
                },
                'sequence_id': 'ga4gh:SQ.Ya6Rs7DHhDeg7YaOSg1EoNi3U_nQ9SvO',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '-',
        'associated_with': ['rfam:RF00026']
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
        'xrefs': ['ncbigene:158960'],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.EJaq2KK3bIftDcyP1YAmJLb08JbBAmAn',
                'interval': {
                    'end': {'value': 154428479, 'type': 'Number'},
                    'start': {'value': 154424379, 'type': 'Number'},
                    'type': 'SequenceInterval'
                },
                'sequence_id': 'ga4gh:SQ.w0WZEvgJF0zf_P4yyTzjjv9oW1z61HHP',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '-',
        'associated_with': []
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
        'xrefs': [],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.sZGLn8Ah76rP34pu8-7W73lkCwQ7XSJD',
                'interval': {
                    'end': {'value': 30685606, 'type': 'Number'},
                    'start': {'value': 30624547, 'type': 'Number'},
                    'type': 'SequenceInterval'
                },
                'sequence_id': 'ga4gh:SQ.AsXvWL1-2i5U_buw6_niVIxD6zTbAuS6',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '+',
        'associated_with': ['uniprot:Q3KRB8']
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
        'xrefs': [],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.goBvYPYef2mQildG6AiiRNVhTo-g4-1E',
                'interval': {
                    'end': {'value': 2748182, 'type': 'Number'},
                    'start': {'value': 2748077, 'type': 'Number'},
                    'type': 'SequenceInterval'
                },
                'sequence_id': 'ga4gh:SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '+',
        'associated_with': ['mirbase:MI0006387']
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
        'xrefs': ['hgnc:11271'],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                '_id': 'ga4gh:VSL.7Jax3UNlW_EZrZ44U-R1eLe_OeCC71IR',
                'interval': {
                    'end': {'value': 155782459, 'type': 'Number'},
                    'start': {'value': 155612571, 'type': 'Number'},
                    'type': 'SequenceInterval'
                },
                'sequence_id': 'ga4gh:SQ.w0WZEvgJF0zf_P4yyTzjjv9oW1z61HHP',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '+',
        'associated_with': []
    }
    return Gene(**params)


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

    # associated_with
    normalizer_response = ensembl.search('mirbase:MI0006387')
    assertion_checks(normalizer_response, hsa_mir_1253, 1,
                     MatchType.ASSOCIATED_WITH)


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


def test_no_match(ensembl):
    """Test that a term normalizes to correct gene concept as a NO match."""
    normalizer_response = ensembl.search('A1BG - AS1')
    assert normalizer_response.match_type == MatchType.NO_MATCH
    assert len(normalizer_response.records) == 0

    normalizer_response = ensembl.search('hnc:5')
    assert normalizer_response.match_type == MatchType.NO_MATCH

    # Test empty query
    normalizer_response = ensembl.search('')
    assert normalizer_response.match_type == MatchType.NO_MATCH
    assert len(normalizer_response.records) == 0

    # Do not search on label
    normalizer_response = ensembl.search('A1BG antisense RNA 1')
    assert normalizer_response.match_type == MatchType.NO_MATCH
    assert len(normalizer_response.records) == 0

    normalizer_response = ensembl.search('ensembl:ENSG00000278704')
    assert normalizer_response.match_type == MatchType.NO_MATCH
    assert len(normalizer_response.records) == 0

    normalizer_response = ensembl.search('ensembl:ENSG00000284906')
    assert normalizer_response.match_type == MatchType.NO_MATCH
    assert len(normalizer_response.records) == 0.


def test_meta_info(ddx11l1, ensembl):
    """Test that the meta field is correct."""
    normalizer_response = ensembl.search('chromosome:1')
    assert normalizer_response.source_meta_.data_license == 'custom'
    assert normalizer_response.source_meta_.data_license_url ==\
           'https://useast.ensembl.org/info/about/legal/disclaimer.html'
    assert normalizer_response.source_meta_.version == '104'
    assert normalizer_response.source_meta_.data_url == \
           'ftp://ftp.ensembl.org/pub/Homo_sapiens.GRCh38.104.gff3.gz'
    assert normalizer_response.source_meta_.rdp_url is None
    assert normalizer_response.source_meta_.genome_assemblies == ['GRCh38']
    assert normalizer_response.source_meta_.data_license_attributes == {
        "non_commercial": False,
        "share_alike": False,
        "attribution": False
    }
