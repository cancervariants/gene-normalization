"""Test import of NCBI source data"""

import datetime

import pytest

from gene.query import QueryHandler
from gene.schemas import (
    DataLicenseAttributes,
    Gene,
    MatchType,
    SourceName,
    SymbolStatus,
)


def check_ncbi_discontinued_gene(normalizer_response, concept_id, symbol, match_type):
    """Check that searches on NCBI discontinued genes are correct."""
    assert len(normalizer_response.records) == 1
    resp = normalizer_response.records[0]
    assert resp.match_type == match_type
    assert resp.concept_id == concept_id
    assert resp.symbol == symbol
    assert resp.symbol_status == SymbolStatus.DISCONTINUED
    assert resp.label is None
    assert resp.strand is None
    assert resp.location_annotations == []
    assert resp.locations == []
    assert resp.aliases == []
    assert resp.previous_symbols == []
    assert resp.xrefs == []
    assert resp.associated_with == []


@pytest.fixture(scope="module")
def ncbi(database):
    """Build ncbi test fixture."""

    class QueryGetter:
        def __init__(self):
            self.query_handler = QueryHandler(database)

        def search(self, query_str, incl="ncbi"):
            resp = self.query_handler.search(query_str, incl=incl)
            return resp.source_matches[SourceName.NCBI]

    return QueryGetter()


@pytest.fixture(scope="module")
def dpf1():
    """Create gene fixture for DPF1."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "double PHD fingers 1",
        "concept_id": "ncbigene:8193",
        "symbol": "DPF1",
        "aliases": ["BAF45b", "NEUD4", "neuro-d4", "SMARCG1"],
        "xrefs": ["hgnc:20225", "ensembl:ENSG00000011332"],
        "previous_symbols": [],
        "associated_with": ["omim:601670"],
        "symbol_status": None,
        "location_annotations": [],
        "strand": "-",
        "locations": [
            {
                "end": 38229695,
                "start": 38211005,
                "sequenceReference": {
                    "type": "SequenceReference",
                    "refgetAccession": "SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl",
                },
                "type": "SequenceLocation",
            }
        ],
        "gene_type": "protein-coding",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def pdp1_symbol():
    """Create gene fixture for PDP1 (ncbigene:54704)."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "pyruvate dehydrogenase phosphatase catalytic subunit 1",
        "concept_id": "ncbigene:54704",
        "symbol": "PDP1",
        "aliases": ["PDH", "PDP", "PDPC", "PPM2A", "PPM2C", "PDPC 1"],
        "xrefs": ["hgnc:9279", "ensembl:ENSG00000164951"],
        "previous_symbols": ["LOC157663", "PPM2C"],
        "associated_with": ["omim:605993"],
        "symbol_status": None,
        "location_annotations": [],
        "strand": "+",
        "locations": [
            {
                "end": 93926068,
                "start": 93916922,
                "sequenceReference": {
                    "type": "SequenceReference",
                    "refgetAccession": "SQ.209Z7zJ-mFypBEWLk4rNC6S_OxY5p7bs",
                },
                "type": "SequenceLocation",
            }
        ],
        "gene_type": "protein-coding",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def pdp1_alias():
    """Create gene fixture for PDP1 (ncbigene:403313)."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "phospholipid phosphatase 6",
        "concept_id": "ncbigene:403313",
        "symbol": "PLPP6",
        "aliases": ["PDP1", "PSDP", "PPAPDC2", "bA6J24.6", "LPRP-B", "PA-PSP"],
        "xrefs": ["hgnc:23682", "ensembl:ENSG00000205808"],
        "previous_symbols": [],
        "associated_with": ["omim:611666"],
        "symbol_status": None,
        "location_annotations": [],
        "strand": "+",
        "locations": [
            {
                "end": 4665258,
                "start": 4662293,
                "sequenceReference": {
                    "type": "SequenceReference",
                    "refgetAccession": "SQ.KEO-4XBcm1cxeo_DIQ8_ofqGUkp4iZhI",
                },
                "type": "SequenceLocation",
            }
        ],
        "gene_type": "protein-coding",
    }
    return Gene(**params)


# X and Y chromosomes
@pytest.fixture(scope="module")
def spry3():
    """Create gene fixture for SPRY3."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "sprouty RTK signaling antagonist 3",
        "concept_id": "ncbigene:10251",
        "symbol": "SPRY3",
        "aliases": ["spry-3"],
        "xrefs": ["hgnc:11271", "ensembl:ENSG00000168939"],
        "previous_symbols": ["LOC170187", "LOC253479"],
        "associated_with": ["omim:300531"],
        "symbol_status": None,
        "location_annotations": [],
        "strand": "+",
        "locations": [
            {
                "end": 155782459,
                "start": 155612585,
                "sequenceReference": {
                    "type": "SequenceReference",
                    "refgetAccession": "SQ.w0WZEvgJF0zf_P4yyTzjjv9oW1z61HHP",
                },
                "type": "SequenceLocation",
            },
            {
                "end": 56968979,
                "start": 56923422,
                "sequenceReference": {
                    "type": "SequenceReference",
                    "refgetAccession": "SQ.8_liLu1aycC0tPQPFmUaGXJLDs5SbPZ5",
                },
                "type": "SequenceLocation",
            },
        ],
        "gene_type": "protein-coding",
    }
    return Gene(**params)


