"""Test that the gene normalizer works as intended for the HGNC source."""

import datetime

import pytest

from gene.query import QueryHandler
from gene.schemas import DataLicenseAttributes, Gene, MatchType, SourceName


@pytest.fixture(scope="module")
def hgnc(database):
    """Build hgnc test fixture."""

    class QueryGetter:
        def __init__(self):
            self.query_handler = QueryHandler(database)

        def search(self, query_str, incl="hgnc"):
            resp = self.query_handler.search(query_str, incl=incl)
            return resp.source_matches[SourceName.HGNC]

    return QueryGetter()


# Test Non Alt Loci Set


@pytest.fixture(scope="module")
def a1bg_as1():
    """Create an A1BG-AS1 gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "A1BG antisense RNA 1",
        "concept_id": "hgnc:37133",
        "symbol": "A1BG-AS1",
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "previous_symbols": ["NCRNA00181", "A1BGAS", "A1BG-AS"],
        "aliases": ["FLJ23569"],
        "symbol_status": "approved",
        "associated_with": [
            "vega:OTTHUMG00000183508",
            "ucsc:uc002qse.3",
            "refseq:NR_015380",
            "ena.embl:BC040926",
            "refseq:NR_015380",
            "ena.embl:BC040926",
        ],
        "xrefs": ["ensembl:ENSG00000268895", "ncbigene:503538"],
        "gene_type": "RNA, long non-coding",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def tp53():
    """Create a TP53 gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "tumor protein p53",
        "concept_id": "hgnc:11998",
        "symbol": "TP53",
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "previous_symbols": [],
        "aliases": ["p53", "LFS1"],
        "symbol_status": "approved",
        "associated_with": [
            "vega:OTTHUMG00000162125",
            "refseq:NM_000546",
            "cosmic:TP53",
            "omim:191170",
            "ucsc:uc060aur.1",
            "uniprot:P04637",
            "orphanet:120204",
            "ena.embl:AF307851",
            "pubmed:6396087",
            "pubmed:3456488",
            "pubmed:2047879",
        ],
        "xrefs": ["ensembl:ENSG00000141510", "ncbigene:7157"],
        "gene_type": "gene with protein product",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def a3galt2():
    """Create an A3GALT2 gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "alpha 1,3-galactosyltransferase 2",
        "concept_id": "hgnc:30005",
        "symbol": "A3GALT2",
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "previous_symbols": ["A3GALT2P"],
        "aliases": ["IGBS3S", "IGB3S"],
        "symbol_status": "approved",
        "xrefs": ["ensembl:ENSG00000184389", "ncbigene:127550"],
        "associated_with": [
            "vega:OTTHUMG00000004125",
            "vega:OTTHUMG00000004125",
            "ucsc:uc031plq.1",
            "uniprot:U3KPV4",
            "ccds:CCDS60080",
            "pubmed:10854427",
            "pubmed:18630988",
            "refseq:NM_001080438",
            "omim:619850",
        ],
        "gene_type": "gene with protein product",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def wdhd1():
    """Create a WDHD1 gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "WD repeat and HMG-box DNA binding protein 1",
        "concept_id": "hgnc:23170",
        "symbol": "WDHD1",
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "previous_symbols": [],
        "aliases": ["AND-1", "CTF4", "CHTF4"],
        "symbol_status": "approved",
        "xrefs": ["ensembl:ENSG00000198554", "ncbigene:11169"],
        "associated_with": [
            "vega:OTTHUMG00000140304",
            "refseq:NM_007086",
            "omim:608126",
            "ucsc:uc001xbm.3",
            "uniprot:O75717",
            "ccds:CCDS41955",
            "ccds:CCDS9721",
            "ena.embl:AJ006266",
            "pubmed:9175701",
            "pubmed:20028748",
        ],
        "gene_type": "gene with protein product",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def g6pr():
    """Create a G6PR gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "glucose-6-phosphatase regulator",
        "concept_id": "hgnc:4059",
        "symbol": "G6PR",
        "location_annotations": ["reserved"],
        "locations": [],
        "strand": None,
        "previous_symbols": [],
        "aliases": ["GSD1aSP"],
        "symbol_status": "approved",
        "xrefs": ["ncbigene:2541"],
        "associated_with": ["pubmed:2172641", "pubmed:7814621", "pubmed:2996501"],
        "gene_type": "unknown",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def pirc24():
    """Create a PIRC24 gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "piwi-interacting RNA cluster 24",
        "concept_id": "hgnc:37528",
        "symbol": "PIRC24",
        "location_annotations": ["6"],
        "locations": [],
        "strand": None,
        "previous_symbols": [],
        "aliases": [],
        "symbol_status": "approved",
        "xrefs": ["ncbigene:100313810"],
        "associated_with": ["pubmed:17881367"],
        "gene_type": "RNA, cluster",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def gage4():
    """Create a GAGE4 gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "G antigen 4",
        "concept_id": "hgnc:4101",
        "symbol": "GAGE4",
        "location_annotations": ["not on reference assembly"],
        "strand": None,
        "locations": [],
        "previous_symbols": [],
        "aliases": ["CT4.4"],
        "symbol_status": "approved",
        "xrefs": ["ncbigene:2576"],
        "associated_with": [
            "refseq:NM_001474",
            "omim:300597",
            "uniprot:P0DSO3",
            "ena.embl:U19145",
            "pubmed:7544395",
        ],
        "gene_type": "gene with protein product",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def mafip():
    """Create a MAFIP gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "MAFF interacting protein",
        "concept_id": "hgnc:31102",
        "symbol": "MAFIP",
        "location_annotations": ["unplaced", "14"],
        "locations": [],
        "strand": None,
        "previous_symbols": [],
        "aliases": ["FLJ35473", "FLJ00219", "FLJ39633", "MIP", "pp5644", "TEKT4P4"],
        "symbol_status": "approved",
        "xrefs": ["ensembl:ENSG00000274847", "ncbigene:727764"],
        "associated_with": [
            "vega:OTTHUMG00000188065",
            "refseq:NR_046439",
            "uniprot:Q8WZ33",
            "ena.embl:AK074146",
            "ena.embl:AF289559",
            "pubmed:16549056",
            "pubmed:15881666",
        ],
        "gene_type": "unknown",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def mt_7sdna():
    """Create a MT-7SDNA gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "mitochondrially encoded 7S DNA",
        "concept_id": "hgnc:7409",
        "symbol": "MT-7SDNA",
        "location_annotations": ["MT"],
        "locations": [],
        "strand": None,
        "previous_symbols": ["MT7SDNA"],
        "aliases": [],
        "symbol_status": "approved",
        "xrefs": [],
        "associated_with": ["pubmed:24709344", "pubmed:273237"],
        "gene_type": "region",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def cecr():
    """Create a CECR gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "cat eye syndrome chromosome region",
        "concept_id": "hgnc:1838",
        "symbol": "CECR",
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "previous_symbols": [],
        "aliases": [],
        "symbol_status": "approved",
        "xrefs": ["ncbigene:1055"],
        "associated_with": [],
        "gene_type": "region",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def csf2ra():
    """Create a CSF2RA gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "colony stimulating factor 2 receptor subunit alpha",
        "concept_id": "hgnc:2435",
        "symbol": "CSF2RA",
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "previous_symbols": ["CSF2R"],
        "aliases": ["CD116", "alphaGMR"],
        "symbol_status": "approved",
        "xrefs": ["ensembl:ENSG00000198223", "ncbigene:1438"],
        "associated_with": [
            "vega:OTTHUMG00000012533",
            "refseq:NM_001161529",
            "orphanet:209477",
            "iuphar:1707",
            "hcdmdb:CD116",
            "omim:306250",
            "omim:425000",
            "ucsc:uc010nvv.3",
            "uniprot:P15509",
            "ena.embl:M64445",
            "pubmed:1702217",
        ],
        "gene_type": "gene with protein product",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def rps24p5():
    """Create a RPS24P5 gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "ribosomal protein S24 pseudogene 5",
        "concept_id": "hgnc:36026",
        "symbol": "RPS24P5",
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "previous_symbols": [],
        "aliases": [],
        "symbol_status": "approved",
        "xrefs": ["ncbigene:100271094"],
        "associated_with": ["refseq:NG_011274", "pubmed:19123937"],
        "gene_type": "pseudogene",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def trl_cag2_1():
    """Create a TRL-CAG2-1 gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "tRNA-Leu (anticodon CAG) 2-1",
        "concept_id": "hgnc:34692",
        "symbol": "TRL-CAG2-1",
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "previous_symbols": ["TRNAL13"],
        "aliases": ["tRNA-Leu-CAG-2-1"],
        "symbol_status": "approved",
        "xrefs": ["ncbigene:100189130"],
        "associated_with": ["ena.embl:HG983896"],
        "gene_type": "RNA, transfer",
    }
    return Gene(**params)


@pytest.fixture(scope="module")
def myo5b():
    """Create a MYO5B gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "myosin VB",
        "concept_id": "hgnc:7603",
        "symbol": "MYO5B",
        "location_annotations": [],
        "strand": None,
        "locations": [],
        "previous_symbols": [],
        "aliases": ["KIAA1119"],
        "symbol_status": "approved",
        "xrefs": ["ensembl:ENSG00000167306", "ncbigene:4645"],
        "associated_with": [
            "vega:OTTHUMG00000179843",
            "refseq:NM_001080467",
            "omim:606540",
            "ucsc:uc002leb.3",
            "uniprot:Q9ULV0",
            "orphanet:171089",
            "ccds:CCDS42436",
            "ena.embl:AB032945",
            "pubmed:8884266",
            "pubmed:17462998",
        ],
        "gene_type": "gene with protein product",
    }
    return Gene(**params)


