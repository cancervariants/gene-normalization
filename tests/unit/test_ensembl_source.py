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
        'label': 'DEAD/H-box helicase 11 like 1 (pseudogene)',
        'previous_symbols': [],
        'aliases': [],
        'other_identifiers': ['hgnc:37102'],
        'symbol_status': None,
        'location_annotations': [],
        'locations': [
            {
                'interval': {
                    'end': '14409',
                    'start': '11869',
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:VSL.tUaFuu4gZM0KH5h3EXTvhYi4ihJzPQF7',
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
                'interval': {
                    'end': '7687538',
                    'start': '7661779',
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:VSL.z7qUxIqvCPT73USOo1SVTRbrrqejT6JP',
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
                'interval': {
                    'end': '516479',
                    'start': '516376',
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:VSL.O2QimEWWS6bLrTqe6KAP--a5-muvksxz',
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
                'interval': {
                    'end': '154428479',
                    'start': '154424380',
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:VSL.U0lJ88JkUFNGdJ5BV8oCHy3DS453GtUO',
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
                'interval': {
                    'end': '30685606',
                    'start': '30624548',
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:VSL.An1MlwkqjP7Jjo8k4kgefV_Ecdm8aFFP',
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
                'interval': {
                    'end': '2748182',
                    'start': '2748078',
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:VSL.Or8qcAjmhzDybjczDhK1eB5c0LOwi4Jt',
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
                'interval': {
                    'end': '155782459',
                    'start': '155612572',
                    'type': 'SimpleInterval'
                },
                'sequence_id': 'ga4gh:VSL.hT8OEIdtXBZqH6kjGzol_MeDsISQ9Zyp',
                'type': 'SequenceLocation'
            }
        ],
        'strand': '+',
        'xrefs': []
    }
    return Gene(**params)


def test_concept_id_ddx11l1(ddx11l1, ensembl):
    """Test that ddx11l1 gene normalizes to correct gene concept
    as a CONCEPT_ID match.
    """
    normalizer_response = ensembl.normalize('ensembl:ENSG00000223972')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == ddx11l1.label
    assert normalized_gene.concept_id == ddx11l1.concept_id
    assert set(normalized_gene.aliases) == set(ddx11l1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_gene.symbol_status == ddx11l1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(ddx11l1.xrefs)
    assert normalized_gene.symbol == ddx11l1.symbol
    assert normalized_gene.strand == ddx11l1.strand
    assert normalized_gene.locations == ddx11l1.locations
    assert normalized_gene.location_annotations == ddx11l1.location_annotations

    normalizer_response = ensembl.normalize('ENSG00000223972')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == ddx11l1.label
    assert normalized_gene.concept_id == ddx11l1.concept_id
    assert set(normalized_gene.aliases) == set(ddx11l1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_gene.symbol_status == ddx11l1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(ddx11l1.xrefs)
    assert normalized_gene.symbol == ddx11l1.symbol
    assert normalized_gene.strand == ddx11l1.strand
    assert normalized_gene.locations == ddx11l1.locations
    assert normalized_gene.location_annotations == ddx11l1.location_annotations

    normalizer_response = ensembl.normalize('ENSEMBL:ENSG00000223972')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == ddx11l1.label
    assert normalized_gene.concept_id == ddx11l1.concept_id
    assert set(normalized_gene.aliases) == set(ddx11l1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_gene.symbol_status == ddx11l1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(ddx11l1.xrefs)
    assert normalized_gene.symbol == ddx11l1.symbol
    assert normalized_gene.strand == ddx11l1.strand
    assert normalized_gene.locations == ddx11l1.locations
    assert normalized_gene.location_annotations == ddx11l1.location_annotations


def test_ddx11l1_symbol(ddx11l1, ensembl):
    """Test that ddx11l1 gene normalizes to correct gene concept
    as an symbol match.
    """
    normalizer_response = ensembl.normalize('ddx11l1')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == ddx11l1.label
    assert normalized_gene.concept_id == ddx11l1.concept_id
    assert set(normalized_gene.aliases) == set(ddx11l1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_gene.symbol_status == ddx11l1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(ddx11l1.xrefs)
    assert normalized_gene.symbol == ddx11l1.symbol
    assert normalized_gene.strand == ddx11l1.strand
    assert normalized_gene.locations == ddx11l1.locations
    assert normalized_gene.location_annotations == ddx11l1.location_annotations

    normalizer_response = ensembl.normalize('DDX11L1')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == ddx11l1.label
    assert normalized_gene.concept_id == ddx11l1.concept_id
    assert set(normalized_gene.aliases) == set(ddx11l1.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(ddx11l1.other_identifiers)
    assert normalized_gene.symbol_status == ddx11l1.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(ddx11l1.previous_symbols)
    assert set(normalized_gene.xrefs) == set(ddx11l1.xrefs)
    assert normalized_gene.symbol == ddx11l1.symbol
    assert normalized_gene.strand == ddx11l1.strand
    assert normalized_gene.locations == ddx11l1.locations
    assert normalized_gene.location_annotations == ddx11l1.location_annotations


def test_concept_id_tp53(tp53, ensembl):
    """Test that tp53 gene normalizes to correct gene concept
    as a CONCEPT_ID match.
    """
    normalizer_response = ensembl.normalize('ENSG00000141510')
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
    assert normalized_gene.strand == tp53.strand
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations

    normalizer_response = ensembl.normalize('ensembl:ENSG00000141510')
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
    assert normalized_gene.strand == tp53.strand
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations

    normalizer_response = ensembl.normalize('ENSEMBL:ENSG00000141510')
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
    assert normalized_gene.strand == tp53.strand
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations


def test_tp53_symbol(tp53, ensembl):
    """Test that tp53 gene normalizes to correct gene concept
    as an symbol match.
    """
    normalizer_response = ensembl.normalize('tp53')
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
    assert normalized_gene.strand == tp53.strand
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations

    normalizer_response = ensembl.normalize('tp53')
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
    assert normalized_gene.strand == tp53.strand
    assert normalized_gene.locations == tp53.locations
    assert normalized_gene.location_annotations == tp53.location_annotations


def test_u6(u6, ensembl):
    """Test that U6 gene normalizes to correct gene concept."""
    normalizer_response = ensembl.normalize('ENSG00000278757')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == u6.label
    assert normalized_gene.concept_id == u6.concept_id
    assert set(normalized_gene.aliases) == set(u6.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(u6.other_identifiers)
    assert normalized_gene.symbol_status == u6.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(u6.previous_symbols)
    assert set(normalized_gene.xrefs) == set(u6.xrefs)
    assert normalized_gene.symbol == u6.symbol
    assert normalized_gene.strand == u6.strand
    assert normalized_gene.locations == u6.locations
    assert normalized_gene.location_annotations == u6.location_annotations

    normalizer_response = ensembl.normalize('U6')
    assert normalizer_response['match_type'] == MatchType.SYMBOL


def test_CH17_340M24_3(CH17_340M24_3, ensembl):
    """Test that CH17_340M24_3 gene normalizes to correct gene concept."""
    normalizer_response = ensembl.normalize('ENSG00000197180')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == CH17_340M24_3.label
    assert normalized_gene.concept_id == CH17_340M24_3.concept_id
    assert set(normalized_gene.aliases) == set(CH17_340M24_3.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(CH17_340M24_3.other_identifiers)
    assert normalized_gene.symbol_status == CH17_340M24_3.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(CH17_340M24_3.previous_symbols)
    assert set(normalized_gene.xrefs) == set(CH17_340M24_3.xrefs)
    assert normalized_gene.symbol == CH17_340M24_3.symbol
    assert normalized_gene.strand == CH17_340M24_3.strand
    assert normalized_gene.locations == CH17_340M24_3.locations
    assert normalized_gene.location_annotations == \
           CH17_340M24_3.location_annotations

    normalizer_response = ensembl.normalize('CH17-340M24.3')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == CH17_340M24_3.label
    assert normalized_gene.concept_id == CH17_340M24_3.concept_id
    assert set(normalized_gene.aliases) == set(CH17_340M24_3.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(CH17_340M24_3.other_identifiers)
    assert normalized_gene.symbol_status == CH17_340M24_3.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(CH17_340M24_3.previous_symbols)
    assert set(normalized_gene.xrefs) == set(CH17_340M24_3.xrefs)
    assert normalized_gene.symbol == CH17_340M24_3.symbol
    assert normalized_gene.strand == CH17_340M24_3.strand
    assert normalized_gene.locations == CH17_340M24_3.locations
    assert normalized_gene.location_annotations ==\
           CH17_340M24_3.location_annotations


def test_AC091057_5(AC091057_5, ensembl):
    """Test that AC091057_5 gene normalizes to correct gene concept."""
    normalizer_response = ensembl.normalize('ENSG00000284906')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == AC091057_5.label
    assert normalized_gene.concept_id == AC091057_5.concept_id
    assert set(normalized_gene.aliases) == set(AC091057_5.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(AC091057_5.other_identifiers)
    assert normalized_gene.symbol_status == AC091057_5.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(AC091057_5.previous_symbols)
    assert set(normalized_gene.xrefs) == set(AC091057_5.xrefs)
    assert normalized_gene.symbol == AC091057_5.symbol
    assert normalized_gene.strand == AC091057_5.strand
    assert normalized_gene.locations == AC091057_5.locations
    assert normalized_gene.location_annotations == \
           AC091057_5.location_annotations

    normalizer_response = ensembl.normalize('AC091057.5')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == AC091057_5.label
    assert normalized_gene.concept_id == AC091057_5.concept_id
    assert set(normalized_gene.aliases) == set(AC091057_5.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(AC091057_5.other_identifiers)
    assert normalized_gene.symbol_status == AC091057_5.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(AC091057_5.previous_symbols)
    assert set(normalized_gene.xrefs) == set(AC091057_5.xrefs)
    assert normalized_gene.symbol == AC091057_5.symbol
    assert normalized_gene.strand == AC091057_5.strand
    assert normalized_gene.locations == AC091057_5.locations
    assert normalized_gene.location_annotations ==\
           AC091057_5.location_annotations


def test_hsa_mir_1253(hsa_mir_1253, ensembl):
    """Test that hsa_mir_1253 gene normalizes to correct gene concept."""
    normalizer_response = ensembl.normalize('ENSG00000272920')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == hsa_mir_1253.label
    assert normalized_gene.concept_id == hsa_mir_1253.concept_id
    assert set(normalized_gene.aliases) == set(hsa_mir_1253.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(hsa_mir_1253.other_identifiers)
    assert normalized_gene.symbol_status == hsa_mir_1253.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(hsa_mir_1253.previous_symbols)
    assert set(normalized_gene.xrefs) == set(hsa_mir_1253.xrefs)
    assert normalized_gene.symbol == hsa_mir_1253.symbol
    assert normalized_gene.strand == hsa_mir_1253.strand
    assert normalized_gene.locations == hsa_mir_1253.locations
    assert normalized_gene.location_annotations == \
           hsa_mir_1253.location_annotations

    normalizer_response = ensembl.normalize('hsa-mir-1253')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == hsa_mir_1253.label
    assert normalized_gene.concept_id == hsa_mir_1253.concept_id
    assert set(normalized_gene.aliases) == set(hsa_mir_1253.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(hsa_mir_1253.other_identifiers)
    assert normalized_gene.symbol_status == hsa_mir_1253.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(hsa_mir_1253.previous_symbols)
    assert set(normalized_gene.xrefs) == set(hsa_mir_1253.xrefs)
    assert normalized_gene.symbol == hsa_mir_1253.symbol
    assert normalized_gene.strand == hsa_mir_1253.strand
    assert normalized_gene.locations == hsa_mir_1253.locations
    assert normalized_gene.location_annotations == \
           hsa_mir_1253.location_annotations


def test_spry3(spry3, ensembl):
    """Test that spry3 gene normalizes to correct gene concept."""
    normalizer_response = ensembl.normalize('EnSG00000168939')
    assert normalizer_response['match_type'] == MatchType.CONCEPT_ID
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == spry3.label
    assert normalized_gene.concept_id == spry3.concept_id
    assert set(normalized_gene.aliases) == set(spry3.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(spry3.other_identifiers)
    assert normalized_gene.symbol_status == spry3.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(spry3.previous_symbols)
    assert set(normalized_gene.xrefs) == set(spry3.xrefs)
    assert normalized_gene.symbol == spry3.symbol
    assert normalized_gene.strand == spry3.strand
    assert normalized_gene.locations == spry3.locations
    assert normalized_gene.location_annotations == spry3.location_annotations

    normalizer_response = ensembl.normalize('spry3')
    assert normalizer_response['match_type'] == MatchType.SYMBOL
    assert len(normalizer_response['records']) == 1
    normalized_gene = normalizer_response['records'][0]
    assert normalized_gene.label == spry3.label
    assert normalized_gene.concept_id == spry3.concept_id
    assert set(normalized_gene.aliases) == set(spry3.aliases)
    assert set(normalized_gene.other_identifiers) == \
           set(spry3.other_identifiers)
    assert normalized_gene.symbol_status == spry3.symbol_status
    assert set(normalized_gene.previous_symbols) == \
           set(spry3.previous_symbols)
    assert set(normalized_gene.xrefs) == set(spry3.xrefs)
    assert normalized_gene.symbol == spry3.symbol
    assert normalized_gene.strand == spry3.strand
    assert normalized_gene.locations == spry3.locations
    assert normalized_gene.location_annotations == spry3.location_annotations


def test_no_match(ensembl):
    """Test that a term normalizes to correct gene concept as a NO match."""
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
    assert normalizer_response['meta_'].data_license == 'custom'
    assert normalizer_response['meta_'].data_license_url ==\
           'https://useast.ensembl.org/info/about/legal/disclaimer.html'
    assert normalizer_response['meta_'].version == '102'
    assert normalizer_response['meta_'].data_url == \
           'ftp://ftp.ensembl.org/pub/'
    assert normalizer_response['meta_'].rdp_url is None
    assert normalizer_response['meta_'].genome_assemblies == ['GRCh38']
    assert normalizer_response['meta_'].data_license_attributes == {
        "non_commercial": False,
        "share_alike": False,
        "attribution": False
    }
