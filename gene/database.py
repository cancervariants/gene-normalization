"""This module creates the database."""
from enum import Enum
import abc
import atexit
import json

import sys
import logging
from os import environ
from typing import List, Optional, Dict, Any, Set

import click
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
import psycopg
from psycopg.errors import UniqueViolation

from gene import PREFIX_LOOKUP
from gene.schemas import SourceMeta, SourceName


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# can be set to either `Dev`, `Staging`, or `Prod`
# ONLY set when wanting to access aws instance
AWS_ENV_VAR_NAME = "GENE_NORM_ENV"

# Set to "true" if want to skip db confirmation check. Should ONLY be used for
# deployment needs
SKIP_AWS_DB_ENV_NAME = "SKIP_AWS_CONFIRMATION"


class AwsEnvName(str, Enum):
    """AWS environment name that is being used"""

    DEVELOPMENT = "Dev"
    STAGING = "Staging"
    PRODUCTION = "Prod"


VALID_AWS_ENV_NAMES = {v.value for v in AwsEnvName.__members__.values()}


def confirm_aws_db_use(env_name: str) -> None:
    """Check to ensure that AWS instance should actually be used."""
    if click.confirm(f"Are you sure you want to use the AWS {env_name} database?",
                     default=False):
        click.echo(f"***GENE AWS {env_name.upper()} DATABASE IN USE***")
    else:
        click.echo("Exiting.")
        sys.exit()


class DatabaseException(Exception):
    """Create custom class for handling database exceptions"""


class DatabaseInitializationException(DatabaseException):
    """Create custom exception for errors during DB connection initialization."""


class DatabaseReadException(DatabaseException):
    """Create custom exception for lookup/read errors"""


class DatabaseWriteException(DatabaseException):
    """Create custom exception for write errors"""


class AbstractDatabase(abc.ABC):
    """A database abstraction."""

    @abc.abstractmethod
    def __init__(self, db_url: Optional[str] = None, **db_args):
        """TODO

        :raise DatabaseInitializationException: if initial setup fails
        """
        pass

    @abc.abstractmethod
    def drop_db(self) -> None:
        """Initiate teardown of DB."""
        pass

    # @abc.abstractmethod
    # def is_initialized(self) -> bool:
    #     """Check that storage backend is set up."""
    #     pass

    @abc.abstractmethod
    def initialize_db(self) -> None:
        """Set up table -- create indices, etc TODO describe further"""
        pass

    @abc.abstractmethod
    def get_source_metadata(self, src_name: SourceName) -> Dict:
        """Todo

        src name == enum?
        """
        pass

    @abc.abstractmethod
    def get_record_by_id(self, concept_id: str, case_sensitive: bool = True,
                         merge: bool = False) -> Optional[Dict]:
        """Fetch record corresponding to provided concept ID
        :param str concept_id: concept ID for gene record
        :param bool case_sensitive: if true, performs exact lookup, which is
            more efficient. Otherwise, performs filter operation, which
            doesn't require correct casing.
        :param bool merge: if true, look for merged record; look for identity
            record otherwise.
        :return: complete gene record, if match is found; None otherwise
        """
        pass

    @abc.abstractmethod
    def get_records_by_type(self, query: str, match_type: str) -> List[Dict]:
        """TODO"""
        pass

    @abc.abstractmethod
    def get_all_concept_ids(self) -> Set[str]:
        """Retrieve concept IDs for use in generating normalized records.

        :return: List of concept IDs as strings.
        """
        pass

    @abc.abstractmethod
    def add_source_metadata(self, src_name: SourceName, data: SourceMeta) -> None:
        """TODO

        :raise DatabaseWriteException:
        """

    @abc.abstractmethod
    def add_record(self, record: Dict, record_type: str = "identity"):
        """Add new record to database.

        :param Dict record: record to upload
        :param str record_type: type of record (either 'identity' or 'merger')
        """
        pass

    @abc.abstractmethod
    def add_ref_record(self, term: str, concept_id: str, ref_type: str,
                       src_name: SourceName) -> None:
        """Add auxiliary/reference record to database.
        :param str term: referent term
        :param str concept_id: concept ID to refer to
        :param str ref_type: one of {'alias', 'label', 'xref', 'associated_with'}
        """
        pass

    @abc.abstractmethod
    def update_record(self, concept_id: str, field: str, new_value: Any,
                      item_type: str = 'identity'):
        """TODO"""
        pass

    @abc.abstractmethod
    def delete_normalized_concepts(self) -> None:
        """TODO

        :raise DatabaseReadException: if DB client requires separate read calls and
            encounters a failure in the process
        :raise DatabaseWriteException: if deletion call fails
        """
        pass

    @abc.abstractmethod
    def delete_source(self, src_name: SourceName) -> None:
        """TODO

        :raise DatabaseReadException: if DB client requires separate read calls and
            encounters a failure in the process
        :raise DatabaseWriteException: if deletion call fails
        """
        pass

    @abc.abstractmethod
    def complete_transaction(self) -> None:
        """Conclude transition or batch writing if relevant."""
        pass