# Test Alt Loci Set


@pytest.fixture(scope="module")
def gstt1():
    """Create an GSTT1 gene fixture."""
    params = {
        "match_type": MatchType.NO_MATCH,
        "label": "glutathione S-transferase theta 1",
        "concept_id": "hgnc:4641",
        "symbol": "GSTT1",
        "location_annotations": ["alternate reference locus"],
        "strand": None,
        "locations": [],
        "previous_symbols": [],
        "aliases": ["2.5.1.18"],
        "symbol_status": "approved",
        "associated_with": [
            "refseq:NM_000853",
            "omim:600436",
            "ucsc:uc002zze.4",
            "uniprot:P30711",
            "orphanet:470418",
            "ena.embl:KI270879",
            "pubmed:8617495",
        ],
        "xrefs": ["ensembl:ENSG00000277656", "ncbigene:2952"],
        "gene_type": "gene with protein product",
    }
    return Gene(**params)


def test_a1bg_as1(check_resp_single_record, a1bg_as1, hgnc):
    """Test that a1bg_as1 normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:37133")
    check_resp_single_record(resp, a1bg_as1, MatchType.CONCEPT_ID)

    resp = hgnc.search("HGNC:37133")
    check_resp_single_record(resp, a1bg_as1, MatchType.CONCEPT_ID)

    resp = hgnc.search("Hgnc:37133")
    check_resp_single_record(resp, a1bg_as1, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("A1BG-AS1")
    check_resp_single_record(resp, a1bg_as1, MatchType.SYMBOL)

    resp = hgnc.search("A1BG-as1")
    check_resp_single_record(resp, a1bg_as1, MatchType.SYMBOL)

    # Previous Symbol
    resp = hgnc.search("NCRNA00181")
    check_resp_single_record(resp, a1bg_as1, MatchType.PREV_SYMBOL)

    resp = hgnc.search("A1BGAS")
    check_resp_single_record(resp, a1bg_as1, MatchType.PREV_SYMBOL)

    resp = hgnc.search("A1BG-AS")
    check_resp_single_record(resp, a1bg_as1, MatchType.PREV_SYMBOL)

    # Alias
    resp = hgnc.search("FLJ23569")
    check_resp_single_record(resp, a1bg_as1, MatchType.ALIAS)

    resp = hgnc.search("flj23569")
    check_resp_single_record(resp, a1bg_as1, MatchType.ALIAS)


def test_a3galt2(check_resp_single_record, a3galt2, hgnc):
    """Test that a3galt2 normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:30005")
    check_resp_single_record(resp, a3galt2, MatchType.CONCEPT_ID)

    resp = hgnc.search("HGNC:30005")
    check_resp_single_record(resp, a3galt2, MatchType.CONCEPT_ID)

    resp = hgnc.search("Hgnc:30005")
    check_resp_single_record(resp, a3galt2, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("A3GALT2")
    check_resp_single_record(resp, a3galt2, MatchType.SYMBOL)

    resp = hgnc.search("a3galt2")
    check_resp_single_record(resp, a3galt2, MatchType.SYMBOL)

    # Previous Symbol
    resp = hgnc.search("A3GALT2P")
    check_resp_single_record(resp, a3galt2, MatchType.PREV_SYMBOL)

    resp = hgnc.search("A3GALT2p")
    check_resp_single_record(resp, a3galt2, MatchType.PREV_SYMBOL)

    # Alias
    resp = hgnc.search("IGBS3S")
    check_resp_single_record(resp, a3galt2, MatchType.ALIAS)

    resp = hgnc.search("igB3s")
    check_resp_single_record(resp, a3galt2, MatchType.ALIAS)


def test_tp53(check_resp_single_record, tp53, hgnc):
    """Test that tp53 normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:11998")
    check_resp_single_record(resp, tp53, MatchType.CONCEPT_ID)

    resp = hgnc.search("HGNC:11998")
    check_resp_single_record(resp, tp53, MatchType.CONCEPT_ID)

    resp = hgnc.search("Hgnc:11998")
    check_resp_single_record(resp, tp53, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("tp53")
    check_resp_single_record(resp, tp53, MatchType.SYMBOL)

    resp = hgnc.search("TP53")
    check_resp_single_record(resp, tp53, MatchType.SYMBOL)

    # Alias
    resp = hgnc.search("LFS1")
    check_resp_single_record(resp, tp53, MatchType.ALIAS)

    resp = hgnc.search("p53")
    check_resp_single_record(resp, tp53, MatchType.ALIAS)


def test_wdhd1(check_resp_single_record, wdhd1, hgnc):
    """Test that a1bg_as1 normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:23170")
    check_resp_single_record(resp, wdhd1, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("WDHD1")
    check_resp_single_record(resp, wdhd1, MatchType.SYMBOL)


def test_g6pr(check_resp_single_record, g6pr, hgnc):
    """Test that g6pr normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:4059")
    check_resp_single_record(resp, g6pr, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("G6PR")
    check_resp_single_record(resp, g6pr, MatchType.SYMBOL)


def test_pirc24(check_resp_single_record, pirc24, hgnc):
    """Test that pirc24 normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:37528")
    check_resp_single_record(resp, pirc24, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("PIRC24")
    check_resp_single_record(resp, pirc24, MatchType.SYMBOL)


def test_gage4(check_resp_single_record, gage4, hgnc):
    """Test that gage4 normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:4101")
    check_resp_single_record(resp, gage4, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("GAGE4")
    check_resp_single_record(resp, gage4, MatchType.SYMBOL)


def test_mafip(check_resp_single_record, mafip, hgnc):
    """Test that mafip normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:31102")
    check_resp_single_record(resp, mafip, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("MAFIP")
    check_resp_single_record(resp, mafip, MatchType.SYMBOL)


def test_mt_7sdna(check_resp_single_record, mt_7sdna, hgnc):
    """Test that mt_7sdna normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:7409")
    check_resp_single_record(resp, mt_7sdna, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("MT-7SDNA")
    check_resp_single_record(resp, mt_7sdna, MatchType.SYMBOL)


def test_cecr(check_resp_single_record, cecr, hgnc):
    """Test that cecr normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:1838")
    check_resp_single_record(resp, cecr, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("CECR")
    check_resp_single_record(resp, cecr, MatchType.SYMBOL)


def test_csf2ra(check_resp_single_record, csf2ra, hgnc):
    """Test that csf2ra normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:2435")
    check_resp_single_record(resp, csf2ra, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("CSF2RA")
    check_resp_single_record(resp, csf2ra, MatchType.SYMBOL)


def test_rps24p5(check_resp_single_record, rps24p5, hgnc):
    """Test that rps24p5 normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:36026")
    check_resp_single_record(resp, rps24p5, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("rpS24P5")
    check_resp_single_record(resp, rps24p5, MatchType.SYMBOL)


def test_trl_cag2_1(check_resp_single_record, trl_cag2_1, hgnc):
    """Test that trl_cag2_1 normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:34692")
    check_resp_single_record(resp, trl_cag2_1, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("TRL-CAG2-1")
    check_resp_single_record(resp, trl_cag2_1, MatchType.SYMBOL)


def test_myo5b(check_resp_single_record, myo5b, hgnc):
    """Test that myo5b normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:7603")
    check_resp_single_record(resp, myo5b, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("MYO5B")
    check_resp_single_record(resp, myo5b, MatchType.SYMBOL)

    # associated_with
    resp = hgnc.search("refseq:NM_001080467")
    check_resp_single_record(resp, myo5b, MatchType.ASSOCIATED_WITH)


def test_gstt1(check_resp_single_record, gstt1, hgnc):
    """Test that gstt1 normalizes to correct gene concept."""
    # Concept ID
    resp = hgnc.search("hgnc:4641")
    check_resp_single_record(resp, gstt1, MatchType.CONCEPT_ID)

    # Symbol
    resp = hgnc.search("GSTT1")
    check_resp_single_record(resp, gstt1, MatchType.SYMBOL)

    # associated_with
    resp = hgnc.search("omim:600436")
    check_resp_single_record(resp, gstt1, MatchType.ASSOCIATED_WITH)


def test_no_match(hgnc):
    """Test that a term normalizes to correct gene concept as a NO match."""
    resp = hgnc.search("A1BG - AS1")
    assert len(resp.records) == 0

    resp = hgnc.search("hnc:5")
    assert len(resp.records) == 0

    # Test empty query
    resp = hgnc.search("")
    assert len(resp.records) == 0

    # Do not search on label
    resp = hgnc.search("A1BG antisense RNA 1")
    assert len(resp.records) == 0


def test_meta_info(hgnc):
    """Test that the meta field is correct."""
    resp = hgnc.search("HGNC:37133")
    assert resp.source_meta_.data_license == "CC0"
    assert (
        resp.source_meta_.data_license_url == "https://www.genenames.org/about/license/"
    )
    assert datetime.datetime.now(tz=datetime.UTC).strptime(
        resp.source_meta_.version, "%Y%m%d"
    )
    assert resp.source_meta_.data_url == {
        "complete_set_archive": "ftp.ebi.ac.uk/pub/databases/genenames/hgnc/json/hgnc_complete_set.json"
    }
    assert resp.source_meta_.rdp_url is None
    assert resp.source_meta_.genome_assemblies == []
    assert resp.source_meta_.data_license_attributes == DataLicenseAttributes(
        non_commercial=False, share_alike=False, attribution=False
    )
