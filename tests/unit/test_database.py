"""Test DynamoDB"""
import pytest
from gene.database import Database
import json
import os
from pathlib import Path
from boto3.dynamodb.conditions import Key

TEST_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope='module')
def db():
    """Create a DynamoDB test fixture."""
    class DB:
        def __init__(self):
            self.db = Database()
            if os.environ.get('TEST') is not None:
                self.load_test_data()

        def load_test_data(self):
            with open(f'{TEST_ROOT}/tests/unit/'
                      f'data/genes.json', 'r') as f:
                genes = json.load(f)
                with self.db.genes.batch_writer() as batch:
                    for gene in genes:
                        batch.put_item(Item=gene)
                f.close()

            with open(f'{TEST_ROOT}/tests/unit/'
                      f'data/metadata.json', 'r') as f:
                metadata = json.load(f)
                with self.db.metadata.batch_writer() as batch:
                    for m in metadata:
                        batch.put_item(Item=m)
                f.close()

    return DB().db


def test_tables_created(db):
    """Check that gene_concepts and gene_metadata are created."""
    existing_tables = db.dynamodb_client.list_tables()['TableNames']
    assert 'gene_concepts' in existing_tables
    assert 'gene_metadata' in existing_tables


def test_item_type(db):
    """Check that items are tagged with item_type attribute."""
    filter_exp = Key('label_and_type').eq('ncbigene:43##identity')
    item = db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'identity'

    filter_exp = Key('label_and_type').eq('prkrap1##symbol')
    item = db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'symbol'

    filter_exp = Key('label_and_type').eq('a1bgas##prev_symbol')
    item = db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'prev_symbol'

    filter_exp = Key('label_and_type').eq('flj23569##alias')
    item = db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'alias'

    filter_exp = Key('label_and_type').eq('omim:606689##associated_with')
    item = db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'associated_with'

    filter_exp = Key('label_and_type').eq('ensembl:ensg00000097007##xref')
    item = db.genes.query(KeyConditionExpression=filter_exp)['Items'][0]
    assert 'item_type' in item
    assert item['item_type'] == 'xref'
