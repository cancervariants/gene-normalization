"""Module to test the query module."""
from gene.query import QueryHandler, InvalidParameterException
from gene.schemas import SourceName, MatchType
import copy
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
def normalized_ache():
    """Return normalized Gene Descriptor for ACHE."""
    return {
        "id": "normalize.gene:ACHE",
        "type": "GeneDescriptor",
        "value": {
            "id": "hgnc:108",
            "type": "Gene"
        },
        "label": "ACHE",
        "xrefs": {
            "ensembl:ENSG00000087085",
            "ncbigene:43"
        },
        "alternate_labels": [
            "3.1.1.7",
            "YT",
            "N-ACHE",
            "ARACHE",
            "ACEE"
        ],
        "extensions": [
            {
                "name": "approved_name",
                "value": "acetylcholinesterase (Cartwright blood group)",
                "type": "Extension"
            },
            {
                "name": "symbol_status",
                "value": "approved",
                "type": "Extension"
            },
            {
                "name": "associated_with",
                "value": [
                    "vega:OTTHUMG00000157033",
                    "ucsc:uc003uxi.4",
                    "ccds:CCDS5710",
                    "ccds:CCDS64736",
                    "ccds:CCDS5709",
                    "uniprot:P22303",
                    "pubmed:1380483",
                    "omim:100740",
                    "merops:S09.979",
                    "iuphar:2465",
                    "refseq:NM_015831"
                ],
                "type": "Extension"
            },
            {
                "name": "chromosome_location",
                "value": {
                    "_id": "ga4gh:VCL.VtdU_0lYXL_o95lXRUfhv-NDJVVpmKoD",
                    "type": "ChromosomeLocation",
                    "species_id": "taxonomy:9606",
                    "chr": "7",
                    "interval": {
                        "end": "q22.1",
                        "start": "q22.1",
                        "type": "CytobandInterval"
                    }
                },
                "type": "Extension"
            }
        ]
    }


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
            "BRAF1",
            "RAFB1",
            "NS7",
            "B-RAF1",
            "B-raf"
        ],
        "extensions": [
            {
                "name": "approved_name",
                "value": "B-Raf proto-oncogene, serine/threonine kinase",
                "type": "Extension"
            },
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
def normalized_abl1():
    """Return normalized Gene Descriptor for ABL1."""
    return {
        "id": "normalize.gene:ABL1",
        "type": "GeneDescriptor",
        "value": {
            "id": "hgnc:76",
            "type": "Gene"
        },
        "label": "ABL1",
        "xrefs": {
            "ensembl:ENSG00000097007",
            "ncbigene:25"
        },
        "alternate_labels": [
            "c-ABL",
            "JTK7",
            "p150",
            "CHDSKM",
            "BCR-ABL",
            "v-abl",
            "c-ABL1",
            "bcr/abl",
            "LOC116063",
            "LOC112779",
            "ABL"
        ],
        "extensions": [
            {
                "name": "approved_name",
                "value": "ABL proto-oncogene 1, non-receptor tyrosine kinase",
                "type": "Extension"
            },
            {
                "name": "symbol_status",
                "value": "approved",
                "type": "Extension"
            },
            {
                "name": "associated_with",
                "value": [
                    "vega:OTTHUMG00000020813",
                    "ucsc:uc004bzv.4",
                    "ccds:CCDS35166",
                    "ccds:CCDS35165",
                    "uniprot:P00519",
                    "pubmed:1857987",
                    "pubmed:12626632",
                    "cosmic:ABL1",
                    "omim:189980",
                    "orphanet:117691",
                    "iuphar:1923",
                    "ena.embl:M14752",
                    "refseq:NM_007313"
                ],
                "type": "Extension"
            },
            {
                "name": "chromosome_location",
                "value": {
                    "_id": "ga4gh:VCL.WvMfE67KxSDAV8JaK593TI74yyJWIsMQ",
                    "type": "ChromosomeLocation",
                    "species_id": "taxonomy:9606",
                    "chr": "9",
                    "interval": {
                        "end": "q34.12",
                        "start": "q34.12",
                        "type": "CytobandInterval"
                    }
                },
                "type": "Extension"
            }
        ]
    }


@pytest.fixture(scope='module')
def normalized_p150():
    """Return normalized Gene Descriptor for p150."""
    return {
        "id": "normalize.gene:P150",
        "type": "GeneDescriptor",
        "value": {
            "id": "hgnc:1910",
            "type": "Gene"
        },
        "label": "CHAF1A",
        "xrefs": {
            "ensembl:ENSG00000167670",
            "ncbigene:10036"
        },
        "alternate_labels": [
            "CAF1P150",
            "MGC71229",
            "CAF-1",
            "P150",
            "CAF1B",
            "CAF1"
        ],
        "extensions": [
            {
                "name": "approved_name",
                "value": "chromatin assembly factor 1 subunit A",
                "type": "Extension"
            },
            {
                "name": "symbol_status",
                "value": "approved",
                "type": "Extension"
            },
            {
                "name": "associated_with",
                "value": [
                    "omim:601246",
                    "ccds:CCDS32875",
                    "pubmed:7600578",
                    "vega:OTTHUMG00000181922",
                    "uniprot:Q13111",
                    "refseq:NM_005483",
                    "ena.embl:U20979",
                    "ucsc:uc002mal.4"
                ],
                "type": "Extension"
            },
            {
                "name": "chromosome_location",
                "value": {
                    "_id": "ga4gh:VCL.yF2TzeunqY92v3yhDsCR_t5X997mWriF",
                    "type": "ChromosomeLocation",
                    "species_id": "taxonomy:9606",
                    "chr": "19",
                    "interval": {
                        "end": "p13.3",
                        "start": "p13.3",
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


def compare_normalize_resp(resp, expected_query, expected_match_type,
                           expected_gene_descriptor, expected_warnings=None,
                           expected_source_meta=None):
    """Check that normalize response is correct"""
    assert resp["query"] == expected_query
    if expected_warnings:
        assert len(resp["warnings"]) == len(expected_warnings), "warnings len"
        for e_warnings in expected_warnings:
            for r_warnings in resp["warnings"]:
                for e_key, e_val in e_warnings.items():
                    for r_key, r_val in r_warnings.items():
                        if e_key == r_val:
                            if isinstance(e_val, list):
                                assert set(r_val) == set(e_val), "warnings val"
                            else:
                                assert r_val == e_val, "warnings val"
    else:
        assert resp["warnings"] == [], "warnings != []"
    assert resp["match_type"] == expected_match_type
    compare_gene_descriptor(expected_gene_descriptor, resp["gene_descriptor"])
    if not expected_source_meta:
        assert resp["source_meta_"] == {}
    else:
        resp_source_meta_keys = resp["source_meta_"].keys()
        assert len(resp_source_meta_keys) == len(expected_source_meta),\
            "source_meta_keys"
        for src in expected_source_meta:
            assert src in resp_source_meta_keys
    compare_service_meta(resp["service_meta_"])


def compare_service_meta(service_meta):
    """Check that service metadata is correct."""
    assert service_meta.name == "gene-normalizer"
    assert service_meta.version >= "0.1.0"
    assert isinstance(service_meta.response_datetime, datetime)
    assert service_meta.url == \
           'https://github.com/cancervariants/gene-normalization'


def compare_gene_descriptor(test, actual):
    """Test that actual and expected gene descriptors match."""
    assert actual["id"] == test["id"]
    assert actual["type"] == test["type"]
    assert actual["value"] == test["value"]
    assert actual["label"] == test["label"]
    assert set(actual["xrefs"]) == set(test["xrefs"]), "xrefs"
    assert set(actual["alternate_labels"]) == set(test["alternate_labels"]), \
        "alt labels"
    extensions_present = "extensions" in test.keys()
    assert ("extensions" in actual.keys()) == extensions_present
    if extensions_present:
        assert len(actual["extensions"]) == len(test["extensions"]), \
            "len of extensions"
        for test_ext in test["extensions"]:
            for actual_ext in actual["extensions"]:
                if actual_ext["name"] == test_ext["name"]:
                    assert isinstance(actual_ext["value"],
                                      type(test_ext["value"]))
                    if isinstance(test_ext["value"], list):
                        assert set(actual_ext["value"]) == \
                               set(test_ext["value"]), f"{test_ext['value']} value"  # noqa: E501
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


def test_ache_query(query_handler, num_sources, normalized_ache):
    """Test that ACHE concept_id shows xref matches."""
    # Search
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

    # Normalize
    q = "ACHE"
    expected_source_meta = ["HGNC", "Ensembl", "NCBI"]
    resp = query_handler.normalize(q)
    compare_normalize_resp(resp, q, MatchType.SYMBOL, normalized_ache,
                           expected_source_meta=expected_source_meta)

    q = "ache"
    resp = query_handler.normalize(q)
    cpy_normalized_ache = copy.deepcopy(normalized_ache)
    cpy_normalized_ache["id"] = "normalize.gene:ache"
    compare_normalize_resp(resp, q, MatchType.SYMBOL, cpy_normalized_ache,
                           expected_source_meta=expected_source_meta)

    q = "hgnc:108"
    resp = query_handler.normalize(q)
    cpy_normalized_ache["id"] = "normalize.gene:hgnc%3A108"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_ache,
                           expected_source_meta=expected_source_meta)

    q = "ensembl:ENSG00000087085"
    resp = query_handler.normalize(q)
    cpy_normalized_ache["id"] = "normalize.gene:ensembl%3AENSG00000087085"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_ache,
                           expected_source_meta=expected_source_meta)

    q = "ncbigene:43"
    resp = query_handler.normalize(q)
    cpy_normalized_ache["id"] = "normalize.gene:ncbigene%3A43"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_ache,
                           expected_source_meta=expected_source_meta)

    q = "3.1.1.7"
    resp = query_handler.normalize(q)
    cpy_normalized_ache["id"] = "normalize.gene:3.1.1.7"
    compare_normalize_resp(resp, q, MatchType.ALIAS, cpy_normalized_ache,
                           expected_source_meta=expected_source_meta)

    q = "ARACHE"
    resp = query_handler.normalize(q)
    cpy_normalized_ache["id"] = "normalize.gene:ARACHE"
    compare_normalize_resp(resp, q, MatchType.ALIAS, cpy_normalized_ache,
                           expected_source_meta=expected_source_meta)

    q = "YT"
    resp = query_handler.normalize(q)
    cpy_normalized_ache["id"] = "normalize.gene:YT"
    compare_normalize_resp(resp, q, MatchType.PREV_SYMBOL, cpy_normalized_ache,
                           expected_source_meta=expected_source_meta)

    q = "omim:100740"
    resp = query_handler.normalize(q)
    cpy_normalized_ache["id"] = "normalize.gene:omim%3A100740"
    compare_normalize_resp(resp, q, MatchType.ASSOCIATED_WITH,
                           cpy_normalized_ache,
                           expected_source_meta=expected_source_meta)


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
    q = "BRAF"
    expected_source_meta = ["HGNC", "Ensembl", "NCBI"]
    resp = query_handler.normalize(q)
    compare_normalize_resp(resp, q, MatchType.SYMBOL, normalized_braf,
                           expected_source_meta=expected_source_meta)

    q = "braf"
    resp = query_handler.normalize(q)
    cpy_normalized_braf = copy.deepcopy(normalized_braf)
    cpy_normalized_braf["id"] = "normalize.gene:braf"
    compare_normalize_resp(resp, q, MatchType.SYMBOL, cpy_normalized_braf,
                           expected_source_meta=expected_source_meta)

    q = "hgnc:1097"
    resp = query_handler.normalize(q)
    cpy_normalized_braf["id"] = "normalize.gene:hgnc%3A1097"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_braf,
                           expected_source_meta=expected_source_meta)

    q = "ensembl:ENSG00000157764"
    resp = query_handler.normalize(q)
    cpy_normalized_braf["id"] = "normalize.gene:ensembl%3AENSG00000157764"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_braf,
                           expected_source_meta=expected_source_meta)

    q = "ncbigene:673"
    resp = query_handler.normalize(q)
    cpy_normalized_braf["id"] = "normalize.gene:ncbigene%3A673"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_braf,
                           expected_source_meta=expected_source_meta)

    q = "NS7"
    resp = query_handler.normalize(q)
    cpy_normalized_braf["id"] = "normalize.gene:NS7"
    compare_normalize_resp(resp, q, MatchType.ALIAS, cpy_normalized_braf,
                           expected_source_meta=expected_source_meta)

    q = "omim:164757"
    resp = query_handler.normalize(q)
    cpy_normalized_braf["id"] = "normalize.gene:omim%3A164757"
    compare_normalize_resp(resp, q, MatchType.ASSOCIATED_WITH,
                           cpy_normalized_braf,
                           expected_source_meta=expected_source_meta)


