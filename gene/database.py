"""This module creates the database."""
import boto3
from os import environ
from typing import List
import click
import sys


class Database:
    """The database class."""

    def __init__(self, db_url: str = '', region_name: str = 'us-east-2'):
        """Initialize Database class.

        :param str db_url: URL endpoint for DynamoDB source
        :param str region_name: default AWS region
        """
        if 'GENE_NORM_PROD' in environ or 'GENE_NORM_EB_PROD' in environ:
            boto_params = {
                'region_name': region_name
            }
            if 'GENE_NORM_EB_PROD' not in environ:
                # EB Instance should not have to confirm.
                # This is used only for updating production via CLI
                if click.confirm("Are you sure you want to use the "
                                 "production database?", default=False):
                    click.echo("***GENE PRODUCTION DATABASE IN USE***")
                else:
                    click.echo("Exiting.")
                    sys.exit()
        else:
            if db_url:
                endpoint_url = db_url
            elif 'GENE_NORM_DB_URL' in environ:
                endpoint_url = environ['GENE_NORM_DB_URL']
            else:
                endpoint_url = 'http://localhost:8000'
            click.echo(f"***Using Gene Database Endpoint: {endpoint_url}***")
            boto_params = {
                'region_name': region_name,
                'endpoint_url': endpoint_url
            }

        self.dynamodb = boto3.resource('dynamodb', **boto_params)
        self.dynamodb_client = boto3.client('dynamodb', **boto_params)

        # Create tables if nonexistent if not connecting to production database
        if 'GENE_NORM_PROD' not in environ and\
                'GENE_NORM_EB_PROD' not in environ:
            existing_tables = self.dynamodb_client.list_tables()['TableNames']
            self.create_genes_table(existing_tables)
            self.create_meta_data_table(existing_tables)

        self.genes = self.dynamodb.Table('gene_concepts')
        self.metadata = self.dynamodb.Table('gene_metadata')
        self.cached_sources = {}

    def create_genes_table(self, existing_tables: List[str]):
        """Create Genes table if non-existent.

        :param List[str] existing_tables: table names already in DB
        """
        table_name = 'gene_concepts'
        if table_name not in existing_tables:
            self.dynamodb.create_table(
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

    def create_meta_data_table(self, existing_tables: List[str]):
        """Create MetaData table if non-existent.

        :param List[str] existing_tables: table names already in DB
        """
        table_name = 'gene_metadata'
        if table_name not in existing_tables:
            self.dynamodb.create_table(
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
