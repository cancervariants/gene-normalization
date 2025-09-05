"""Test DynamoDB and ETL methods."""

from os import environ
from pathlib import Path
from unittest.mock import patch

import pytest
from boto3.dynamodb.conditions import Key

from gene.config import get_config
from gene.database import AWS_ENV_VAR_NAME
from gene.etl import HGNC, NCBI, Ensembl
from gene.etl.merge import Merge
from gene.schemas import RecordType

IS_DDB_TEST = not get_config().db_url.startswith("postgres")
ALIASES = {
    "NC_000001.11": ["ga4gh:SQ.Ya6Rs7DHhDeg7YaOSg1EoNi3U_nQ9SvO"],
    "NC_000002.12": ["ga4gh:SQ.pnAqCRBrTsUoBghSD1yp_jXWSmlbdh4g"],
    "NC_000003.12": ["ga4gh:SQ.Zu7h9AggXxhTaGVsy7h_EZSChSZGcmgX"],
    "NC_000007.14": ["ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"],
    "NC_000009.12": ["ga4gh:SQ.KEO-4XBcm1cxeo_DIQ8_ofqGUkp4iZhI"],
    "NC_000011.10": ["ga4gh:SQ.2NkFm8HK88MqeNkCgj78KidCAXgnsfV1"],
    "NC_000015.10": ["ga4gh:SQ.AsXvWL1-2i5U_buw6_niVIxD6zTbAuS6"],
    "NC_000017.11": ["ga4gh:SQ.dLZ15tNO1Ur0IcGjwc3Sdi_0A6Yf4zm7"],
    "NC_000019.10": ["ga4gh:SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl"],
    "NC_000023.11": ["ga4gh:SQ.w0WZEvgJF0zf_P4yyTzjjv9oW1z61HHP"],
    "NC_000008.11": ["ga4gh:SQ.209Z7zJ-mFypBEWLk4rNC6S_OxY5p7bs"],
    "NC_000012.12": ["ga4gh:SQ.6wlJpONE3oNb4D69ULmEXhqyDZ4vwNfl"],
    "NC_000024.10": ["ga4gh:SQ.8_liLu1aycC0tPQPFmUaGXJLDs5SbPZ5"],
    "NT_167246.2": ["ga4gh:SQ.MjujHSAsgNWRTX4w3ysM7b5OVhZpdXu1"],
    "NT_167249.2": ["ga4gh:SQ.Q8IworEhpLeXwpz1CHM7C3luysh-ltx-"],
}


@pytest.fixture(scope="module")
def db_fixture(database):
    """Create a database test fixture."""

    class DB:
        def __init__(self):
            self.db = database
            self.db_name = self.db.__class__.__name__
            self.merge = Merge(database=self.db)
            if get_config().test and AWS_ENV_VAR_NAME not in environ:
                self.db.drop_db()
                self.db.initialize_db()

    return DB()


@pytest.fixture(scope="module")
def processed_ids():
    """Create a test fixture to store processed ids for merged concepts."""
    return []


def _get_aliases(seqid):
    """Monkey patch get aliases method

    :param str seqid: Sequence ID accession
    :return: List of aliases for seqid
    """
    return ALIASES[seqid]


@pytest.fixture(scope="module")
def etl_data_path(test_data_dir: Path):
    """Create a test fixture to return etl data path."""
    return test_data_dir / "etl_data"


def test_tables_created(db_fixture):
    """Check that requisite tables are created."""
    existing_tables = db_fixture.db.list_tables()
    if db_fixture.db_name == "PostgresDatabase":
        assert set(existing_tables) == {
            "gene_associations",
            "gene_symbols",
            "gene_previous_symbols",
            "gene_aliases",
            "gene_xrefs",
            "gene_concepts",
            "gene_merged",
            "gene_sources",
        }
    else:
        assert db_fixture.db.gene_table in existing_tables