def test_abl1_query(query_handler, num_sources, normalized_abl1):
    """Test that ABL1 concept_id shows xref matches."""
    # Search
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

    # Normalize
    q = "ABL1"
    expected_source_meta = ["HGNC", "Ensembl", "NCBI"]
    resp = query_handler.normalize(q)
    compare_normalize_resp(resp, q, MatchType.SYMBOL, normalized_abl1,
                           expected_source_meta=expected_source_meta)

    q = "abl1"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1 = copy.deepcopy(normalized_abl1)
    cpy_normalized_abl1["id"] = "normalize.gene:abl1"
    compare_normalize_resp(resp, q, MatchType.SYMBOL, cpy_normalized_abl1,
                           expected_source_meta=expected_source_meta)

    q = "hgnc:76"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1["id"] = "normalize.gene:hgnc%3A76"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_abl1,
                           expected_source_meta=expected_source_meta)

    q = "ensembl:ENSG00000097007"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1["id"] = "normalize.gene:ensembl%3AENSG00000097007"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_abl1,
                           expected_source_meta=expected_source_meta)

    q = "ncbigene:25"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1["id"] = "normalize.gene:ncbigene%3A25"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_abl1,
                           expected_source_meta=expected_source_meta)

    q = "v-abl"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1["id"] = "normalize.gene:v-abl"
    compare_normalize_resp(resp, q, MatchType.ALIAS, cpy_normalized_abl1,
                           expected_source_meta=expected_source_meta)

    q = "LOC116063"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1["id"] = "normalize.gene:LOC116063"
    compare_normalize_resp(resp, q, MatchType.PREV_SYMBOL, cpy_normalized_abl1,
                           expected_source_meta=expected_source_meta)

    q = "ABL"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1["id"] = "normalize.gene:ABL"
    compare_normalize_resp(resp, q, MatchType.PREV_SYMBOL, cpy_normalized_abl1,
                           expected_source_meta=expected_source_meta)

    q = "refseq:NM_007313"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1["id"] = "normalize.gene:refseq%3ANM_007313"
    compare_normalize_resp(resp, q, MatchType.ASSOCIATED_WITH,
                           cpy_normalized_abl1,
                           expected_source_meta=expected_source_meta)


def test_multiple_norm_concepts(query_handler, normalized_p150):
    """Tests where more than one normalized concept is found."""
    q = "P150"
    expected_source_meta = ["HGNC", "Ensembl", "NCBI"]
    resp = query_handler.normalize(q)
    expected_warnings = [{
        "multiple_normalized_concepts_found":
            ['hgnc:16850', 'hgnc:76', 'hgnc:17168', 'hgnc:500', 'hgnc:8982']
    }]
    compare_normalize_resp(resp, q, MatchType.ALIAS, normalized_p150,
                           expected_source_meta=expected_source_meta,
                           expected_warnings=expected_warnings)


def test_service_meta(query_handler):
    """Test service meta info in response."""
    resp = query_handler.search("pheno")
    compare_service_meta(resp["service_meta_"])
