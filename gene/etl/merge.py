"""Create concept groups and merged records."""
import logging
from timeit import default_timer as timer
from typing import Dict, Optional, Set, Tuple

from gene.database import AbstractDatabase
from gene.database.database import DatabaseWriteException
from gene.schemas import GeneTypeFieldName, RecordType, SourcePriority

logger = logging.getLogger("gene")
logger.setLevel(logging.DEBUG)


class Merge:
    """Handles record merging."""

    def __init__(self, database: AbstractDatabase) -> None:
        """Initialize Merge instance.

        :param database: db instance to use for record retrieval and creation.
        """
        self._database = database
        self._groups = {}  # dict keying concept IDs to group Sets

    def create_merged_concepts(self, record_ids: Set[str]) -> None:
        """Create concept groups, generate merged concept records, and update database.

        :param record_ids: concept identifiers from which groups should be generated.
            Should *not* include any records from excluded sources.
        """
        logger.info("Generating record ID sets...")
        start = timer()
        for record_id in record_ids:
            new_group = self._create_record_id_set(record_id)
            if new_group:
                for concept_id in new_group:
                    self._groups[concept_id] = new_group
        end = timer()
        logger.debug(f"Built record ID sets in {end - start} seconds")

        self._groups = {k: v for k, v in self._groups.items() if len(v) > 1}

        logger.info("Creating merged records and updating database...")
        uploaded_ids = set()
        start = timer()
        for record_id, group in self._groups.items():
            if record_id in uploaded_ids:
                continue
            merged_record = self._generate_merged_record(group)

            # add group merger item to DB
            self._database.add_merged_record(merged_record)

            # add updated references
            for concept_id in group:
                merge_ref = merged_record["concept_id"]
                try:
                    self._database.update_merge_ref(concept_id, merge_ref)
                except DatabaseWriteException as dw:
                    if str(dw).startswith("No such record exists"):
                        logger.error(
                            f"Updating nonexistent record: {concept_id} "
                            f"for merge ref to {merge_ref}"
                        )
                    else:
                        logger.error(str(dw))
            uploaded_ids |= group
        self._database.complete_write_transaction()
        logger.info("Merged concept generation successful.")
        end = timer()
        logger.debug(f"Generated and added concepts in {end - start} seconds")

    def _create_record_id_set(
        self, record_id: str, observed_id_set: Optional[Set] = None
    ) -> Set[str]:
        """Recursively create concept ID group for an individual record ID.

        :param record_id: concept ID for record to build group from
        :param observed_id_set: container with all already-searched-for IDs. Provided
        to avoid repeating work.
        :return: set of related identifiers pertaining to a common concept.
        """
        if observed_id_set is None:
            observed_id_set = set()

        if record_id in self._groups:
            return self._groups[record_id]
        else:
            db_record = self._database.get_record_by_id(record_id)
            if not db_record:
                logger.warning(
                    f"Record ID set creator could not resolve "
                    f"lookup for {record_id} in ID set: "
                    f"{observed_id_set}"
                )
                return observed_id_set - {record_id}

            record_xrefs = db_record.get("xrefs")
            if not record_xrefs:
                return observed_id_set | {db_record["concept_id"]}
            else:
                local_id_set = set(record_xrefs)
            merged_id_set = {record_id} | observed_id_set
            for local_record_id in local_id_set - observed_id_set:
                merged_id_set |= self._create_record_id_set(
                    local_record_id, merged_id_set
                )
            return merged_id_set

    def _generate_merged_record(self, record_id_set: Set[str]) -> Dict:
        """Generate merged record from provided concept ID group.
        Where attributes are sets, they should be merged, and where they are
        scalars, assign from the highest-priority source where that attribute
        is non-null.

        Priority is: HGNC > NCBI > Ensembl

        :param record_id_set: group of concept IDs
        :return: completed merged drug object to be stored in DB
        """
        records = []
        for record_id in record_id_set:
            record = self._database.get_record_by_id(record_id)
            if record:
                records.append(record)
            else:
                logger.error(
                    f"Merge record generator could not retrieve "
                    f"record for {record_id} in {record_id_set}"
                )

        def record_order(record: Dict) -> Tuple[int, str]:
            """Provide priority values of concepts for sort function.

            :param record: gene record
            :return: rank and concept ID
            """
            src = record["src_name"].upper()
            if src in SourcePriority.__members__:
                source_rank = SourcePriority[src].value
            else:
                raise Exception(
                    f"Prohibited source: {src} in concept_id " f"{record['concept_id']}"
                )
            return source_rank, record["concept_id"]

        records.sort(key=record_order)

        # initialize merged record
        merged_attrs = {
            "concept_id": records[0]["concept_id"],
            "aliases": set(),
            "associated_with": set(),
            "previous_symbols": set(),
            "hgnc_locus_type": set(),
            "ncbi_gene_type": set(),
            "ensembl_biotype": set(),
            "strand": set(),
        }
        if len(records) > 1:
            merged_attrs["xrefs"] = list({r["concept_id"] for r in records[1:]})

        # merge from constituent records
        set_fields = ["aliases", "associated_with", "previous_symbols", "strand"]
        scalar_fields = ["symbol", "symbol_status", "label", "location_annotations"]
        for record in records:
            for field in set_fields:
                merged_attrs[field] |= set(record.get(field, set()))

            for field in scalar_fields:
                if field not in merged_attrs and field in record:
                    merged_attrs[field] = record[field]

            locations = record.get("locations")
            if locations:
                merged_attrs[f"{record['src_name'].lower()}_locations"] = locations

            gene_type = record.get("gene_type")
            if gene_type:
                merged_field = GeneTypeFieldName[record["src_name"].upper()]
                merged_attrs[merged_field] |= {gene_type}

        for field in set_fields + [
            "hgnc_locus_type",
            "ncbi_gene_type",
            "ensembl_biotype",
        ]:
            field_value = merged_attrs[field]
            if field_value:
                merged_attrs[field] = list(field_value)
            else:
                del merged_attrs[field]

        # ensure no conflicting strands
        unique_strand_values = set(merged_attrs.get("strand", []))
        num_unique_strand_values = len(unique_strand_values)
        if num_unique_strand_values > 1:
            del merged_attrs["strand"]
        elif num_unique_strand_values == 1:
            merged_attrs["strand"] = list(unique_strand_values)[0]

        merged_attrs["item_type"] = RecordType.MERGER.value
        return merged_attrs
