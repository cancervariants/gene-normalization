"""Provide DynamoDB client."""
import atexit
import logging
import sys
from os import environ
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Set, Union

import boto3
import click
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from gene.database.database import (
    AWS_ENV_VAR_NAME,
    SKIP_AWS_DB_ENV_NAME,
    VALID_AWS_ENV_NAMES,
    AbstractDatabase,
    AwsEnvName,
    DatabaseInitializationError,
    DatabaseReadError,
    DatabaseWriteError,
    confirm_aws_db_use,
)
from gene.database.schemas import StoredGene, convert_to_gene
from gene.schemas import (
    ITEM_TYPES,
    Gene,
    RecordType,
    RefType,
    SourceMeta,
    SourceName,
)

_logger = logging.getLogger(__name__)


class DynamoDbDatabase(AbstractDatabase):
    """Database class employing DynamoDB."""

    def __init__(self, db_url: Optional[str] = None, **db_args) -> None:
        """Initialize Database class.

        :param str db_url: URL endpoint for DynamoDB source
        :Keyword Arguments:
            * region_name: AWS region (defaults to "us-east-2")
            * silent: if True, suppress console output
        :raise DatabaseInitializationError: if initial setup fails
        """
        self.gene_table = environ.get("GENE_DYNAMO_TABLE", "gene_normalizer")
        region_name = db_args.get("region_name", "us-east-2")

        if AWS_ENV_VAR_NAME in environ:
            if "GENE_TEST" in environ:
                raise DatabaseInitializationError(
                    f"Cannot have both GENE_TEST and {AWS_ENV_VAR_NAME} set."
                )  # noqa: E501
            try:
                aws_env = AwsEnvName(environ[AWS_ENV_VAR_NAME])
            except ValueError:
                raise DatabaseInitializationError(
                    f"{AWS_ENV_VAR_NAME} must be one of {VALID_AWS_ENV_NAMES}: found {environ[AWS_ENV_VAR_NAME]} instead."
                )
            skip_confirmation = environ.get(SKIP_AWS_DB_ENV_NAME)
            if (not skip_confirmation) or (
                skip_confirmation and skip_confirmation != "true"
            ):  # noqa: E501
                confirm_aws_db_use(aws_env)

            boto_params = {"region_name": region_name}

            if aws_env == AwsEnvName.DEVELOPMENT:
                self.gene_table = environ.get(
                    "GENE_DYNAMO_TABLE", "gene_normalizer_nonprod"
                )
        else:
            if db_url:
                endpoint_url = db_url
            elif "GENE_NORM_DB_URL" in environ:
                endpoint_url = environ["GENE_NORM_DB_URL"]
            else:
                endpoint_url = "http://localhost:8000"
            if db_args.get("silent") != True:  # noqa: E712
                click.echo(
                    f"***Using Gene-Normalizer DynamoDB endpoint: {endpoint_url}***"
                )
            boto_params = {"region_name": region_name, "endpoint_url": endpoint_url}

        self.dynamodb = boto3.resource("dynamodb", **boto_params)
        self.dynamodb_client = boto3.client("dynamodb", **boto_params)

        # Only create tables for local instance
        envs_do_not_create_tables = {AWS_ENV_VAR_NAME, "GENE_TEST"}
        if not set(envs_do_not_create_tables) & set(environ):
            self.initialize_db()

        self.genes = self.dynamodb.Table(self.gene_table)
        self.batch = self.genes.batch_writer()
        self._cached_sources: Dict[str, SourceMeta] = {}
        atexit.register(self.close_connection)

    def list_tables(self) -> List[str]:
        """Return names of tables in database.

        :return: Table names in DynamoDB
        """
        return self.dynamodb_client.list_tables()["TableNames"]

    def drop_db(self) -> None:
        """Delete all tables from database. Requires manual confirmation.

        :raise DatabaseWriteError: if called in a protected setting with confirmation
            silenced.
        """
        try:
            if not self._check_delete_okay():
                return
        except DatabaseWriteError as e:
            raise e

        if self.gene_table in self.list_tables():
            self.dynamodb.Table(self.gene_table).delete()

    def _create_genes_table(self) -> None:
        """Create Genes table."""
        self.dynamodb.create_table(
            TableName=self.gene_table,
            KeySchema=[
                {"AttributeName": "label_and_type", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "concept_id", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "label_and_type", "AttributeType": "S"},
                {"AttributeName": "concept_id", "AttributeType": "S"},
                {"AttributeName": "src_name", "AttributeType": "S"},
                {"AttributeName": "item_type", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "src_index",
                    "KeySchema": [{"AttributeName": "src_name", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "KEYS_ONLY"},
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 10,
                        "WriteCapacityUnits": 10,
                    },
                },
                {
                    "IndexName": "item_type_index",
                    "KeySchema": [{"AttributeName": "item_type", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "KEYS_ONLY"},
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 10,
                        "WriteCapacityUnits": 10,
                    },
                },
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 10, "WriteCapacityUnits": 10},
        )

    def check_schema_initialized(self) -> bool:
        """Check if database schema is properly initialized.

        :return: True if DB appears to be fully initialized, False otherwise
        """
        existing_tables = self.list_tables()
        exists = self.gene_table in existing_tables
        if not exists:
            _logger.info(f"{self.gene_table} table is missing or unavailable.")
        return exists

    def check_tables_populated(self) -> bool:
        """Perform rudimentary checks to see if tables are populated.

        Emphasis is on rudimentary -- if some rogueish element has deleted half of the
        gene aliases, this method won't pick it up. It just wants to see if a few
        critical tables have at least a small number of records.

        :return: True if queries successful, false if DB appears empty
        """
        sources = self.genes.query(
            IndexName="item_type_index",
            KeyConditionExpression=Key("item_type").eq("source"),
        ).get("Items", [])
        if len(sources) < len(SourceName):
            _logger.info("Gene sources table is missing expected sources.")
            return False

        records = self.genes.query(
            IndexName="item_type_index",
            KeyConditionExpression=Key("item_type").eq("identity"),
            Limit=1,
        )
        if len(records.get("Items", [])) < 1:
            _logger.info("Gene records index is empty.")
            return False

        normalized_records = self.genes.query(
            IndexName="item_type_index",
            KeyConditionExpression=Key("item_type").eq(RecordType.MERGER.value),
            Limit=1,
        )
        if len(normalized_records.get("Items", [])) < 1:
            _logger.info("Normalized gene records index is empty.")
            return False

        return True

    def initialize_db(self) -> None:
        """Create gene_normalizer table if not already created."""
        if not self.check_schema_initialized():
            self._create_genes_table()

    def get_source_metadata(self, src_name: Union[str, SourceName]) -> SourceMeta:
        """Get license, versioning, data lookup, etc information for a source.

        :param src_name: name of the source to get data for
        :return: structured metadata object
        :raise DatabaseReadError: if unable to find metadata for source
        """
        if isinstance(src_name, SourceName):
            src_name = src_name.value
        if src_name in self._cached_sources:
            return self._cached_sources[src_name]
        else:
            pk = f"{src_name.lower()}##source"
            concept_id = f"source:{src_name.lower()}"
            metadata = self.genes.get_item(
                Key={"label_and_type": pk, "concept_id": concept_id}
            ).get("Item")
            structured_metadata = SourceMeta(**metadata)
            if not metadata:
                raise DatabaseReadError(
                    f"Unable to retrieve data for source {src_name}"
                )
            self._cached_sources[src_name] = structured_metadata
            return structured_metadata

    @staticmethod
    def _get_gene_from_record(record: Dict) -> Gene:
        """TODO"""

    def get_record_by_id(
        self, concept_id: str, case_sensitive: bool = True
    ) -> Optional[Gene]:
        """Fetch record corresponding to provided concept ID

        :param concept_id: concept ID for gene record
        :param case_sensitive: if true, performs exact lookup, which is more
            efficient. Otherwise, performs filter operation, which doesn't require
            correct casing.
        :return: complete gene record, if match is found; None otherwise
        """
        pk = f"{concept_id.lower()}##{RecordType.IDENTITY.value}"
        try:
            if case_sensitive:
                match = self.genes.get_item(
                    Key={"label_and_type": pk, "concept_id": concept_id}
                )
                result = match["Item"]
            else:
                exp = Key("label_and_type").eq(pk)
                response = self.genes.query(KeyConditionExpression=exp)
                result = response["Items"][0]
        except (KeyError, IndexError):  # record doesn't exist
            return None
        except ClientError as e:
            _logger.error(
                f"boto3 client error on get_records_by_id for search term {concept_id}: {e.response['Error']['Message']}"
            )
            return None

        result_parsed = StoredGene(**result)
        result_formatted = convert_to_gene(result_parsed)
        return result_formatted

    def get_ids_by_ref(self, search_term: str, ref_type: RefType) -> List[str]:
        """Retrieve concept IDs for records matching the user's query. Other methods
        are responsible for actually retrieving full records.

        :param search_term: string to match against
        :param ref_type: type of match to look for.
        :return: list of associated concept IDs. Empty if lookup fails.
        """
        pk = f"{search_term}##{ref_type.value.lower()}"
        filter_exp = Key("label_and_type").eq(pk)
        try:
            matches = self.genes.query(KeyConditionExpression=filter_exp)
            return [m["concept_id"] for m in matches.get("Items", None)]
        except ClientError as e:
            _logger.error(
                f"boto3 client error on get_refs_by_type for search term {search_term}: {e.response['Error']['Message']}"
            )
            return []

    def get_normalized_record(self, concept_id: str) -> Optional[Gene]:
        """TODO"""
        result = self.genes.get_item(
            Key={
                "label_and_type": f"{concept_id.lower()}##{RecordType.IDENTITY.value}",
                "concept_id": concept_id,
            }
        )
        if "Item" not in result:
            return None
        record = result["Item"]
        if "normalized_id" in record:
            normalized_id = record["normalized_id"]
            result = self.genes.get_item(
                Key={
                    "label_and_type": f"normalize.gene.{normalized_id.lower()}##{RecordType.MERGER.value}",
                    "concept_id": normalized_id,
                }
            )
            if "Item" not in result:
                _logger.error("Broken merge ref to % in %.", normalized_id, concept_id)
                return None
            record = result["Item"]
        return record

    def get_all_concept_ids(self) -> Set[str]:
        """Retrieve concept IDs for use in generating normalized records.

        :return: List of concept IDs as strings.
        """
        last_evaluated_key = None
        concept_ids = []
        params = {
            "ProjectionExpression": "concept_id",
        }
        while True:
            if last_evaluated_key:
                response = self.genes.scan(
                    ExclusiveStartKey=last_evaluated_key, **params
                )
            else:
                response = self.genes.scan(**params)
            records = response["Items"]
            for record in records:
                concept_ids.append(record["concept_id"])
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break
        return set(concept_ids)

    # TODO not done
    def get_all_records(self, record_type: RecordType) -> Generator[Gene, None, None]:
        """Retrieve all source or normalized records. Either return all source records,
        or all records that qualify as "normalized" (i.e., merged groups + source
        records that are otherwise ungrouped).

        For example,

        >>> from gene.database import create_db
        >>> from gene.schemas import RecordType
        >>> db = create_db()
        >>> for record in db.get_all_records(RecordType.MERGER):
        >>>     pass  # do something

        :param record_type: type of result to return
        :return: Generator that lazily provides records as they are retrieved
        """
        last_evaluated_key = None
        while True:
            if last_evaluated_key:
                response = self.genes.scan(
                    ExclusiveStartKey=last_evaluated_key,
                )
            else:
                response = self.genes.scan()
            records = response.get("Items", [])
            for record in records:
                incoming_record_type = record.get("item_type")
                if record_type == RecordType.IDENTITY:
                    if incoming_record_type == record_type:
                        yield record
                else:
                    if (
                        incoming_record_type == RecordType.IDENTITY
                        and not record.get("merge_ref")  # noqa: E501
                    ) or incoming_record_type == RecordType.MERGER:
                        yield record
            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

    def add_source_metadata(self, src_name: SourceName, metadata: SourceMeta) -> None:
        """Add new source metadata entry.

        :param src_name: name of source
        :param data: known source attributes
        :raise DatabaseWriteError: if write fails
        """
        src_name_value = src_name.value
        metadata_item = metadata.model_dump(mode="json", exclude_none=True)
        metadata_item["src_name"] = src_name_value
        metadata_item["label_and_type"] = f"{str(src_name_value).lower()}##source"
        metadata_item["concept_id"] = f"source:{str(src_name_value).lower()}"
        metadata_item["item_type"] = "source"
        try:
            self.genes.put_item(Item=metadata_item)
        except ClientError as e:
            raise DatabaseWriteError(e)

    def add_record(self, gene: StoredGene, src_name: SourceName) -> None:
        """Add new record to database.

        :param record: source gene record to upload
        :param src_name: name of source for record.
        """
        db_record = gene.model_dump(mode="json", exclude_none=True)
        concept_id = gene.concept_id
        db_record["src_name"] = src_name.value
        db_record["label_and_type"] = f"{concept_id.lower()}##identity"
        db_record["item_type"] = RecordType.IDENTITY
        try:
            self.batch.put_item(Item=db_record)
        except ClientError as e:
            _logger.error(
                f"boto3 client error on add_record for {concept_id}: {e.response['Error']['Message']}"
            )
        for attr_type in ITEM_TYPES.keys():
            if attr_type in db_record:
                value = db_record[attr_type]
                if not value:
                    continue
                ref_type = RefType[attr_type.upper()]
                if isinstance(value, str):
                    self._add_ref_record(value, concept_id, ref_type, src_name)
                else:
                    for item in {v.lower() for v in value}:
                        self._add_ref_record(item, concept_id, ref_type, src_name)

    def add_merged_record(self, merged_gene: StoredGene) -> None:
        """Add merged record to database.

        :param merged_gene: merged gene record to add
        """
        db_record = merged_gene.model_dump(mode="json", exclude_none=True)
        concept_id = db_record["concept_id"]
        db_record["label_and_type"] = f"{concept_id.lower()}##{RecordType.MERGER.value}"
        db_record["item_type"] = RecordType.MERGER.value

        try:
            self.batch.put_item(Item=db_record)
        except ClientError as e:
            _logger.error(
                f"boto3 client error on add_record for {concept_id}: {e.response['Error']['Message']}"
            )

    def _add_ref_record(
        self, term: str, concept_id: str, ref_type: RefType, src_name: SourceName
    ) -> None:
        """Add auxiliary/reference record to database.

        :param term: referent term
        :param concept_id: concept ID to refer to
        :param ref_type: type of reference
        :param src_name: name of source for record
        """
        label_and_type = f"{term.lower()}##{ref_type.value}"
        record = {
            "label_and_type": label_and_type,
            "concept_id": concept_id.lower(),
            "src_name": src_name.value,
            "item_type": ref_type.value,
        }
        try:
            self.batch.put_item(Item=record)
        except ClientError as e:
            _logger.error(
                f"boto3 client error adding reference {term} for {concept_id} with match type {ref_type}: {e.response['Error']['Message']}"
            )

    def update_merge_ref(self, concept_id: str, merge_ref: Any) -> None:  # noqa: ANN401
        """Update the merged record reference of an individual record to a new value.

        :param concept_id: record to update
        :param merge_ref: new ref value
        :raise DatabaseWriteError: if attempting to update non-existent record
        """
        label_and_type = f"{concept_id.lower()}##identity"
        key = {"label_and_type": label_and_type, "concept_id": concept_id}
        update_expression = "set merge_ref=:r"
        update_values = {":r": merge_ref.lower()}
        condition_expression = "attribute_exists(label_and_type)"
        try:
            self.genes.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=update_values,
                ConditionExpression=condition_expression,
            )
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code == "ConditionalCheckFailedException":
                raise DatabaseWriteError(
                    f"No such record exists for keys {label_and_type}, {concept_id}"
                )
            else:
                _logger.error(
                    f"boto3 client error in `database.update_record()`: {e.response['Error']['Message']}"
                )

    def delete_normalized_concepts(self) -> None:
        """Remove merged records from the database. Use when performing a new update
        of normalized data.

        :raise DatabaseReadError: if DB client requires separate read calls and
            encounters a failure in the process
        :raise DatabaseWriteError: if deletion call fails
        """
        while True:
            with self.genes.batch_writer(
                overwrite_by_pkeys=["label_and_type", "concept_id"]
            ) as batch:
                try:
                    response = self.genes.query(
                        IndexName="item_type_index",
                        KeyConditionExpression=Key("item_type").eq(
                            RecordType.MERGER.value
                        ),
                    )
                except ClientError as e:
                    raise DatabaseReadError(e)
                records = response["Items"]
                if not records:
                    break
                for record in records:
                    batch.delete_item(
                        Key={
                            "label_and_type": record["label_and_type"],
                            "concept_id": record["concept_id"],
                        }
                    )

    def delete_source(self, src_name: SourceName) -> None:
        """Delete all data for a source. Use when updating source data.

        :param src_name: name of source to delete
        :raise DatabaseReadError: if DB client requires separate read calls and
            encounters a failure in the process
        :raise DatabaseWriteError: if deletion call fails
        """
        while True:
            try:
                response = self.genes.query(
                    IndexName="src_index",
                    KeyConditionExpression=Key("src_name").eq(src_name.value),
                )
            except ClientError as e:
                raise DatabaseReadError(e)
            records = response["Items"]
            if not records:
                break
            with self.genes.batch_writer(
                overwrite_by_pkeys=["label_and_type", "concept_id"]
            ) as batch:
                for record in records:
                    try:
                        batch.delete_item(
                            Key={
                                "label_and_type": record["label_and_type"],
                                "concept_id": record["concept_id"],
                            }
                        )
                    except ClientError as e:
                        raise DatabaseWriteError(e)

    def complete_write_transaction(self) -> None:
        """Conclude transaction or batch writing if relevant."""
        self.batch.__exit__(*sys.exc_info())
        self.batch = self.genes.batch_writer()

    def close_connection(self) -> None:
        """Perform any manual connection closure procedures if necessary."""
        self.batch.__exit__(*sys.exc_info())

    def load_from_remote(self, url: Optional[str] = None) -> None:
        """Load DB from remote dump. Not available for DynamoDB database backend.

        :param url: remote location to retrieve gzipped dump file from
        """
        raise NotImplementedError

    def export_db(self, export_location: Path) -> None:
        """Dump DB to specified location. Not available for DynamoDB database backend.

        :param export_location: path to save DB dump at
        """
        raise NotImplementedError
