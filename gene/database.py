"""This module creates the database."""
import boto3

DYNAMODB = boto3.resource('dynamodb', endpoint_url="http://localhost:8001")
DYNAMODBCLIENT = \
    boto3.client('dynamodb', endpoint_url="http://localhost:8001")
GENES_TABLE = DYNAMODB.Table('gene_concepts')
METADATA_TABLE = DYNAMODB.Table('gene_metadata')
cached_sources = dict()


class Database:
    """The database class."""

    def __init__(self, *args, **kwargs):
        """Initialize Database class."""
        existing_tables = DYNAMODBCLIENT.list_tables()['TableNames']
        self.create_genes_table(DYNAMODB, existing_tables)
        self.create_meta_data_table(DYNAMODB, existing_tables)

    def create_genes_table(self, dynamodb, existing_tables):
        """Create Genes table if not exists."""
        table_name = 'gene_concepts'
        if table_name not in existing_tables:
            dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'label_and_type',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'concept_id',
                        'KeyType': 'RANGE'  # Sort key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'label_and_type',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'concept_id',
                        'AttributeType': 'S'
                    },
                    {
                        'AttributeName': 'src_name',
                        'AttributeType': 'S'
                    }

                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'src_index',
                        'KeySchema': [
                            {
                                'AttributeName': 'src_name',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'KEYS_ONLY'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 10,
                            'WriteCapacityUnits': 10
                        }
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )

    def create_meta_data_table(self, dynamodb, existing_tables):
        """Create MetaData table if not exists."""
        table_name = 'gene_metadata'
        if table_name not in existing_tables:
            dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'src_name',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'src_name',
                        'AttributeType': 'S'
                    },
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
