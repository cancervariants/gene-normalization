"""Test DynamoDB"""
import pytest
from gene.database import Database
from gene import PROJECT_ROOT
import json
import os


@pytest.fixture(scope='module')
def db():
    """Create a DynamoDB test fixture."""
    class DB:
        def __init__(self):
            self.db = Database(db_url=os.environ['GENE_NORM_DB_URL'])
            if os.environ.get('TEST') is not None:
                self.load_test_data()

        def load_test_data(self):
            with open(f'{PROJECT_ROOT}/tests/unit/'
                      f'data/genes.json', 'r') as f:
                genes = json.load(f)
                with self.db.genes.batch_writer() as batch:
                    for gene in genes:
                        batch.put_item(Item=gene)
                f.close()

            with open(f'{PROJECT_ROOT}/tests/unit/'
                      f'data/metadata.json', 'r') as f:
                metadata = json.load(f)
                with self.db.metadata.batch_writer() as batch:
                    for m in metadata:
                        batch.put_item(Item=m)
                f.close()

    return DB().db


def test_tables_created(db):
    """Check that gene_concepts and gene_metadata are created."""
    existing_tables = db.ddb_client.list_tables()['TableNames']
    assert 'gene_concepts' in existing_tables
    assert 'gene_metadata' in existing_tables
