"""Provide PostgreSQL client.

TODO
 * use connection pool? https://www.psycopg.org/psycopg3/docs/advanced/pool.html
 * async?
 * AWS environment stuff? Not sure if necessary at this juncture
 * properly close connection? seems to be closing correctly here but idk
 * materialized view for _get_record calls
 * this should work: get record ID for ensembl:ensg00000290825
"""

import atexit
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import tempfile

import psycopg
from psycopg.errors import UniqueViolation
import requests

from gene.database import AbstractDatabase, DatabaseException, \
    DatabaseReadException, DatabaseWriteException
from gene.schemas import SourceMeta, SourceName


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class PostgresDatabase(AbstractDatabase):
    """Database class employing PostgreSQL."""

    def __init__(self, db_url: Optional[str] = None, **db_args) -> None:
        """Initialize Postgres connection.

        :param db_url: libpq compliant database connection URI
        :param **db_args: see below

        :Keyword Arguments:
            * user: Postgres username
            * password: Postgres password (optional or blank if unneeded)
            * db_name: name of database to connect to

        :raise DatabaseInitializationException: if initial setup fails
        """
        if db_url:
            conninfo = db_url
        elif "GENE_NORM_DB_URL" in os.environ:
            conninfo = os.environ["GENE_NORM_DB_URL"]
        else:
            user = db_args.get("user", "postgres")
            password = db_args.get("password", "")
            db_name = db_args.get("db_name", "gene_normalizer")
            if password:
                conninfo = f"dbname={db_name} user={user} password={password}"
            else:
                conninfo = f"dbname={db_name} user={user}"

        self.conn = psycopg.connect(conninfo)
        self.initialize_db()
        self._cached_sources = {}

        atexit.register(self.complete_transaction)

    def drop_db(self) -> None:
        """Perform complete teardown of DB. Useful for quickly resetting all data or
        reconstructing after apparent schema error.
        """
        drop_query = """
        DROP TABLE IF EXISTS
            gene_associations,
            gene_symbols,
            gene_previous_symbols,
            gene_aliases,
            gene_xrefs,
            gene_concepts,
            gene_merged,
            gene_sources;
        """
        with self.conn.cursor() as cur:
            cur.execute(drop_query)
            self.conn.commit()
        logger.info("Dropped all existing gene normalizer tables.")

    def initialize_db(self) -> None:
        """Check if DB is set up. If not, create tables/indexes/views."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_type = 'BASE TABLE' AND table_schema = 'public'"
            )
            tables = {t[0] for t in cur.fetchall()}

        expected_tables = ["gene_associations", "gene_sources", "gene_concepts",
                           "gene_symbols", "gene_previous_symbols", "gene_aliases",
                           "gene_merged"]
        for table in expected_tables:
            if table not in tables:
                logger.info(f"{table} was missing -- resetting gene normalizer tables")
                self.drop_db()
                self._create_tables()
                break
        # TODO check indexes as well?

    def _create_indexes(self) -> None:
        """Create all indexes."""
        query = """
        CREATE INDEX IF NOT EXISTS idx_gm_concept_id ON gene_merged (concept_id);
        CREATE INDEX IF NOT EXISTS idx_gm_concept_id_low
            ON gene_merged ((lower(concept_id)));

        CREATE INDEX IF NOT EXISTS idx_gc_source ON gene_concepts (source);
        CREATE INDEX IF NOT EXISTS idx_gc_source_low
            ON gene_concepts ((lower(concept_id)));
        CREATE INDEX IF NOT EXISTS idx_gc_merged ON gene_concepts (merge_ref);

        CREATE INDEX IF NOT EXISTS idx_gs_concept ON gene_symbols (concept_id);

        CREATE INDEX IF NOT EXISTS idx_gps_concept
            ON gene_previous_symbols (concept_id);

        CREATE INDEX IF NOT EXISTS idx_ga_concept ON gene_aliases (concept_id);

        CREATE INDEX IF NOT EXISTS idx_gx_concept ON gene_xrefs (concept_id);

        CREATE INDEX IF NOT EXISTS idx_g_as_concept ON gene_associations (concept_id);
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit()

    def _create_tables(self) -> None:
        """Create all tables, indexes, and views.

        TODO
         * materialized view for record lookups/joins?
         * if writes are too slow, could drop indexes before refreshing a source
           and then re-add them after
        """
        logger.debug("Creating new gene normalizer tables.")
        sources_table = """
        CREATE TABLE IF NOT EXISTS gene_sources (
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
        CREATE TABLE IF NOT EXISTS gene_merged (
            concept_id VARCHAR(127) PRIMARY KEY,
            symbol TEXT,
            symbol_status VARCHAR(127),
            previous_symbols TEXT [],
            label TEXT,
            strand VARCHAR(1),
            ensembl_locations JSON [],
            hgnc_locations JSON [],
            ncbi_locations JSON [],
            location_annotations TEXT [],
            ensembl_biotype TEXT,
            hgnc_locus_type TEXT,
            ncbi_gene_type TEXT,
            aliases TEXT [],
            associated_with TEXT [],
            xrefs TEXT []
        )
        """

        concepts_table = """
        CREATE TABLE IF NOT EXISTS gene_concepts (
            concept_id VARCHAR(127) PRIMARY KEY,
            source VARCHAR(127) NOT NULL REFERENCES gene_sources (name)
                ON DELETE CASCADE,
            symbol_status VARCHAR(127),
            label TEXT,
            strand VARCHAR(1),
            location_annotations TEXT [],
            locations JSON [],
            gene_type TEXT,
            merge_ref VARCHAR(127) REFERENCES gene_merged (concept_id)
                ON DELETE CASCADE
        );
        """

        symbols_table = """
        CREATE TABLE IF NOT EXISTS gene_symbols (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            concept_id VARCHAR(127) REFERENCES gene_concepts (concept_id)
                ON DELETE CASCADE
        );
        """

        previous_symbols_table = """
        CREATE TABLE IF NOT EXISTS gene_previous_symbols (
            id SERIAL PRIMARY KEY,
            prev_symbol TEXT NOT NULL,
            concept_id VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
                ON DELETE CASCADE
        );
        """

        aliases_table = """
        CREATE TABLE IF NOT EXISTS gene_aliases (
            id SERIAL PRIMARY KEY,
            alias TEXT NOT NULL,
            concept_id VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
                ON DELETE CASCADE
        );
        """

        xrefs_table = """
        CREATE TABLE IF NOT EXISTS gene_xrefs (
            id SERIAL PRIMARY KEY,
            xref TEXT NOT NULL,
            concept_id VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
                ON DELETE CASCADE
        );
        """

        assoc_table = """
        CREATE TABLE IF NOT EXISTS gene_associations (
            id SERIAL PRIMARY KEY,
            associated_with TEXT NOT NULL,
            concept_ID VARCHAR(127) NOT NULL REFERENCES gene_concepts (concept_id)
                ON DELETE CASCADE
        );
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
        self._create_indexes()

    def get_source_metadata(self, src_name: SourceName) -> Dict:
        """Get license, versioning, data lookup, etc information for a source.

        :param SourceName: name of the source to get data for
        """
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

    def _get_record(self, concept_id: str, case_sensitive: bool) -> Optional[Dict]:
        """Retrieve non-merged record. The query is pretty different, so this method
        is broken out for PostgreSQL.

        :param concept_id: ID of concept to get
        :param case_sensitive:
        :return: complete record object if successful
        """
        query = """
        SELECT
            gc.concept_id,
            gc.symbol_status,
            gc.label,
            gc.strand,
            gc.location_annotations,
            gc.locations,
            gc.gene_type,
            ga.aliases,
            gas.associated_with,
            gps.previous_symbols,
            gs.symbol,
            gx.xrefs,
            gc.source
        FROM gene_concepts gc
        FULL OUTER JOIN (
            SELECT ga.concept_id, ARRAY_AGG(ga.alias) AS aliases
            FROM gene_aliases ga
            GROUP BY ga.concept_id
        ) ga ON gc.concept_id = ga.concept_id
        FULL OUTER JOIN (
            SELECT gas.concept_id, ARRAY_AGG(gas.associated_with) AS associated_with
            FROM gene_associations gas
            GROUP BY gas.concept_id
        ) gas ON gc.concept_id = gas.concept_id
        FULL OUTER JOIN (
            SELECT gps.concept_id, ARRAY_AGG(gps.prev_symbol)
                AS previous_symbols
            FROM gene_previous_symbols gps
            GROUP BY gps.concept_id
        ) gps ON gc.concept_id = gps.concept_id
        FULL OUTER JOIN gene_symbols gs ON gc.concept_id = gs.concept_id
        FULL OUTER JOIN (
            SELECT gx.concept_id, ARRAY_AGG(gx.xref) AS xrefs
            FROM gene_xrefs gx
            GROUP BY gx.concept_id
        ) gx ON gc.concept_id = gx.concept_id
        """
        if case_sensitive:
            query += "WHERE gc.concept_id = %s;"
            concept_id_param = concept_id
        else:
            query += "WHERE lower(gc.concept_id) = %s;"
            concept_id_param = concept_id.lower()

        with self.conn.cursor() as cur:
            cur.execute(query, [concept_id_param])
            result = cur.fetchone()
        if not result:
            return None

        gene_record = {
            "concept_id": result[0],
            "symbol_status": result[1],
            "label": result[2],
            "strand": result[3],
            "location_annotations": result[4],
            "locations": result[5],
            "gene_type": result[6],
            "aliases": result[7],
            "associated_with": result[8],
            "previous_symbols": result[9],
            "symbol": result[10],
            "xrefs": result[11],
            "src_name": result[12],
        }
        return {k: v for k, v in gene_record.items() if v}

    def _get_merged_record(
        self, concept_id: str, case_sensitive: bool
    ) -> Optional[Dict]:
        """Retrieve normalized record from DB.

        :param concept_id: normalized ID for the merged record
        :param case_sensitive: True if `concept_id` is correctly cased (enables
            faster lookup)
        :return: normalized record if successful
        """
        if case_sensitive:
            query = "SELECT * FROM gene_merged WHERE concept_id = %s;"
        else:
            concept_id = concept_id.lower()
            query = "SELECT * FROM gene_merged WHERE lower(concept_id) = %s;"
        with self.conn.cursor() as cur:
            cur.execute(query, [concept_id])
            result = cur.fetchone()
        if not result:
            return None

        merged_record = {
            "concept_id": result[0],
            "symbol": result[1],
            "symbol_status": result[2],
            "previous_symbols": result[3],
            "label": result[4],
            "strand": result[5],
            "location_annotations": result[6],
            "ensembl_locations": json.loads(result[8]),
            "hgnc_locations": json.loads(result[9]),
            "ncbi_locations": json.loads(result[10]),
            "ensembl_biotype": result[11],
            "hgnc_locus_type": result[12],
            "ncbi_gene_type": result[13],
            "aliases": result[14],
            "associated_with": result[15],
            "xrefs": result[16],
        }
        return merged_record

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
            return self._get_merged_record(concept_id, case_sensitive)
        else:
            return self._get_record(concept_id, case_sensitive)

    def get_refs_by_type(self, query: str, match_type: str) -> List[str]:
        """Retrieve concept IDs for records matching the user's query. Other methods
        are responsible for actually retrieving full records.

        :param query: string to match against
        :param match_type: type of match to look for. Should be one of {"symbol",
            "prev_symbol", "alias", "xref", "associated_with"} (use `get_record_by_id`
            for concept ID lookup)
        :return: list of associated concept IDs. Empty if lookup fails.
        """
        if match_type == "symbol":
            table = "gene_symbols"
        elif match_type == "prev_symbol":
            table = "gene_previous_symbols"
        elif match_type == "alias":
            table = "gene_aliases"
        elif match_type == "xref":
            table = "gene_xrefs"
        elif match_type == "associated_with":
            table = "gene_associations"
        else:
            raise ValueError

        lookup_query = "SELECT concept_id FROM %s WHERE lower(%s) = %s;"
        with self.conn.cursor() as cur:
            cur.execute(lookup_query, (table, match_type, query.lower()))
            concept_ids = cur.fetchall()
        if concept_ids:
            return [i[0] for i in concept_ids]
        else:
            return []

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
        """Add new source metadata entry.

        :param src_name: name of source
        :param data: known source attributes
        :raise DatabaseWriteException: if write fails
        """
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
                    src_name.value,
                    meta.data_license, meta.data_license_url, meta.version,
                    meta.data_url, meta.rdp_url,
                    meta.data_license_attributes["non_commercial"],
                    meta.data_license_attributes["attribution"],
                    meta.data_license_attributes["share_alike"],
                    meta.genome_assemblies
                ]
            )
        self.conn.commit()

    def _add_identity_record(self, record: Dict) -> None:
        """Add source record into database.

        :param record: prepared data to add
        """
        record_query = """
            INSERT INTO gene_concepts (
                concept_id, source, symbol_status, label,
                strand, location_annotations, locations, gene_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """

        insert_symbol = "INSERT INTO gene_symbols (symbol, concept_id) VALUES (%s, %s)"
        insert_prev_symbol = "INSERT INTO gene_previous_symbols (prev_symbol, concept_id) VALUES (%s, %s)"  # noqa: E501
        insert_alias = "INSERT INTO gene_aliases (alias, concept_id) VALUES (%s, %s)"
        insert_xref = "INSERT INTO gene_xrefs (xref, concept_id) VALUES (%s, %s)"
        insert_assoc = "INSERT INTO gene_associations (associated_with, concept_id) VALUES (%s, %s)"  # noqa: E501

        concept_id = record["concept_id"]
        locations = [json.dumps(loc) for loc in record.get("locations", [])]
        if not locations:
            locations = None
        with self.conn.cursor() as cur:
            try:
                cur.execute(record_query, [
                    concept_id, record["src_name"], record.get("symbol_status"),
                    record.get("label"), record.get("strand"),
                    record.get("location_annotations"),
                    locations,
                    record.get("gene_type")
                ])
                for a in record.get("aliases", []):
                    cur.execute(insert_alias, [a, concept_id])
                for x in record.get("xrefs", []):
                    cur.execute(insert_xref, [x, concept_id])
                for a in record.get("associated_with", []):
                    cur.execute(insert_assoc, [a, concept_id])
                for p in record.get("previous_symbols", []):
                    cur.execute(insert_prev_symbol, [p, concept_id])
                if record.get("symbol"):
                    cur.execute(insert_symbol, [record["symbol"], concept_id])
                self.conn.commit()
            except UniqueViolation:
                logger.error(
                    f"Record with ID {concept_id} already exists"
                )
                self.conn.rollback()

    def _add_merged_record(self, record: Dict) -> None:
        """Add merged record to database.

        :param record: merged data to add
        """
        record_query = """
        INSERT INTO gene_merged (
            concept_id, symbol, symbol_status, previous_symbols, label, strand,
            location_annotations, ensembl_locations, hgnc_locations, ncbi_locations,
            hgnc_locus_type, ensembl_biotype, ncbi_gene_type, aliases, associated_with,
            xrefs
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        ensembl_locations = record.get("ensembl_locations")
        if ensembl_locations:
            ensembl_locations = [json.dumps(i) for i in ensembl_locations]
        ncbi_locations = record.get("ncbi_locations")
        if ncbi_locations:
            ncbi_locations = [json.dumps(i) for i in ncbi_locations]
        hgnc_locations = record.get("hgnc_locations")
        if hgnc_locations:
            hgnc_locations = [json.dumps(i) for i in hgnc_locations]
        with self.conn.cursor() as cur:
            cur.execute(record_query, [
                record["concept_id"],
                record.get("symbol"),
                record.get("symbol_status"),
                record.get("previous_symbols"),
                record.get("label"),
                record.get("strand"),
                record.get("location_annotations"),
                ensembl_locations,
                hgnc_locations,
                ncbi_locations,
                record.get("hgnc_locus_type"),
                record.get("ensembl_biotype"),
                record.get("ncbi_gene_type"),
                record.get("aliases"),
                record.get("associated_with"),
                record.get("xrefs"),
            ])
            self.conn.commit()

    def add_record(self, record: Dict, record_type: str = "identity") -> None:
        """Add new record to database.

        :param Dict record: record to upload
        :param str record_type: type of record (either 'identity' or 'merger')
        """
        if record_type == "identity":
            self._add_identity_record(record)
        elif record_type == "merger":
            self._add_merged_record(record)
        else:
            raise ValueError

    def add_ref_record(self, term: str, concept_id: str, ref_type: str,
                       src_name: SourceName) -> None:
        """Add auxiliary/reference record, like an xref or alias, to the database.
        PostgreSQL requires that we write the main concept record first, so
        we actually perform the reference writing in that method, and this is
        just a stub. A minor refactor of the base ETL method could clean that up for
        gene, but might not work in other normalizers.

        :param term: referent term
        :param concept_id: concept ID to refer to
        :param ref_type: one of {'alias', 'label', 'xref', 'associated_with'}
        :param src_name: name of source that concept ID belongs to
        """
        pass

    def update_record(self, concept_id: str, field: str, new_value: Any,
                      item_type: str = "identity") -> None:
        """Update the field of an individual record to a new value.

        It's technically a major anti-pattern to use string formatting to build queries
        (the psycopg docs have an extended rant about it) but here we're using preset
        options only and raising a ValueError for anything tricky, so it shouldn't be a
        huge deal.

        :param concept_id: record to update
        :param field: name of field to update
        :param new_value: new value
        :param item_type: record type, one of {'identity', 'merger'}
        :raise DatabaseWriteException: if attempting to update non-existent record
        """
        if item_type != "identity":
            raise NotImplementedError
        elif field in {"symbol_status", "label", "strand", "location_annotations",
                       "locations", "gene_type", "merge_ref"}:
            update_query = f"""
                UPDATE gene_concepts
                SET {field} = %(new_value)s
                WHERE concept_id = %(concept_id)s;
            """
        elif field in {"xrefs", "aliases", "associated_with", "previous_symbols"}:
            raise NotImplementedError
        elif field == "symbol":
            raise NotImplementedError
        else:
            raise ValueError

        with self.conn.cursor() as cur:
            cur.execute(update_query, {  # type: ignore
                "field": field,
                "new_value": new_value,
                "concept_id": concept_id
            })
            row_count = cur.rowcount
            self.conn.commit()

        # UPDATE will fail silently unless we check the # of affected rows
        if row_count < 1:
            raise DatabaseWriteException(
                f"No such record exists for primary key {concept_id}"
            )

    def delete_normalized_concepts(self) -> None:
        """Remove merged records from the database. Use when performing a new update
        of normalized data.

        It would be faster to drop the entire table and do a cascading delete onto the
        merge_ref column in gene_concepts, but that requires an exclusive access lock
        on the DB, which can be annoying (ie you couldn't have multiple processes
        accessing it, or PgAdmin, etc...)

        :raise DatabaseReadException: if DB client requires separate read calls and
            encounters a failure in the process
        :raise DatabaseWriteException: if deletion call fails
        """
        query = """
            UPDATE gene_concepts SET merge_ref = NULL;
            DELETE FROM gene_merged;
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit()
        self._create_tables()

    def delete_source(self, src_name: SourceName) -> None:
        """Delete all data for a source. Use when updating source data.

        :param src_name: name of source to delete
        :raise DatabaseWriteException: if deletion call fails
        """
        drop_source_query = "DELETE FROM gene_sources gs WHERE gs.name = %s;"

        with self.conn.cursor() as cur:
            cur.execute(drop_source_query, [src_name.value])
            self.conn.commit()

    def complete_transaction(self) -> None:
        """Conclude transaction or batch writing if relevant."""
        if not self.conn.closed:
            self.conn.commit()

    def load_from_remote(self, url: Optional[str]) -> None:
        """Load DB from remote dump. Warning: Deletes all existing data. If not
        passed as an argument, will try to grab from GENE_NORM_POSTGRES_DUMP_URL
        environment variable.

        TODO:
        * prompt to okay data delete?
        * test it
        * assume the file is gzipped?

        :param url: location of pg_dump file
        """
        if not url:
            url = os.environ.get(
                "GENE_NORM_POSTGRES_DUMP_URL",
                "https://vicc-normalizers.s3.us-east-2.amazonaws.com/gene_normalization/postgresql/gene_norm_latest.sql"  # noqa: E501
            )
        if not url:
            raise DatabaseException("Must provide URL to pg_dump file")
        self.drop_db()
        file = Path(tempfile.NamedTemporaryFile().name)
        with requests.get(url, stream=True) as r:
            try:
                r.raise_for_status()
            except requests.HTTPError:
                raise DatabaseException(
                    f"Unable to retrieve PostgreSQL dump file from {url}"
                )
            with open(file, "wb") as h:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        h.write(chunk)
        if self.conn.info.password:
            pw_param = f"-W {self.conn.info.password}"
        else:
            pw_param = "-w"
        os.system(
            f"psql -d {self.conn.info.dbname} -U {self.conn.info.user} {pw_param} -f {file.absolute()}"  # noqa: E501
        )
