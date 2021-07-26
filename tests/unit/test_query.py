"""Module to test the query module."""
from gene.query import QueryHandler, InvalidParameterException
from gene.schemas import SourceName, MatchType
import pytest
from datetime import datetime


@pytest.fixture(scope='module')
def query_handler():
    """Build query_handler test fixture."""
    class QueryGetter:

        def __init__(self):
            self.query_handler = QueryHandler()

        def search(self, query_str, keyed=False, incl='', excl=''):
            return self.query_handler.search(query_str=query_str, keyed=keyed,
                                             incl=incl, excl=excl)

        def normalize(self, query_str):
            return self.query_handler.normalize(query_str)

    return QueryGetter()


@pytest.fixture(scope='module')
def normalized_braf():
    """Return normalized Gene Descriptor for BRAF."""
    return {
        "id": "normalize.gene:BRAF",
        "type": "GeneDescriptor",
        "value": {
            "id": "hgnc:1097",
            "type": "Gene"
        },
        "label": "BRAF",
        "xrefs": {
            "ensembl:ENSG00000157764",
            "ncbigene:673"
        },
        "alternate_labels": [
            "B-Raf proto-oncogene, serine/threonine kinase",
            "BRAF1",
            "RAFB1",
            "NS7",
            "B-RAF1",
            "B-raf"
        ],
        "extensions": [
            {
                "name": "symbol_status",
                "value": "approved",
                "type": "Extension"
            },
            {
                "name": "associated_with",
                "value": [
                    "vega:OTTHUMG00000157457",
                    "ucsc:uc003vwc.5",
                    "ccds:CCDS5863",
                    "ccds:CCDS87555",
                    "uniprot:P15056",
                    "pubmed:2284096",
                    "pubmed:1565476",
                    "cosmic:BRAF",
                    "omim:164757",
                    "orphanet:119066",
                    "iuphar:1943",
                    "ena.embl:M95712",
                    "refseq:NM_004333"
                ],
                "type": "Extension"
            },
            {
                "name": "chromosome_location",
                "value": {
                    "_id": "ga4gh:VCL.O6yCQ1cnThOrTfK9YUgMlTfM6HTqbrKw",
                    "type": "ChromosomeLocation",
                    "species_id": "taxonomy:9606",
                    "chr": "7",
                    "interval": {
                        "end": "q34",
                        "start": "q34",
                        "type": "CytobandInterval"
                    }
                },
                "type": "Extension"
            }
        ]
    }


@pytest.fixture(scope='module')
def num_sources():
    """Get the number of sources."""
    return len({s for s in SourceName})


def compare_gene_descriptor(test, actual):
    """Test that actual and expected gene descriptors match."""
    assert actual["id"] == test["id"]
    assert actual["type"] == test["type"]
    assert actual["value"] == test["value"]
    assert actual["label"] == test["label"]
    assert set(actual["xrefs"]) == set(test["xrefs"])
    assert set(actual["alternate_labels"]) == set(test["alternate_labels"])
    extensions_present = "extensions" in test.keys()
    assert ("extensions" in actual.keys()) == extensions_present
    if extensions_present:
        assert len(actual["extensions"]) == len(test["extensions"])
        for test_ext in test["extensions"]:
            for actual_ext in actual["extensions"]:
                if actual_ext["name"] == test_ext["name"]:
                    assert isinstance(actual_ext["value"],
                                      type(test_ext["value"]))
                    if isinstance(test_ext["value"], list):
                        assert set(actual_ext["value"]) == \
                               set(test_ext["value"])
                    else:
                        assert actual_ext["value"] == test_ext["value"]
                    assert actual_ext["type"] == test_ext["type"]


def test_search_query(query_handler, num_sources):
    """Test that query returns properly-structured response."""
    resp = query_handler.search(' BRAF ')
    assert resp['query'] == 'BRAF'
    matches = resp['source_matches']
    assert isinstance(matches, list)
    assert len(matches) == num_sources


def test_search_query_keyed(query_handler, num_sources):
    """Test that query returns properly-structured response."""
    resp = query_handler.search(' BRAF ', keyed=True)
    assert resp['query'] == 'BRAF'
    matches = resp['source_matches']
    assert isinstance(matches, dict)
    assert len(matches) == num_sources