@pytest.mark.skipif(not get_config().test, reason="not in test environment")
@patch.object(Ensembl, "get_seqrepo")
def test_ensembl_etl(test_get_seqrepo, processed_ids, db_fixture, etl_data_path):
    """Test that ensembl etl methods work correctly."""
    test_get_seqrepo.return_value = None
    e = Ensembl(db_fixture.db, data_path=etl_data_path)
    e._get_seq_id_aliases = _get_aliases
    ensembl_ids = e.perform_etl(use_existing=True)
    processed_ids += ensembl_ids


@pytest.mark.skipif(not get_config().test, reason="not in test environment")
@patch.object(HGNC, "get_seqrepo")
def test_hgnc_etl(test_get_seqrepo, processed_ids, db_fixture, etl_data_path):
    """Test that hgnc etl methods work correctly."""
    test_get_seqrepo.return_value = None
    h = HGNC(db_fixture.db, data_path=etl_data_path)
    hgnc_ids = h.perform_etl(use_existing=True)
    processed_ids += hgnc_ids


@pytest.mark.skipif(not get_config().test, reason="not in test environment")
@patch.object(NCBI, "get_seqrepo")
def test_ncbi_etl(test_get_seqrepo, processed_ids, db_fixture, etl_data_path):
    """Test that ncbi etl methods work correctly."""
    test_get_seqrepo.return_value = None
    n = NCBI(db_fixture.db, data_path=etl_data_path)
    n._get_seq_id_aliases = _get_aliases
    ncbi_ids = n.perform_etl(use_existing=True)
    processed_ids += ncbi_ids


@pytest.mark.skipif(not get_config().test, reason="not in test environment")
def test_merged_concepts(processed_ids, db_fixture):
    """Create merged concepts and load to db."""
    db_fixture.merge.create_merged_concepts(processed_ids)


@pytest.mark.skipif(not IS_DDB_TEST, reason="only applies to DynamoDB in test env")
def test_item_type(db_fixture):
    """Check that items are tagged with item_type attribute."""
    filter_exp = Key("label_and_type").eq("ncbigene:8193##identity")
    item = db_fixture.db.genes.query(KeyConditionExpression=filter_exp)["Items"][0]
    assert "item_type" in item
    assert item["item_type"] == "identity"

    filter_exp = Key("label_and_type").eq("prkrap1##symbol")
    item = db_fixture.db.genes.query(KeyConditionExpression=filter_exp)["Items"][0]
    assert "item_type" in item
    assert item["item_type"] == "symbol"

    filter_exp = Key("label_and_type").eq("loc157663##prev_symbol")
    item = db_fixture.db.genes.query(KeyConditionExpression=filter_exp)["Items"][0]
    assert "item_type" in item
    assert item["item_type"] == "prev_symbol"

    filter_exp = Key("label_and_type").eq("flj23569##alias")
    item = db_fixture.db.genes.query(KeyConditionExpression=filter_exp)["Items"][0]
    assert "item_type" in item
    assert item["item_type"] == "alias"

    filter_exp = Key("label_and_type").eq("omim:606689##associated_with")
    item = db_fixture.db.genes.query(KeyConditionExpression=filter_exp)["Items"][0]
    assert "item_type" in item
    assert item["item_type"] == "associated_with"

    filter_exp = Key("label_and_type").eq("ensembl:ensg00000268895##xref")
    item = db_fixture.db.genes.query(KeyConditionExpression=filter_exp)["Items"][0]
    assert "item_type" in item
    assert item["item_type"] == "xref"


@pytest.mark.skipif(not get_config().test, reason="not in test environment")
def test_get_all_records(db_fixture):
    """Basic test of get_all_records method.

    It's probably overkill (and unmaintainable) to do exact checks against every
    record, but fairly easy to check against expected counts and ensure that nothing
    is getting sent twice.
    """
    source_records = list(db_fixture.db.get_all_records(RecordType.IDENTITY))
    assert len(source_records) == 63
    source_ids = {r["concept_id"] for r in source_records}
    assert len(source_ids) == 63

    normalized_records = list(db_fixture.db.get_all_records(RecordType.MERGER))
    assert len(normalized_records) == 46
    normalized_ids = {r["concept_id"] for r in normalized_records}
    assert len(normalized_ids) == 46
