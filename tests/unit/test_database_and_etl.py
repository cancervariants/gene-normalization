"""Test DynamoDB and ETL methods."""
import pytest
from gene.etl import Ensembl, HGNC, NCBI
from gene.etl.merge import Merge
from gene.database import Database
import os
from pathlib import Path
from boto3.dynamodb.conditions import Key


@pytest.fixture(scope='module')
def is_test_env():
    """Test fixture to determine whether or not using test environment."""
    return os.environ.get('TEST') is not None


@pytest.fixture(scope='module')
def dynamodb(is_test_env):
    """Create a DynamoDB test fixture."""
    class DB:
        def __init__(self):
            self.db = Database()
            self.merge = Merge(database=self.db)
            if is_test_env:
                self.db.delete_all_db_tables()
                self.db.create_db_tables()
    return DB()


@pytest.fixture(scope='module')
def processed_ids():
    """Create a test fixture to store processed ids for merged concepts."""
    return list()


@pytest.fixture(scope='module')
def etl_data_path():
    """Create a test fixture to return etl data path."""
    project_root = Path().resolve().parents[1]
    return project_root / 'tests' / 'unit' / 'data' / 'etl_data'


def test_tables_created(dynamodb):
    """Check that gene_concepts and gene_metadata are created."""
    existing_tables = dynamodb.db.dynamodb_client.list_tables()['TableNames']
    assert 'gene_concepts' in existing_tables
    assert 'gene_metadata' in existing_tables


def test_ensembl_transform(processed_ids, dynamodb, etl_data_path,
                           is_test_env):
    """Test ensembl transform method."""
    if is_test_env:
        e = Ensembl(dynamodb.db)
        e._data_src = etl_data_path / 'ensembl_104.gff3'
        e._transform_data()
        e._add_meta()
        processed_ids += e._processed_ids


def test_hgnc_transform(processed_ids, dynamodb, etl_data_path, is_test_env):
    """Test hgnc transform method."""
    if is_test_env:
        h = HGNC(dynamodb.db)
        h._data_src = etl_data_path / 'hgnc_20210810.json'
        h._version = '20210810'
        h._transform_data()
        h._add_meta()
        processed_ids += h._processed_ids


def test_ncbi_transform(processed_ids, dynamodb, etl_data_path, is_test_env):
    """Test ncbi transform method."""
    if is_test_env:
        n = NCBI(dynamodb.db)
        n._info_src = etl_data_path / 'ncbi_info_20210813.tsv'
        n._history_src = etl_data_path / 'ncbi_history_20210813.tsv'
        n._gff_src = etl_data_path / 'ncbi_GRCh38.p13.gff'
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
    filter_exp = Key('label_and_type').eq('ncbigene:43##identity')
    item = \
        dynamodb.db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'identity'

    filter_exp = Key('label_and_type').eq('prkrap1##symbol')
    item = \
        dynamodb.db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'symbol'

    filter_exp = Key('label_and_type').eq('a1bgas##prev_symbol')
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

    filter_exp = Key('label_and_type').eq('ensembl:ensg00000097007##xref')
    item = \
        dynamodb.db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'xref'