# chromosome but no map locations
@pytest.fixture(scope="module")
def adcp1():
    """Create gene fixture for ADCP1."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "adenosine deaminase complexing protein 1",
        "concept_id": "ncbigene:106",
        "symbol": "ADCP1",
        "aliases": [],
        "xrefs": ["hgnc:229"],
        "previous_symbols": [],
        "associated_with": [],
        "symbol_status": None,
        "strand": None,
        "location_annotations": ["6"],
        "locations": [],
        "gene_type": "unknown",
    }
    return Gene(**params)


# no chromosome or map locations
@pytest.fixture(scope="module")
def afa():
    """Create gene fixture for AFA."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "ankyloblepharon filiforme adnatum",
        "concept_id": "ncbigene:170",
        "symbol": "AFA",
        "aliases": [],
        "xrefs": [],
        "previous_symbols": [],
        "associated_with": ["omim:106250"],
        "symbol_status": None,
        "strand": None,
        "location_annotations": [],
        "locations": [],
        "gene_type": "unknown",
    }
    return Gene(**params)


# Contains non cytogenic locations (i.e. "map from Rosati....")
@pytest.fixture(scope="module")
def znf84():
    """Create gene fixture for ZNF84."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "zinc finger protein 84",
        "concept_id": "ncbigene:7637",
        "symbol": "ZNF84",
        "aliases": ["HPF2"],
        "xrefs": ["hgnc:13159", "ensembl:ENSG00000198040"],
        "previous_symbols": ["LOC100287429"],
        "associated_with": ["omim:618554"],
        "symbol_status": None,
        "location_annotations": ["map from Rosati ref via FISH [AFS]"],
        "strand": "+",
        "locations": [
            {
                "end": 133063299,
                "start": 133037508,
                "sequenceReference": {
                    "type": "SequenceReference",
                    "refgetAccession": "SQ.6wlJpONE3oNb4D69ULmEXhqyDZ4vwNfl",
                },
                "type": "SequenceLocation",
            }
        ],
        "gene_type": "protein-coding",
    }
    return Gene(**params)


# No arm or sub band
@pytest.fixture(scope="module")
def slc25a6():
    """Create gene fixture for SLC25A6."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "solute carrier family 25 member 6",
        "concept_id": "ncbigene:293",
        "symbol": "SLC25A6",
        "aliases": ["AAC3", "ANT", "ANT 2", "ANT 3", "ANT3", "ANT3Y"],
        "xrefs": ["hgnc:10992", "ensembl:ENSG00000169100", "ensembl:ENSG00000292334"],
        "previous_symbols": ["ANT3Y"],
        "associated_with": ["omim:300151", "omim:403000"],
        "symbol_status": None,
        "location_annotations": ["X", "Y"],
        "strand": "-",
        "locations": [
            {
                "type": "SequenceLocation",
                "sequenceReference": {
                    "type": "SequenceReference",
                    "refgetAccession": "SQ.w0WZEvgJF0zf_P4yyTzjjv9oW1z61HHP",
                },
                "start": 1386151,
                "end": 1392113,
            },
            {
                "type": "SequenceLocation",
                "sequenceReference": {
                    "type": "SequenceReference",
                    "refgetAccession": "SQ.8_liLu1aycC0tPQPFmUaGXJLDs5SbPZ5",
                },
                "start": 1386151,
                "end": 1392113,
            },
        ],
        "gene_type": "protein-coding",
    }
    return Gene(**params)