class DynamoDbDatabase(AbstractDatabase):
    """The database class."""

    def __init__(self, db_url: Optional[str] = None, **db_args):
        """Initialize Database class.

        :param str db_url: URL endpoint for DynamoDB source
        :param str region_name: default AWS region
        """
        gene_concepts_table = "gene_concepts"  # default
        gene_metadata_table = "gene_metadata"  # default

        region_name = db_args.get("region_name", "us-east-2")

        if AWS_ENV_VAR_NAME in environ:
            if "GENE_TEST" in environ:
                raise DatabaseException(f"Cannot have both GENE_TEST and {AWS_ENV_VAR_NAME} set.")  # noqa: E501

            aws_env = environ[AWS_ENV_VAR_NAME]
            if aws_env not in VALID_AWS_ENV_NAMES:
                raise DatabaseException(f"{AWS_ENV_VAR_NAME} must be one of {VALID_AWS_ENV_NAMES}")  # noqa: E501

            skip_confirmation = environ.get(SKIP_AWS_DB_ENV_NAME)
            if (not skip_confirmation) or (skip_confirmation and skip_confirmation != "true"):  # noqa: E501
                confirm_aws_db_use(environ[AWS_ENV_VAR_NAME])

            boto_params = {
                "region_name": region_name
            }

            if aws_env == AwsEnvName.DEVELOPMENT:
                gene_concepts_table = "gene_concepts_nonprod"
                gene_metadata_table = "gene_metadata_nonprod"
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

        # Only create tables for local instance
        envs_do_not_create_tables = {AWS_ENV_VAR_NAME, "GENE_TEST"}
        if not set(envs_do_not_create_tables) & set(environ):
            self.initialize_db()

        self.genes = self.dynamodb.Table(gene_concepts_table)
        self.metadata = self.dynamodb.Table(gene_metadata_table)
        self.batch = self.genes.batch_writer()
        self._cached_sources = {}
        atexit.register(self.complete_transaction)

    def _get_table_names(self) -> List[str]:
        """Return names of tables in database.

        :return: Table names in DynamoDB
        """
        return self.dynamodb_client.list_tables()['TableNames']

    def drop_db(self) -> None:
        """Delete all tables from database."""
        existing_tables = self._get_table_names()
        for table_name in existing_tables:
            self.dynamodb.Table(table_name).delete()

    def _create_genes_table(self, existing_tables: List[str]):
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
                    },
                    {
                        'AttributeName': 'item_type',
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
                    },
                    {
                        'IndexName': 'item_type_index',
                        'KeySchema': [
                            {
                                'AttributeName': 'item_type',
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

    def _create_meta_data_table(self, existing_tables: List[str]) -> None:
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

    def initialize_db(self) -> None:
        """Create gene_concepts and gene_metadata tables."""
        existing_tables = self._get_table_names()
        self._create_genes_table(existing_tables)
        self._create_meta_data_table(existing_tables)

    def get_source_metadata(self, src_name: SourceName) -> Dict:
        """TODO

        this method should cache lookups
        """
        if src_name in self._cached_sources:
            return self._cached_sources[src_name]
        else:
            metadata = self.metadata.get_item(Key={"src_name": src_name}).get("Item")
            self._cached_sources[src_name] = metadata
            return metadata

    def get_record_by_id(self, concept_id: str,
                         case_sensitive: bool = True,
                         merge: bool = False) -> Optional[Dict]:
        """Fetch record corresponding to provided concept ID
        :param str concept_id: concept ID for gene record
        :param bool case_sensitive: if true, performs exact lookup, which is
            more efficient. Otherwise, performs filter operation, which
            doesn't require correct casing.
        :param bool merge: if true, look for merged record; look for identity
            record otherwise.
        :return: complete gene record, if match is found; None otherwise
        """
        try:
            if merge:
                pk = f'{concept_id.lower()}##merger'
            else:
                pk = f'{concept_id.lower()}##identity'
            if case_sensitive:
                match = self.genes.get_item(Key={
                    'label_and_type': pk,
                    'concept_id': concept_id
                })
                return match['Item']
            else:
                exp = Key('label_and_type').eq(pk)
                response = self.genes.query(KeyConditionExpression=exp)
                return response['Items'][0]
        except ClientError as e:
            logger.error(f"boto3 client error on get_records_by_id for "
                         f"search term {concept_id}: "
                         f"{e.response['Error']['Message']}")
            return None
        except (KeyError, IndexError):  # record doesn't exist
            return None

    def get_records_by_type(self, query: str,
                            match_type: str) -> List[Dict]:
        """Retrieve records for given query and match type.
        :param query: string to match against
        :param str match_type: type of match to look for. Should be one
            of {"symbol", "prev_symbol", "alias", "xref", "associated_with"}
            (use `get_record_by_id` for concept ID lookup)
        :return: list of matching records. Empty if lookup fails.
        """
        pk = f'{query}##{match_type.lower()}'
        filter_exp = Key('label_and_type').eq(pk)
        try:
            matches = self.genes.query(KeyConditionExpression=filter_exp)
            return matches.get('Items', None)
        except ClientError as e:
            logger.error(f"boto3 client error on get_records_by_type for "
                         f"search term {query}: "
                         f"{e.response['Error']['Message']}")
            return []

    def get_all_concept_ids(self) -> Set[str]:
        """Retrieve concept IDs for use in generating normalized records.

        :return: List of concept IDs as strings.
        """
        last_evaluated_key = None
        concept_ids = []
        params = {
            'ProjectionExpression': 'concept_id',
        }
        while True:
            if last_evaluated_key:
                response = self.genes.scan(
                    ExclusiveStartKey=last_evaluated_key, **params
                )
            else:
                response = self.genes.scan(**params)
            records = response['Items']
            for record in records:
                concept_ids.append(record['concept_id'])
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break
        return set(concept_ids)

    def add_source_metadata(self, src_name: SourceName, metadata: SourceMeta) -> None:
        """TODO

        :raise DatabaseWriteException:
        """
        metadata_item = metadata.dict()
        metadata_item["src_name"] = src_name.value
        try:
            self.metadata.put_item(Item=metadata_item)
        except ClientError as e:
            raise DatabaseWriteException(e)

    def add_record(self, record: Dict, record_type: str = "identity"):
        """Add new record to database.
        :param Dict record: record to upload
        :param str record_type: type of record (either 'identity' or 'merger')
        """
        id_prefix = record['concept_id'].split(':')[0].lower()
        record['src_name'] = PREFIX_LOOKUP[id_prefix]
        label_and_type = f'{record["concept_id"].lower()}##{record_type}'
        record['label_and_type'] = label_and_type
        record['item_type'] = record_type
        try:
            self.batch.put_item(
                Item=record,
                # ConditionExpression='attribute_not_exists(concept_id) AND attribute_not_exists(label_and_type)'  # noqa: E501
            )
        except ClientError as e:
            logger.error("boto3 client error on add_record for "
                         f"{record['concept_id']}: "
                         f"{e.response['Error']['Message']}")

    def add_ref_record(self, term: str, concept_id: str, ref_type: str,
                       src_name: SourceName) -> None:
        """Add auxiliary/reference record to database.
        :param str term: referent term
        :param str concept_id: concept ID to refer to
        :param str ref_type: one of {'alias', 'label', 'xref',
            'associated_with'}
        """
        label_and_type = f"{term.lower()}##{ref_type}"
        record = {
            "label_and_type": label_and_type,
            "concept_id": concept_id.lower(),
            "src_name": src_name.value,
            "item_type": ref_type,
        }
        try:
            self.batch.put_item(Item=record)
        except ClientError as e:
            logger.error(f"boto3 client error adding reference {term} for "
                         f"{concept_id} with match type {ref_type}: "
                         f"{e.response['Error']['Message']}")

    def update_record(self, concept_id: str, field: str, new_value: Any,
                      item_type: str = 'identity'):
        """Update the field of an individual record to a new value.
        :param str concept_id: record to update
        :param str field: name of field to update
        :param str new_value: new value
        :param str item_type: record type, one of {'identity', 'merger'}
        """
        key = {
            'label_and_type': f'{concept_id.lower()}##{item_type}',
            'concept_id': concept_id
        }
        update_expression = f"set {field}=:r"
        update_values = {':r': new_value}
        try:
            self.genes.update_item(Key=key,
                                   UpdateExpression=update_expression,
                                   ExpressionAttributeValues=update_values)
        except ClientError as e:
            logger.error(f"boto3 client error in `database.update_record()`: "
                         f"{e.response['Error']['Message']}")

    def delete_normalized_concepts(self) -> None:
        """TODO

        :raise DatabaseReadException: if DDB raises ClientError while acquiring
            records to delete
        :raise DatabaseWriteException: if DDB raises ClientError during deletion
        """
        while True:
            with self.genes.batch_writer(
                overwrite_by_pkeys=["label_and_type", "concept_id"]
            ) as batch:
                try:
                    response = self.genes.query(
                        IndexName="item_type_index",
                        KeyConditionExpression=Key("item_type").eq("merger"),
                    )
                except ClientError as e:
                    raise DatabaseReadException(e)
                records = response["Items"]
                if not records:
                    break
                for record in records:
                    batch.delete_item(Key={
                        "label_and_type": record["label_and_type"],
                        "concept_id": record["concept_id"]
                    })

    def delete_source(self, src_name: SourceName) -> None:
        """TODO"""
        while True:
            try:
                response = self.genes.query(
                    IndexName="src_index",
                    KeyConditionExpression=Key("src_name").eq(
                        src_name.value
                    )
                )
            except ClientError as e:
                raise DatabaseReadException(e)
            records = response["Items"]
            if not records:
                break
            with self.genes.batch_writer(
                overwrite_by_pkeys=["label_and_type", "concept_id"]
            ) as batch:
                for record in records:
                    try:
                        batch.delete_item(Key={
                            "label_and_type": record["label_and_type"],
                            "concept_id": record["concept_id"]
                        })
                    except ClientError as e:
                        raise DatabaseWriteException(e)

        try:
            self.metadata.delete_item(Key={
                "src_name": src_name.value
            })
        except ClientError as e:
            raise DatabaseWriteException(e)

    def complete_transaction(self):
        """Flush internal batch_writer."""
        self.batch.__exit__(*sys.exc_info())
        self.batch = self.genes.batch_writer()


class PostgresDatabase(AbstractDatabase):
    """TODO"""

    def __init__(self, db_url: Optional[str] = None, **db_args):
        """TODO

        :raise DatabaseInitializationException: if initial setup fails
        """
        # TODO user should provide connection parameters
        self._db_name = "gene_normalizer"
        self.conn = psycopg.connect(f"dbname={self._db_name} user=postgres")
        self.initialize_db()
        self._reset_ref_record_queue()
        self._cached_sources = {}

        atexit.register(self.complete_transaction)

    def _reset_ref_record_queue(self) -> None:
        """TODO"""
        self._ref_record_queue = {
            "alias": [],
            "xref": [],
            "associated_with": [],
            "prev_symbol": [],
            "symbol": [],  # TODO
        }

    def drop_db(self) -> None:
        """Initiate teardown of DB."""
        pass

    def initialize_db(self) -> None:
        """Set up table -- create indices, etc TODO describe further"""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_type = 'BASE TABLE' AND table_schema = 'public'"
            )
            tables = [t[0] for t in cur.fetchall()]

        if "gene_concepts" not in tables:
            self._create_tables()

    def _create_tables(self) -> None:
        """TODO

        * create indexes/views/something?
        """
        sources_table = """
        CREATE TABLE gene_sources (
            name VARCHAR(127) PRIMARY KEY,
            data_license TEXT NOT NULL,
            data_license_url TEXT NOT NULL,
            version TEXT NOT NULL,
            data_url TEXT NOT NULL,
            rdp_url TEXT,
            data_license_nc BOOLEAN NOT NULL,
            data_license_attr BOOLEAN NOT NULL,
            data_license_sa BOOLEAN NOT NULL,
            genome_assemblies TEXT [] NOT NULL
        );
        """

        merged_table = """
        CREATE TABLE gene_merged (
            concept_id VARCHAR(127) PRIMARY KEY,
            symbol TEXT,
            symbol_status VARCHAR(127),
            previous_symbols TEXT [],
            label TEXT,
            strand VARCHAR(1),
            location_annotations TEXT [],
            locations JSON [],
            gene_type TEXT
            ensembl_locations JSON [],
            hgnc_locations JSON [],
            ncbi_locations JSON [],
            ensembl_biotype TEXT,
            hgnc_locus_type TEXT,
            ncbi_gene_type TEXT,
            aliases TEXT [],
            associated_with TEXT [],
            xrefs TEXT [],
        )
        """

        concepts_table = """
        CREATE TABLE gene_concepts (
            concept_id VARCHAR(127) PRIMARY KEY,
            source VARCHAR(127) NOT NULL REFERENCES gene_sources (name)
                ON DELETE CASCADE,
            symbol_status VARCHAR(127),
            label TEXT,
            strand VARCHAR(1),
            location_annotations TEXT [],
            locations JSON [],
            gene_type TEXT,
            merged_id VARCHAR(127) REFERENCES gene_merged (concept_id)
        );
        CREATE INDEX idx_gc_source ON gene_concepts (source);
        CREATE INDEX idx_gc_merged ON gene_concepts (merged_id);
        """

        symbols_table = """
        CREATE TABLE gene_symbols (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            concept_id VARCHAR(127) REFERENCES gene_concepts (concept_id)
                ON DELETE CASCADE
        );
        CREATE INDEX idx_gs_concept ON gene_symbols (concept_id);
        """

        previous_symbols_table = """
        CREATE TABLE gene_previous_symbols (
            id SERIAL PRIMARY KEY,
            previous_symbol TEXT NOT NULL,
            concept_id VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
                ON DELETE CASCADE
        );
        CREATE INDEX idx_gps_concept ON gene_previous_symbols (concept_id);
        """

        aliases_table = """
        CREATE TABLE gene_aliases (
            id SERIAL PRIMARY KEY,
            alias TEXT NOT NULL,
            concept_id VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
                ON DELETE CASCADE
        );
        CREATE INDEX idx_ga_concept ON gene_aliases (concept_id);
        """

        xrefs_table = """
        CREATE TABLE gene_xrefs (
            id SERIAL PRIMARY KEY,
            xref TEXT NOT NULL,
            concept_id VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
                ON DELETE CASCADE
        );
        CREATE INDEX idx_gx_concept ON gene_xrefs (concept_id);
        """

        assoc_table = """
        CREATE TABLE gene_associations (
            id SERIAL PRIMARY KEY,
            assoc_with TEXT NOT NULL,
            concept_ID VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
                ON DELETE CASCADE
        );
        CREATE INDEX idx_g_as_concept ON gene_associations (concept_id);
        """

        with self.conn.cursor() as cur:
            cur.execute(sources_table)
            cur.execute(merged_table)
            cur.execute(concepts_table)
            cur.execute(symbols_table)
            cur.execute(previous_symbols_table)
            cur.execute(aliases_table)
            cur.execute(xrefs_table)
            cur.execute(assoc_table)
            self.conn.commit()

    def get_source_metadata(self, src_name: SourceName) -> Dict:
        """Todo"""
        if src_name in self._cached_sources:
            return self._cached_sources[src_name]

        metadata_query = "SELECT * FROM gene_sources WHERE name = %s;"
        with self.conn.cursor() as cur:
            cur.execute(metadata_query, [src_name.value])
            metadata_result = cur.fetchone()
            if not metadata_result:
                raise DatabaseReadException(f"{src_name.value} metadata lookup failed")
            metadata = {
                "data_license": metadata_result[1],
                "data_license_url": metadata_result[2],
                "version": metadata_result[3],
                "data_url": metadata_result[4],
                "rdp_url": metadata_result[5],
                "data_license_attributes": {
                    "non_commercial": metadata_result[6],
                    "attribution": metadata_result[7],
                    "share_alike": metadata_result[8],
                },
                "genome_assemblies": metadata_result[9]
            }
            self._cached_sources[src_name] = metadata
            return metadata

    def get_record_by_id(self, concept_id: str, case_sensitive: bool = True,
                         merge: bool = False) -> Optional[Dict]:
        """Fetch record corresponding to provided concept ID
        :param str concept_id: concept ID for gene record
        :param bool case_sensitive: if true, performs exact lookup, which is
            more efficient. Otherwise, performs filter operation, which
            doesn't require correct casing.
        :param bool merge: if true, look for merged record; look for identity
            record otherwise.
        :return: complete gene record, if match is found; None otherwise
        """
        if merge:
            pass  # TODO
        else:
            query = ""
            print(query)

    def get_records_by_type(self, query: str, match_type: str) -> List[Dict]:
        """TODO"""
        pass

    def get_all_concept_ids(self) -> Set[str]:
        """Retrieve concept IDs for use in generating normalized records.

        :return: List of concept IDs as strings.
        """
        ids_query = "SELECT concept_id FROM gene_concepts;"
        with self.conn.cursor() as cur:
            cur.execute(ids_query)
            ids_tuple = cur.fetchall()
        return {i[0] for i in ids_tuple}

    def add_source_metadata(self, src_name: SourceName, meta: SourceMeta) -> None:
        """TODO"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO gene_sources(
                    name, data_license, data_license_url, version, data_url, rdp_url,
                    data_license_nc, data_license_attr, data_license_sa,
                    genome_assemblies
                )
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s );
                """,
                [
                    src_name, meta.data_license, meta.data_license_url, meta.version,
                    meta.data_url, meta.rdp_url,
                    meta.data_license_attributes["non_commercial"],
                    meta.data_license_attributes["attribution"],
                    meta.data_license_attributes["share_alike"],
                    meta.genome_assemblies
                ]
            )
        self.conn.commit()

    def add_record(self, record: Dict, record_type: str = "identity"):
        """Add new record to database.

        :param Dict record: record to upload
        :param str record_type: type of record (either 'identity' or 'merger')
        """
        record_query = """
            INSERT INTO gene_concepts (
                concept_id, source, symbol_status, label,
                strand, location_annotations, locations, gene_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """

        insert_symbol = "INSERT INTO gene_symbols (symbol, concept_id) VALUES (%s, %s)"
        insert_prev_symbol = "INSERT INTO gene_previous_symbols (previous_symbol, concept_id) VALUES (%s, %s)"  # noqa: E501
        insert_alias = "INSERT INTO gene_aliases (alias, concept_id) VALUES (%s, %s)"
        insert_xref = "INSERT INTO gene_xrefs (xref, concept_id) VALUES (%s, %s)"
        insert_assoc = "INSERT INTO gene_associations (assoc_with, concept_id) VALUES (%s, %s)"  # noqa: E501

        concept_id = record["concept_id"]
        locations = [json.dumps(loc) for loc in record.get("locations", [])]
        with self.conn.cursor() as cur:
            try:
                cur.execute(record_query, [
                    concept_id, record["src_name"], record.get("symbol_status"),
                    record.get("label"), record.get("strand"),
                    record.get("location_annotations"),
                    locations,
                    record.get("gene_type")
                ])
            except UniqueViolation:  # TODO debugging
                print(record)
                self.conn.rollback()
            else:
                for a in self._ref_record_queue["alias"]:
                    cur.execute(insert_alias, [a, concept_id])
                for x in self._ref_record_queue["xref"]:
                    cur.execute(insert_xref, [x, concept_id])
                for a in self._ref_record_queue["associated_with"]:
                    cur.execute(insert_assoc, [a, concept_id])
                for p in self._ref_record_queue["prev_symbol"]:
                    cur.execute(insert_prev_symbol, [p, concept_id])
                if self._ref_record_queue["symbol"]:
                    cur.execute(
                        insert_symbol, [self._ref_record_queue["symbol"][0], concept_id]
                    )
                self.conn.commit()
        self._reset_ref_record_queue()

    def add_ref_record(self, term: str, concept_id: str, ref_type: str,
                       src_name: SourceName) -> None:
        """Add auxiliary/reference record to database.

        TODO
        * sort of a janky solution here, not actually sure if necessary
        * should just make this method a stub and extract all values in `add_record()`


        :param str term: referent term
        :param str concept_id: concept ID to refer to
        :param str ref_type: one of {'alias', 'label', 'xref',
            'associated_with'}
        """
        self._ref_record_queue[ref_type].append(term)

    def update_record(self, concept_id: str, field: str, new_value: Any,
                      item_type: str = 'identity') -> None:
        """TODO"""
        pass

    def delete_normalized_concepts(self) -> None:
        """TODO

        :raise DatabaseReadException: if DB client requires separate read calls and
            encounters a failure in the process
        :raise DatabaseWriteException: if deletion call fails
        """
        pass

    def delete_source(self, src_name: SourceName) -> None:
        """TODO

        :raise DatabaseReadException: if DB client requires separate read calls and
            encounters a failure in the process
        :raise DatabaseWriteException: if deletion call fails
        """
        drop_source_query = "DELETE FROM gene_sources gs WHERE gs.name = %s;"

        with self.conn.cursor() as cur:
            cur.execute(drop_source_query, [src_name.value])
            self.conn.commit()

    def complete_transaction(self) -> None:
        """Conclude transition or batch writing if relevant.

        TODO
        * should double check if connection should be closed here -- seems to be
            handled by uvicorn?
        """
        if not self.conn.closed:
            self.conn.commit()
            self.conn.close()