def test_search_query_inc_exc(query_handler, num_sources):
    """Test that query incl and excl work correctly."""
    sources = "hgnc, ensembl, ncbi"
    resp = query_handler.search('BRAF', excl=sources)
    matches = resp['source_matches']
    assert len(matches) == num_sources - len(sources.split())

    sources = 'Hgnc, NCBi'
    resp = query_handler.search('BRAF', keyed=True, incl=sources)
    matches = resp['source_matches']
    assert len(matches) == len(sources.split())
    assert 'HGNC' in matches
    assert 'NCBI' in matches

    sources = 'HGnC'
    resp = query_handler.search('BRAF', keyed=True, excl=sources)
    matches = resp['source_matches']
    assert len(matches) == num_sources - len(sources.split())
    assert 'Ensembl' in matches
    assert 'NCBI' in matches


def test_search_invalid_parameter_exception(query_handler):
    """Test that Invalid parameter exception works correctly."""
    with pytest.raises(InvalidParameterException):
        resp = query_handler.search('BRAF', keyed=True, incl='hgn')  # noqa: F841, E501

    with pytest.raises(InvalidParameterException):
        resp = query_handler.search('BRAF', incl='hgnc', excl='hgnc')  # noqa: F841, E501


def test_ache_query(query_handler, num_sources):
    """Test that ACHE concept_id shows xref matches."""
    resp = query_handler.search('ncbigene:43', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.XREF
    assert matches['Ensembl']['match_type'] == MatchType.NO_MATCH
    assert matches['NCBI']['match_type'] == MatchType.CONCEPT_ID

    resp = query_handler.search('hgnc:108', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.CONCEPT_ID
    assert matches['Ensembl']['match_type'] == MatchType.XREF
    assert matches['NCBI']['match_type'] == MatchType.XREF

    resp = query_handler.search('ensembl:ENSG00000087085', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.XREF
    assert matches['Ensembl']['match_type'] == MatchType.CONCEPT_ID
    assert matches['NCBI']['match_type'] == MatchType.XREF


def test_braf_query(query_handler, num_sources, normalized_braf):
    """Test that BRAF concept_id shows xref matches."""
    # Search
    resp = query_handler.search('ncbigene:673', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.XREF
    assert matches['Ensembl']['match_type'] == MatchType.NO_MATCH
    assert matches['NCBI']['match_type'] == MatchType.CONCEPT_ID

    resp = query_handler.search('hgnc:1097', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.CONCEPT_ID
    assert matches['Ensembl']['match_type'] == MatchType.XREF
    assert matches['NCBI']['match_type'] == MatchType.XREF

    resp = query_handler.search('ensembl:ENSG00000157764', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.XREF
    assert matches['Ensembl']['match_type'] == MatchType.CONCEPT_ID
    assert matches['NCBI']['match_type'] == MatchType.XREF

    # Normalize
    resp = query_handler.normalize("BRAF")
    compare_gene_descriptor(normalized_braf, resp["gene_descriptor"])


def test_abl1_query(query_handler, num_sources):
    """Test that ABL1 concept_id shows xref matches."""
    resp = query_handler.search('ncbigene:25', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.XREF
    assert matches['Ensembl']['match_type'] == MatchType.NO_MATCH
    assert matches['NCBI']['match_type'] == MatchType.CONCEPT_ID

    resp = query_handler.search('hgnc:76', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.CONCEPT_ID
    assert matches['Ensembl']['match_type'] == MatchType.XREF
    assert matches['NCBI']['match_type'] == MatchType.XREF

    resp = query_handler.search('ensembl:ENSG00000097007', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.XREF
    assert matches['Ensembl']['match_type'] == MatchType.CONCEPT_ID
    assert matches['NCBI']['match_type'] == MatchType.XREF


def test_service_meta(query_handler):
    """Test service meta info in response."""
    test_query = "pheno"

    response = query_handler.search(test_query)
    service_meta = response['service_meta_']
    assert service_meta.name == "gene-normalizer"
    assert service_meta.version >= "0.1.0"
    assert isinstance(service_meta.response_datetime, datetime)
    assert service_meta.url == 'https://github.com/cancervariants/gene-normalization'  # noqa: E501