# Contains arm but no sub band
@pytest.fixture(scope="module")
def loc106783576():
    """Create gene fixture for ."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "nonconserved acetylation island sequence 68 enhancer",
        "concept_id": "ncbigene:106783576",
        "symbol": "LOC106783576",
        "aliases": [],
        "xrefs": [],
        "previous_symbols": [],
        "associated_with": [],
        "symbol_status": None,
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "gene_type": "biological-region",
    }
    return Gene(**params)


# Testing for cen
@pytest.fixture(scope="module")
def glc1b():
    """Create gene fixture for GLC1B."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "glaucoma 1, open angle, B (adult-onset)",
        "concept_id": "ncbigene:2722",
        "symbol": "GLC1B",
        "aliases": [],
        "xrefs": [],
        "previous_symbols": [],
        "associated_with": ["omim:606689"],
        "symbol_status": None,
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "gene_type": "unknown",
    }
    return Gene(**params)


# Testing for ter ranges
@pytest.fixture(scope="module")
def hdpa():
    """Create gene fixture for HDPA."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "Hodgkin disease, susceptibility, pseudoautosomal",
        "concept_id": "ncbigene:50829",
        "symbol": "HDPA",
        "aliases": [],
        "xrefs": [],
        "previous_symbols": [],
        "associated_with": ["omim:300221"],
        "symbol_status": None,
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "gene_type": "unknown",
    }
    return Gene(**params)


# Testing for annotation
@pytest.fixture(scope="module")
def prkrap1():
    """Create gene fixture for PRKRAP1."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "protein activator of interferon induced protein kinase "
        "EIF2AK2 pseudogene 1",
        "concept_id": "ncbigene:731716",
        "symbol": "PRKRAP1",
        "aliases": [],
        "xrefs": ["hgnc:33447"],
        "previous_symbols": ["LOC100289695"],
        "associated_with": [],
        "symbol_status": None,
        "location_annotations": ["alternate reference locus"],
        "strand": "+",
        "locations": [
            {
                "end": 3941874,
                "start": 3940269,
                "sequenceReference": {
                    "type": "SequenceReference",
                    "refgetAccession": "SQ.MjujHSAsgNWRTX4w3ysM7b5OVhZpdXu1",
                },
                "type": "SequenceLocation",
            },
            {
                "end": 3932085,
                "start": 3930480,
                "sequenceReference": {
                    "type": "SequenceReference",
                    "refgetAccession": "SQ.Q8IworEhpLeXwpz1CHM7C3luysh-ltx-",
                },
                "type": "SequenceLocation",
            },
        ],
        "gene_type": "pseudo",
    }
    return Gene(**params)


