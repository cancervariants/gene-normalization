"""Test that the gene normalizer works as intended for the Ensembl source."""
import pytest

from gene.query import QueryHandler
from gene.schemas import Gene, MatchType, SourceName
from tests.conftest import check_resp_single_record


@pytest.fixture(scope="module")
def ensembl(database):
    """Build ensembl test fixture."""

    class QueryGetter:
        def __init__(self):
            self.query_handler = QueryHandler(database)

        def search(self, query_str, incl="ensembl"):
            resp = self.query_handler.search(query_str, keyed=True, incl=incl)
            return resp.source_matches[SourceName.ENSEMBL.value]

    e = QueryGetter()
    return e


@pytest.fixture(scope="module")
def ddx11l1():
    """Create a DDX11L1 fixutre."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "concept_id": "ensembl:ENSG00000223972",
        "symbol": "DDX11L1",
        "label": "DEAD/H-box helicase 11 like 1 (pseudogene)",
        "previous_symbols": [],
        "aliases": [],
        "xrefs": ["hgnc:37102"],
        "symbol_status": None,
        "location_annotations": [],
        "locations": [
            {
                "_id": "ga4gh:VSL.dJvg-3cfkRkZEOuAmJ9xbkTBrTCea2VP",
                "interval": {
                    "end": {"value": 13670, "type": "Number"},
                    "start": {"value": 12009, "type": "Number"},
                    "type": "SequenceInterval",
                },
                "sequence_id": "ga4gh:SQ.Ya6Rs7DHhDeg7YaOSg1EoNi3U_nQ9SvO",
                "type": "SequenceLocation",
            }
        ],
        "strand": "+",
        "associated_with": [],
        "gene_type": "transcribed_unprocessed_pseudogene",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def tp53():
    """Create a TP53 fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "concept_id": "ensembl:ENSG00000141510",
        "symbol": "TP53",
        "label": "tumor protein p53",
        "previous_symbols": [],
        "aliases": [],
        "xrefs": ["hgnc:11998"],
        "symbol_status": None,
        "location_annotations": [],
        "locations": [
            {
                "_id": "ga4gh:VSL.7q-vAjxSYARaPbbUjhDng2oay795NfbE",
                "interval": {
                    "end": {"value": 7687538, "type": "Number"},
                    "start": {"value": 7661778, "type": "Number"},
                    "type": "SequenceInterval",
                },
                "sequence_id": "ga4gh:SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7",
                "type": "SequenceLocation",
            }
        ],
        "strand": "-",
        "associated_with": [],
        "gene_type": "protein_coding",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def ATP6AP1_DT():  # noqa: N802
    """Create a ATP6AP1-DT test fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "concept_id": "ensembl:ENSG00000197180",
        "symbol": "ATP6AP1-DT",
        "label": "ATP6AP1 divergent transcript",
        "previous_symbols": [],
        "aliases": [],
        "xrefs": ["hgnc:25138"],
        "symbol_status": None,
        "location_annotations": [],
        "locations": [
            {
                "_id": "ga4gh:VSL.GPNFtIoo1cr6b_wQSk7xP2wzncSyXgSx",
                "interval": {
                    "end": {"value": 154428526, "type": "Number"},
                    "start": {"value": 154424377, "type": "Number"},
                    "type": "SequenceInterval",
                },
                "sequence_id": "ga4gh:SQ.w0WZEvgJF0zf_P4yyTzjjv9oW1z61HHP",
                "type": "SequenceLocation",
            }
        ],
        "strand": "-",
        "associated_with": [],
        "gene_type": "lncRNA",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def hsa_mir_1253():
    """Create a hsa-miR-1253 test fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "concept_id": "ensembl:ENSG00000272920",
        "symbol": "hsa-mir-1253",
        "label": "hsa-mir-1253",
        "previous_symbols": [],
        "aliases": [],
        "xrefs": [],
        "symbol_status": None,
        "location_annotations": [],
        "locations": [
            {
                "_id": "ga4gh:VSL.goBvYPYef2mQildG6AiiRNVhTo-g4-1E",
                "interval": {
                    "end": {"value": 2748182, "type": "Number"},
                    "start": {"value": 2748077, "type": "Number"},
                    "type": "SequenceInterval",
                },
                "sequence_id": "ga4gh:SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7",
                "type": "SequenceLocation",
            }
        ],
        "strand": "+",
        "associated_with": ["mirbase:MI0006387"],
        "gene_type": "lncRNA",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def spry3():
    """Create a SPRY3 test fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "concept_id": "ensembl:ENSG00000168939",
        "symbol": "SPRY3",
        "label": "sprouty RTK signaling antagonist 3",
        "previous_symbols": [],
        "aliases": [],
        "xrefs": ["hgnc:11271"],
        "symbol_status": None,
        "location_annotations": [],
        "locations": [
            {
                "_id": "ga4gh:VSL.7Jax3UNlW_EZrZ44U-R1eLe_OeCC71IR",
                "interval": {
                    "end": {"value": 155782459, "type": "Number"},
                    "start": {"value": 155612571, "type": "Number"},
                    "type": "SequenceInterval",
                },
                "sequence_id": "ga4gh:SQ.w0WZEvgJF0zf_P4yyTzjjv9oW1z61HHP",
                "type": "SequenceLocation",
            }
        ],
        "strand": "+",
        "associated_with": [],
        "gene_type": "protein_coding",
    }
    return Gene(**params)


def test_ddx11l1(ensembl, ddx11l1):
    """Test that DDX11L1 normalizes to correct gene concept."""
    # Concept ID
    resp = ensembl.search("ensembl:ENSG00000223972")
    check_resp_single_record(resp, ddx11l1, MatchType.CONCEPT_ID)

    resp = ensembl.search("ENSEMBL:ENSG00000223972")
    check_resp_single_record(resp, ddx11l1, MatchType.CONCEPT_ID)

    resp = ensembl.search("ENSG00000223972")
    check_resp_single_record(resp, ddx11l1, MatchType.CONCEPT_ID)

    # Symbol
    resp = ensembl.search("ddx11l1")
    check_resp_single_record(resp, ddx11l1, MatchType.SYMBOL)

    resp = ensembl.search("DDX11L1")
    check_resp_single_record(resp, ddx11l1, MatchType.SYMBOL)


def test_tp53(ensembl, tp53):
    """Test that tp53 normalizes to correct gene concept."""
    # Concept ID
    resp = ensembl.search("ensembl:ENSG00000141510")
    check_resp_single_record(resp, tp53, MatchType.CONCEPT_ID)

    resp = ensembl.search("ENSEMBL:ENSG00000141510")
    check_resp_single_record(resp, tp53, MatchType.CONCEPT_ID)

    resp = ensembl.search("ENSG00000141510")
    check_resp_single_record(resp, tp53, MatchType.CONCEPT_ID)

    # Symbol
    resp = ensembl.search("tp53")
    check_resp_single_record(resp, tp53, MatchType.SYMBOL)

    resp = ensembl.search("TP53")
    check_resp_single_record(resp, tp53, MatchType.SYMBOL)


def test_ATP6AP1_DT(ensembl, ATP6AP1_DT):  # noqa: N802 N803
    """Test that ATP6AP1-DT normalizes to correct gene concept."""
    # Concept ID
    resp = ensembl.search("ensembl:ENSG00000197180")
    check_resp_single_record(resp, ATP6AP1_DT, MatchType.CONCEPT_ID)

    resp = ensembl.search("ENSEMBL:ENSG00000197180")
    check_resp_single_record(resp, ATP6AP1_DT, MatchType.CONCEPT_ID)

    resp = ensembl.search("ENSG00000197180")
    check_resp_single_record(resp, ATP6AP1_DT, MatchType.CONCEPT_ID)

    # Symbol
    resp = ensembl.search("ATP6AP1-DT")
    check_resp_single_record(resp, ATP6AP1_DT, MatchType.SYMBOL)


def test_hsa_mir_1253(ensembl, hsa_mir_1253):
    """Test that hsa-mir-1253 normalizes to correct gene concept."""
    # Concept ID
    resp = ensembl.search("ensembl:ENSG00000272920")
    check_resp_single_record(resp, hsa_mir_1253, MatchType.CONCEPT_ID)

    resp = ensembl.search("ENSEMBL:ENSG00000272920")
    check_resp_single_record(resp, hsa_mir_1253, MatchType.CONCEPT_ID)

    resp = ensembl.search("ENSG00000272920")
    check_resp_single_record(resp, hsa_mir_1253, MatchType.CONCEPT_ID)

    # Symbol
    resp = ensembl.search("hsa-mir-1253")
    check_resp_single_record(resp, hsa_mir_1253, MatchType.SYMBOL)

    # associated_with
    resp = ensembl.search("mirbase:MI0006387")
    check_resp_single_record(resp, hsa_mir_1253, MatchType.ASSOCIATED_WITH)


def test_spry3(ensembl, spry3):
    """Test that spry3 normalizes to correct gene concept."""
    # Concept ID
    resp = ensembl.search("ensembl:EnSG00000168939")
    check_resp_single_record(resp, spry3, MatchType.CONCEPT_ID)

    resp = ensembl.search("ENSEMBL:EnSG00000168939")
    check_resp_single_record(resp, spry3, MatchType.CONCEPT_ID)

    resp = ensembl.search("EnSG00000168939")
    check_resp_single_record(resp, spry3, MatchType.CONCEPT_ID)

    # Symbol
    resp = ensembl.search("spry3")
    check_resp_single_record(resp, spry3, MatchType.SYMBOL)


def test_no_match(ensembl):
    """Test that a term normalizes to correct gene concept as a NO match."""
    resp = ensembl.search("A1BG - AS1")
    assert len(resp.records) == 0

    resp = ensembl.search("hnc:5")
    assert len(resp.records) == 0

    # Test empty query
    resp = ensembl.search("")
    assert len(resp.records) == 0

    # Do not search on label
    resp = ensembl.search("A1BG antisense RNA 1")
    assert len(resp.records) == 0

    resp = ensembl.search("ensembl:ENSG00000278704")
    assert len(resp.records) == 0

    resp = ensembl.search("ensembl:ENSG00000284906")
    assert len(resp.records) == 0


def test_meta_info(ensembl):
    """Test that the meta field is correct."""
    resp = ensembl.search("chromosome:1")
    assert resp.source_meta_.data_license == "custom"
    assert (
        resp.source_meta_.data_license_url
        == "https://useast.ensembl.org/info/about/legal/disclaimer.html"
    )
    assert resp.source_meta_.version == "110"
    assert (
        resp.source_meta_.data_url
        == "ftp://ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.110.gff3.gz"
    )  # noqa: E501
    assert resp.source_meta_.rdp_url is None
    assert resp.source_meta_.genome_assemblies == ["GRCh38"]
    assert resp.source_meta_.data_license_attributes == {
        "non_commercial": False,
        "share_alike": False,
        "attribution": False,
    }
