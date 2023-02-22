"""Test DynamoDB and ETL methods."""
import shutil
from os import environ
from pathlib import Path

import pytest
from boto3.dynamodb.conditions import Key
from mock import patch

from gene.etl import Ensembl, HGNC, NCBI
from gene.etl.merge import Merge
from gene.database import AWS_ENV_VAR_NAME
from gene.database.dynamodb import DynamoDbDatabase


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
    "NT_167249.2": ["ga4gh:SQ.Q8IworEhpLeXwpz1CHM7C3luysh-ltx-"]
}


@pytest.fixture(scope='module')
def is_test_env():
    """Test fixture to determine whether or not using test environment."""
    return environ.get("GENE_TEST", "").lower() == "true"


@pytest.fixture(scope='module')
def dynamodb(is_test_env):
    """Create a DynamoDB test fixture."""
    class DB:
        def __init__(self):
            self.db = DynamoDbDatabase()
            self.merge = Merge(database=self.db)
            if is_test_env and AWS_ENV_VAR_NAME not in environ:
                self.db.drop_db()
                self.db.initialize_db()
    return DB()


@pytest.fixture(scope='module')
def processed_ids():
    """Create a test fixture to store processed ids for merged concepts."""
    return list()


def _get_aliases(sr, seqid):
    """Monkey patch get aliases method

    :param SeqRepo sr: seqrepo instance
    :param str seqid: Sequence ID accession
    :return: List of aliases for seqid
    """
    return ALIASES[seqid]


@pytest.fixture(scope='module')
def etl_data_path():
    """Create a test fixture to return etl data path."""
    test_root = Path(__file__).resolve().parents[2]
    return test_root / 'tests' / 'unit' / 'data' / 'etl_data'


def test_tables_created(dynamodb):
    """Check that gene_concepts and gene_metadata are created."""
    existing_tables = dynamodb.db.dynamodb_client.list_tables()['TableNames']
    assert 'gene_concepts' in existing_tables
    assert 'gene_metadata' in existing_tables


@patch.object(Ensembl, 'get_seqrepo')
def test_ensembl_etl(test_get_seqrepo, processed_ids, dynamodb, etl_data_path,
                     is_test_env):
    """Test that ensembl etl methods work correctly."""
    if is_test_env:
        test_get_seqrepo.return_value = None
        e = Ensembl(dynamodb.db)

        e.src_data_dir = etl_data_path / 'ensembl'
        e._download_data()
        e._extract_data()
        shutil.rmtree(e.src_data_dir)

        e._sequence_location.get_aliases = _get_aliases
        e._data_src = etl_data_path / 'ensembl_109.gff3'
        e._transform_data()
        e._add_meta()
        processed_ids += e._processed_ids


@patch.object(HGNC, 'get_seqrepo')
def test_hgnc_etl(test_get_seqrepo, processed_ids, dynamodb, etl_data_path,
                  is_test_env):
    """Test that hgnc etl methods work correctly."""
    if is_test_env:
        test_get_seqrepo.return_value = None
        h = HGNC(dynamodb.db)

        h.src_data_dir = etl_data_path / 'hgnc'
        h._download_data()
        h._extract_data()
        shutil.rmtree(h.src_data_dir)

        h._data_src = etl_data_path / 'hgnc_20210810.json'
        h._version = '20210810'
        h._transform_data()
        h._add_meta()
        processed_ids += h._processed_ids


@patch.object(NCBI, 'get_seqrepo')
def test_ncbi_etl(test_get_seqrepo, processed_ids, dynamodb, etl_data_path,
                  is_test_env):
    """Test that ncbi etl methods work correctly."""
    if is_test_env:
        test_get_seqrepo.return_value = None
        n = NCBI(dynamodb.db)

        n.src_data_dir = etl_data_path / 'ncbi'
        n._extract_data()
        shutil.rmtree(n.src_data_dir)

        n._sequence_location.get_aliases = _get_aliases
        n._info_src = etl_data_path / 'ncbi_info_20210813.tsv'
        n._history_src = etl_data_path / 'ncbi_history_20210813.tsv'
        n._gff_src = etl_data_path / 'ncbi_GRCh38.p14.gff'
        n._version = n._info_src.stem.split('_')[-1]
        n._transform_data()
        n._add_meta()
        processed_ids += n._processed_ids


def test_merged_conecpts(processed_ids, dynamodb, is_test_env):
    """Create merged concepts and load to db."""
    if is_test_env:
        dynamodb.merge.create_merged_concepts(processed_ids)


def test_item_type(dynamodb):
    """Check that items are tagged with item_type attribute."""
    filter_exp = Key('label_and_type').eq('ncbigene:8193##identity')
    item = \
        dynamodb.db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'identity'

    filter_exp = Key('label_and_type').eq('prkrap1##symbol')
    item = \
        dynamodb.db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'symbol'

    filter_exp = Key('label_and_type').eq('loc157663##prev_symbol')
    item = \
        dynamodb.db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'prev_symbol'

    filter_exp = Key('label_and_type').eq('flj23569##alias')
    item = \
        dynamodb.db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'alias'

    filter_exp = Key('label_and_type').eq('omim:606689##associated_with')
    item = \
        dynamodb.db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'associated_with'

    filter_exp = Key('label_and_type').eq('ensembl:ensg00000268895##xref')
    item = \
        dynamodb.db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'xref'