# Different arms
@pytest.fixture(scope="module")
def spg37():
    """Create gene fixture for SPG37."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "spastic paraplegia 37 (autosomal dominant)",
        "concept_id": "ncbigene:100049159",
        "symbol": "SPG37",
        "aliases": [],
        "xrefs": [],
        "previous_symbols": [],
        "associated_with": ["omim:611945"],
        "symbol_status": None,
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "gene_type": "unknown",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def source_urls():
    """Provide source data URLs fixture."""
    return {
        "info_file": "ftp.ncbi.nlm.nih.govgene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz",
        "history_file": "ftp.ncbi.nlm.nih.govgene/DATA/gene_history.gz",
        "assembly_file": "ftp.ncbi.nlm.nih.govgenomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/",
    }


def test_dpf1(check_resp_single_record, ncbi, dpf1):
    """Test that DPF1 normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("ncbigene:8193")
    check_resp_single_record(resp, dpf1, MatchType.CONCEPT_ID)

    resp = ncbi.search("ncbIgene:8193")
    check_resp_single_record(resp, dpf1, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("DPF1")
    check_resp_single_record(resp, dpf1, MatchType.SYMBOL)

    resp = ncbi.search("DpF1")
    check_resp_single_record(resp, dpf1, MatchType.SYMBOL)

    # Alias
    resp = ncbi.search("BAF45b")
    check_resp_single_record(resp, dpf1, MatchType.ALIAS)

    resp = ncbi.search("NEUD4")
    check_resp_single_record(resp, dpf1, MatchType.ALIAS)

    resp = ncbi.search("neuro-d4")
    check_resp_single_record(resp, dpf1, MatchType.ALIAS)

    # associated_with
    resp = ncbi.search("omim:601670")
    check_resp_single_record(resp, dpf1, MatchType.ASSOCIATED_WITH)

    # No Match
    resp = ncbi.search("DPF 1")
    assert len(resp.records) == 0

    resp = ncbi.search("DPG1")
    assert len(resp.records) == 0


def test_pdp1(compare_records, check_resp_single_record, ncbi, pdp1_symbol, pdp1_alias):
    """Test that PDP1 normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("ncbigene:54704")
    check_resp_single_record(resp, pdp1_symbol, MatchType.CONCEPT_ID)

    resp = ncbi.search("NCBIGENE:54704")
    check_resp_single_record(resp, pdp1_symbol, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("PDP1")
    assert len(resp.records) == 2
    # first record check (should always be symbol)
    compare_records(resp.records[0], pdp1_symbol, MatchType.SYMBOL)
    compare_records(resp.records[1], pdp1_alias, MatchType.ALIAS)

    resp = ncbi.search("pdp1")
    assert len(resp.records) == 2
    # first record check (should always be symbol)
    compare_records(resp.records[0], pdp1_symbol, MatchType.SYMBOL)
    compare_records(resp.records[1], pdp1_alias, MatchType.ALIAS)

    # Previous Symbol
    resp = ncbi.search("LOC157663")
    check_resp_single_record(resp, pdp1_symbol, MatchType.PREV_SYMBOL)

    resp = ncbi.search("PPM2C")
    check_resp_single_record(resp, pdp1_symbol, MatchType.PREV_SYMBOL)

    resp = ncbi.search("loc157663")
    check_resp_single_record(resp, pdp1_symbol, MatchType.PREV_SYMBOL)

    # Alias
    resp = ncbi.search("pdh")
    check_resp_single_record(resp, pdp1_symbol, MatchType.ALIAS)

    resp = ncbi.search("PDP")
    check_resp_single_record(resp, pdp1_symbol, MatchType.ALIAS)

    resp = ncbi.search("PDPC")
    check_resp_single_record(resp, pdp1_symbol, MatchType.ALIAS)

    resp = ncbi.search("PPM2A")
    check_resp_single_record(resp, pdp1_symbol, MatchType.ALIAS)


def test_spry3(check_resp_single_record, ncbi, spry3):
    """Test that SPRY3 normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("NCBIgene:10251")
    check_resp_single_record(resp, spry3, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("sprY3")
    check_resp_single_record(resp, spry3, MatchType.SYMBOL)

    # Alias
    resp = ncbi.search("SPRY-3")
    check_resp_single_record(resp, spry3, MatchType.ALIAS)


def test_adcp1(check_resp_single_record, ncbi, adcp1):
    """Test that ADCP1 normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("NCBIgene:106")
    check_resp_single_record(resp, adcp1, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("ADCP1")
    check_resp_single_record(resp, adcp1, MatchType.SYMBOL)


def test_afa(check_resp_single_record, ncbi, afa):
    """Test that AFA normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("NCBIgene:170")
    check_resp_single_record(resp, afa, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("AFA")
    check_resp_single_record(resp, afa, MatchType.SYMBOL)


def test_znf84(check_resp_single_record, ncbi, znf84):
    """Test that ZNF84 normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("NCBIgene:7637")
    check_resp_single_record(resp, znf84, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("ZNF84")
    check_resp_single_record(resp, znf84, MatchType.SYMBOL)


def test_slc25a6(check_resp_single_record, ncbi, slc25a6):
    """Test that SLC25A6 normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("NCBIgene:293")
    check_resp_single_record(resp, slc25a6, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("SLC25A6")
    check_resp_single_record(resp, slc25a6, MatchType.SYMBOL)


def test_loc106783576(check_resp_single_record, ncbi, loc106783576):
    """Test that LOC106783576 normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("NCBIgene:106783576")
    check_resp_single_record(resp, loc106783576, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("LOC106783576")
    check_resp_single_record(resp, loc106783576, MatchType.SYMBOL)


def test_oms(ncbi):
    """Test that OMS matches to correct gene concept."""
    resp = ncbi.search("NCBIgene:619538")
    assert len(resp.records) == 0


def test_glc1b(check_resp_single_record, ncbi, glc1b):
    """Test that GLC1B normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("NCBIgene:2722")
    check_resp_single_record(resp, glc1b, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("GLC1B")
    check_resp_single_record(resp, glc1b, MatchType.SYMBOL)

    # associated_with
    resp = ncbi.search("omim:606689")
    check_resp_single_record(resp, glc1b, MatchType.ASSOCIATED_WITH)


def test_hdpa(check_resp_single_record, ncbi, hdpa):
    """Test that HDPA normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("NCBIgene:50829")
    check_resp_single_record(resp, hdpa, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("HDPA")
    check_resp_single_record(resp, hdpa, MatchType.SYMBOL)


def test_prkrap1(check_resp_single_record, ncbi, prkrap1):
    """Test that PRKRAP1 normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("NCBIgene:731716")
    check_resp_single_record(resp, prkrap1, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("PRKRAP1")
    check_resp_single_record(resp, prkrap1, MatchType.SYMBOL)

    # xref
    resp = ncbi.search("hgnc:33447")
    check_resp_single_record(resp, prkrap1, MatchType.XREF)


def test_spg37(check_resp_single_record, ncbi, spg37):
    """Test that SPG37 normalizes to correct gene concept."""
    # Concept ID
    resp = ncbi.search("NCBIgene:100049159")
    check_resp_single_record(resp, spg37, MatchType.CONCEPT_ID)

    # Symbol
    resp = ncbi.search("SPG37")
    check_resp_single_record(resp, spg37, MatchType.SYMBOL)

    # associated_with
    resp = ncbi.search("omim:611945")
    check_resp_single_record(resp, spg37, MatchType.ASSOCIATED_WITH)


def test_discontinued_genes(ncbi):
    """Test searches for discontinued genes."""
    # HOTS
    resp = ncbi.search("ncbigene:103344718")
    check_ncbi_discontinued_gene(
        resp, "ncbigene:103344718", "HOTS", MatchType.CONCEPT_ID
    )

    resp = ncbi.search("HOTS")
    check_ncbi_discontinued_gene(
        resp, "ncbigene:103344718", "HOTS", MatchType.CONCEPT_ID
    )

    resp = ncbi.search("hots")
    check_ncbi_discontinued_gene(
        resp, "ncbigene:103344718", "HOTS", MatchType.CONCEPT_ID
    )

    # AASTH23
    resp = ncbi.search("ncbigene:544580")
    check_ncbi_discontinued_gene(
        resp, "ncbigene:544580", "AASTH23", MatchType.CONCEPT_ID
    )

    resp = ncbi.search("AASTH23")
    check_ncbi_discontinued_gene(
        resp, "ncbigene:544580", "AASTH23", MatchType.CONCEPT_ID
    )

    resp = ncbi.search("aastH23")
    check_ncbi_discontinued_gene(
        resp, "ncbigene:544580", "AASTH23", MatchType.CONCEPT_ID
    )


def test_no_match(ncbi, source_urls):
    """Test that nonexistent query doesn"t normalize to a match."""
    response = ncbi.search("cisplatin")
    assert len(response.records) == 0
    # double-check that meta still populates
    assert response.source_meta_.data_license == "custom"
    assert (
        response.source_meta_.data_license_url
        == "https://www.ncbi.nlm.nih.gov/home/about/policies/"
    )
    assert datetime.datetime.now(tz=datetime.UTC).strptime(
        response.source_meta_.version, "%Y%m%d"
    )
    assert response.source_meta_.data_url == source_urls
    assert response.source_meta_.rdp_url == "https://reusabledata.org/ncbi-gene.html"
    assert not response.source_meta_.data_license_attributes.non_commercial
    assert not response.source_meta_.data_license_attributes.share_alike
    assert not response.source_meta_.data_license_attributes.attribution

    # check blank
    response = ncbi.search("")
    assert len(response.records) == 0

    # check some strange characters
    response = ncbi.search("----")
    assert len(response.records) == 0

    response = ncbi.search("''")
    assert len(response.records) == 0

    response = ncbi.search("~~~")
    assert len(response.records) == 0

    response = ncbi.search(" ")
    assert len(response.records) == 0

    # Incorrect Concept IDs
    response = ncbi.search("ncblgene:8193")
    assert len(response.records) == 0

    response = ncbi.search("NCBIGENE54704")
    assert len(response.records) == 0

    response = ncbi.search("54704")
    assert len(response.records) == 0

    response = ncbi.search("ncbigene;54704")
    assert len(response.records) == 0


def test_meta(ncbi, source_urls):
    """Test NCBI source metadata."""
    response = ncbi.search("PDP1")
    assert response.source_meta_.data_license == "custom"
    assert (
        response.source_meta_.data_license_url
        == "https://www.ncbi.nlm.nih.gov/home/about/policies/"
    )
    assert datetime.datetime.now(tz=datetime.UTC).strptime(
        response.source_meta_.version, "%Y%m%d"
    )
    assert response.source_meta_.data_url == source_urls
    assert response.source_meta_.rdp_url == "https://reusabledata.org/ncbi-gene.html"
    assert response.source_meta_.genome_assemblies == ["GRCh38.p14"]
    assert response.source_meta_.data_license_attributes == DataLicenseAttributes(
        non_commercial=False, share_alike=False, attribution=False
    )
