"""Provides methods for handling queries."""
import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar
from urllib.parse import quote

from ga4gh.core import ga4gh_identify
from ga4gh.vrs import models
from ga4gh.vrsatile.pydantic.vrs_models import VRSTypes
from ga4gh.vrsatile.pydantic.vrsatile_models import Extension, GeneDescriptor

from gene import ITEM_TYPES, NAMESPACE_LOOKUP, PREFIX_LOOKUP, logger
from gene.database import AbstractDatabase, DatabaseReadException
from gene.schemas import (
    BaseGene,
    BaseNormalizationService,
    Gene,
    GeneTypeFieldName,
    MatchesNormalized,
    MatchType,
    NamespacePrefix,
    NormalizeService,
    RecordType,
    RefType,
    SearchService,
    ServiceMeta,
    SourceName,
    SourcePriority,
    UnmergedNormalizationService,
)
from gene.version import __version__

NormService = TypeVar("NormService", bound=BaseNormalizationService)


class InvalidParameterException(Exception):  # noqa: N818
    """Exception for invalid parameter args provided by the user."""


class QueryHandler:
    """Class for normalizer management. Stores reference to database instance
    and normalizes query input.
    """

    def __init__(self, database: AbstractDatabase) -> None:
        """Initialize QueryHandler instance. Requires a created database object to
        initialize. The most straightforward way to do this is via the ``create_db``
        method in the ``gene.database`` module:

        >>> from gene.query import QueryHandler
        >>> from gene.database import create_db
        >>> q = QueryHandler(create_db())

        We'll generally call ``create_db`` without any arguments in code examples, for
        the sake of brevity. See the `usage` page in the docs and the ``create_db`` API
        description for more details.

        :param database: storage backend to search against
        """
        self.db = database

    @staticmethod
    def _emit_warnings(query_str: str) -> List:
        """Emit warnings if query contains non breaking space characters.

        :param query_str: query string
        :return: List of warnings
        """
        warnings = []
        nbsp = re.search("\xa0|&nbsp;", query_str)
        if nbsp:
            warnings = [
                {
                    "non_breaking_space_characters": "Query contains non-breaking space characters"
                }
            ]
            logger.warning(
                f"Query ({query_str}) contains non-breaking space characters."
            )
        return warnings

    @staticmethod
    def _transform_sequence_location(loc: Dict) -> models.SequenceLocation:
        """Transform a sequence location to VRS sequence location

        :param loc: Sequence location
        :return: VRS sequence location
        """
        return models.SequenceLocation(
            type="SequenceLocation",
            sequence_id=loc["sequence_id"],
            interval=models.SequenceInterval(
                type="SequenceInterval",
                start=models.Number(value=int(loc["start"]), type="Number"),
                end=models.Number(value=int(loc["end"]), type="Number"),
            ),
        )

    @staticmethod
    def _transform_chromosome_location(loc: Dict) -> models.ChromosomeLocation:
        """Transform a chromosome location to VRS chromosome location

        :param loc: Chromosome location
        :return: VRS chromosome location
        """
        transformed_loc = models.ChromosomeLocation(
            type="ChromosomeLocation",
            species_id=loc["species_id"],
            chr=loc["chr"],
            interval=models.CytobandInterval(
                type="CytobandInterval", start=loc["start"], end=loc["end"]
            ),
        )
        return transformed_loc

    def _transform_location(self, loc: Dict) -> Dict:
        """Transform a sequence/chromosome location to VRS sequence/chromosome location

        :param loc: Sequence or Chromosome location
        :return: VRS sequence or chromosome location represented as a dictionary
        """
        if loc["type"] == VRSTypes.SEQUENCE_LOCATION:
            transformed_loc = self._transform_sequence_location(loc)
        else:
            transformed_loc = self._transform_chromosome_location(loc)
        transformed_loc._id = ga4gh_identify(transformed_loc)
        return transformed_loc.as_dict()

    def _transform_locations(self, record: Dict) -> Dict:
        """Transform gene locations to VRS Chromosome/Sequence Locations

        :param record: original record
        :return: record with transformed locations attributes, if applicable
        """
        record_locations = list()
        if "locations" in record:
            for loc in record["locations"]:
                record_locations.append(self._transform_location(loc))
        record["locations"] = record_locations
        return record

    def _get_src_name(self, concept_id: str) -> SourceName:
        """Get source name enum from ID.

        :param concept_id: candidate concept ID string to check
        :return: SourceName option
        :raise: ValueError if unrecognized ID provided
        """
        if concept_id.startswith(NamespacePrefix.ENSEMBL.value):
            return SourceName.ENSEMBL
        elif concept_id.startswith(NamespacePrefix.NCBI.value):
            return SourceName.NCBI
        elif concept_id.startswith(NamespacePrefix.HGNC.value):
            return SourceName.HGNC
        else:
            raise ValueError("Invalid or unrecognized concept ID provided")

    def _add_record(
        self, response: Dict[str, Dict], item: Dict, match_type: MatchType
    ) -> None:
        """Add individual record (i.e. Item in DynamoDB) to response object

        :param response: in-progress response object to return to client
        :param item: Item retrieved from DynamoDB
        :param match_type: match type for query
        """
        item = self._transform_locations(item)
        item["match_type"] = match_type
        gene = Gene(**item)
        src_name = item["src_name"]

        matches = response["source_matches"]
        if src_name not in matches.keys():
            pass
        elif matches[src_name] is None:
            matches[src_name] = {
                "records": [gene],
                "source_meta_": self.db.get_source_metadata(src_name),
            }
        else:
            matches[src_name]["records"].append(gene)

    def _fetch_record(
        self, response: Dict[str, Dict], concept_id: str, match_type: MatchType
    ) -> None:
        """Add fetched record to response

        :param response: in-progress response object to return to client.
        :param concept_id: Concept id to fetch record for. Should be all lower-case.
        :param match_type: match type for record
        """
        try:
            match = self.db.get_record_by_id(concept_id, case_sensitive=False)
        except DatabaseReadException as e:
            logger.error(
                f"Encountered DatabaseReadException looking up {concept_id}: {e}"
            )
        else:
            if match:
                self._add_record(response, match, match_type)
            else:
                logger.error(
                    f"Unable to find expected record for {concept_id} matching as {match_type}"
                )  # noqa: E501

    def _post_process_resp(self, resp: Dict) -> Dict:
        """Fill all empty source_matches slots with NO_MATCH results and
        sort source records by descending `match_type`.

        :param resp: incoming response object
        :return: response object with empty source slots filled with NO_MATCH results
            and corresponding source metadata
        """
        for src_name in resp["source_matches"].keys():
            if resp["source_matches"][src_name] is None:
                resp["source_matches"][src_name] = {
                    "match_type": MatchType.NO_MATCH,
                    "records": [],
                    "source_meta_": self.db.get_source_metadata(src_name),
                }
            else:
                records = resp["source_matches"][src_name]["records"]
                if len(records) > 1:
                    records = sorted(records, key=lambda k: k.match_type, reverse=True)
        return resp

    def _response_keyed(self, query: str, sources: Set[str]) -> Dict:
        """Return response as dict where key is source name and value
        is a list of records. Corresponds to `keyed=true` API parameter.

        :param query: string to match against
        :param sources: sources to match from
        :return: completed response object to return to client
        """
        resp = {
            "query": query,
            "warnings": self._emit_warnings(query),
            "source_matches": {source: None for source in sources},
        }
        if query == "":
            return self._post_process_resp(resp)
        query_l = query.lower()

        queries = list()
        if [p for p in PREFIX_LOOKUP.keys() if query_l.startswith(p)]:
            queries.append((query_l, RecordType.IDENTITY.value))

        for prefix in [p for p in NAMESPACE_LOOKUP.keys() if query_l.startswith(p)]:
            term = f"{NAMESPACE_LOOKUP[prefix].lower()}:{query_l}"
            queries.append((term, RecordType.IDENTITY.value))

        for match in ITEM_TYPES.values():
            queries.append((query_l, match))

        matched_concept_ids = list()
        for term, item_type in queries:
            try:
                if item_type == RecordType.IDENTITY.value:
                    record = self.db.get_record_by_id(term, False)
                    if record and record["concept_id"] not in matched_concept_ids:
                        self._add_record(resp, record, MatchType.CONCEPT_ID)
                else:
                    refs = self.db.get_refs_by_type(term, RefType(item_type))
                    for ref in refs:
                        if ref not in matched_concept_ids:
                            self._fetch_record(resp, ref, MatchType[item_type.upper()])
                            matched_concept_ids.append(ref)

            except DatabaseReadException as e:
                logger.error(
                    f"Encountered DatabaseReadException looking up {item_type}"
                    f" {term}: {e}"
                )
                continue

        # remaining sources get no match
        return self._post_process_resp(resp)

    def _response_list(self, query: str, sources: Set[str]) -> Dict:
        """Return response as list, where the first key-value in each item
        is the source name. Corresponds to `keyed=false` API parameter.

        :param query: string to match against
        :param sources: sources to match from
        :return: completed response object to return to client
        """
        response_dict = self._response_keyed(query, sources)
        source_list = []
        for src_name in response_dict["source_matches"].keys():
            src = {
                "source": src_name,
            }
            to_merge = response_dict["source_matches"][src_name]
            src.update(to_merge)

            source_list.append(src)
        response_dict["source_matches"] = source_list

        return response_dict

    @staticmethod
    def _get_service_meta() -> ServiceMeta:
        """Return metadata about gene-normalizer service.

        :return: Service Meta
        """
        return ServiceMeta(version=__version__, response_datetime=str(datetime.now()))

    def search(
        self,
        query_str: str,
        keyed: bool = False,
        incl: str = "",
        excl: str = "",
        **params,
    ) -> SearchService:
        """Return highest match for each source.

        >>> from gene.query import QueryHandler
        >>> from gene.database import create_db
        >>> q = QueryHandler(create_db())
        >>> result = q.search("BRAF")
        >>> result.source_matches[0].records[0].concept_id
        'ncbigene:673'

        :param query_str: query, a string, to search for
        :param keyed: if true, return response as dict keying source names to source
            objects; otherwise, return list of source objects
        :param incl: str containing comma-separated names of sources to use. Will
            exclude all other sources. Case-insensitive.
        :param excl: str containing comma-separated names of source to exclude. Will
            include all other source. Case-insensitive.
        :return: SearchService class containing all matches found in sources.
        :raise InvalidParameterException: if both `incl` and `excl` args are provided,
            or if invalid source names are given
        """
        possible_sources = {
            name.value.lower(): name.value for name in SourceName.__members__.values()
        }
        sources = dict()
        for k, v in possible_sources.items():
            if self.db.get_source_metadata(v):
                sources[k] = v

        if not incl and not excl:
            query_sources = set(sources.values())
        elif incl and excl:
            detail = "Cannot request both source inclusions and exclusions."
            raise InvalidParameterException(detail)
        elif incl:
            req_sources = [n.strip() for n in incl.split(",")]
            invalid_sources = []
            query_sources = set()
            for source in req_sources:
                if source.lower() in sources.keys():
                    query_sources.add(sources[source.lower()])
                else:
                    invalid_sources.append(source)
            if invalid_sources:
                detail = f"Invalid source name(s): {invalid_sources}"
                raise InvalidParameterException(detail)
        else:
            req_exclusions = [n.strip() for n in excl.lower().split(",")]
            req_excl_dict = {r.lower(): r for r in req_exclusions}
            invalid_sources = []
            query_sources = set()
            for req_l, req in req_excl_dict.items():
                if req_l not in sources.keys():
                    invalid_sources.append(req)
            for src_l, src in sources.items():
                if src_l not in req_excl_dict.keys():
                    query_sources.add(src)
            if invalid_sources:
                detail = f"Invalid source name(s): {invalid_sources}"
                raise InvalidParameterException(detail)

        query_str = query_str.strip()

        if keyed:
            resp = self._response_keyed(query_str, query_sources)
        else:
            resp = self._response_list(query_str, query_sources)

        resp["service_meta_"] = self._get_service_meta()
        return SearchService(**resp)

    def _add_merged_meta(self, response: NormalizeService) -> NormalizeService:
        """Add source metadata to response object.

        :param response: in-progress response object
        :return: completed response object.
        """
        sources_meta = {}
        gene_descr = response.gene_descriptor
        xrefs = gene_descr.xrefs or []  # type: ignore
        ids = [gene_descr.gene_id] + xrefs  # type: ignore
        for concept_id in ids:
            prefix = concept_id.split(":")[0]
            src_name = PREFIX_LOOKUP[prefix.lower()]
            if src_name not in sources_meta:
                sources_meta[src_name] = self.db.get_source_metadata(src_name)
        response.source_meta_ = sources_meta
        return response

    def _add_alt_matches(
        self, response: NormService, record: Dict, possible_concepts: List[str]
    ) -> NormService:
        """Add alternate matches warning to response object

        :param response: in-progress response object
        :param record: normalized record
        :param possible_concepts: other possible matches
        :return: updated response object
        """
        norm_concepts = set()
        for concept_id in possible_concepts:
            r = self.db.get_record_by_id(concept_id, True)
            if r:
                merge_ref = r.get("merge_ref")
                if merge_ref:
                    norm_concepts.add(merge_ref)
        norm_concepts = norm_concepts - {record["concept_id"]}
        if norm_concepts:
            response.warnings.append(
                {"multiple_normalized_concepts_found": list(norm_concepts)}
            )
        return response

    def _add_gene_descriptor(
        self,
        response: NormalizeService,
        record: Dict,
        match_type: MatchType,
        possible_concepts: Optional[List[str]] = None,
    ) -> NormalizeService:
        """Add gene descriptor to response.

        :param response: Response object
        :param record: Gene record
        :param match_type: query's match type
        :param possible_concepts: List of other normalized concepts found
        :return: Response with gene descriptor
        """
        params = {
            "id": f"normalize.gene:{quote(response.query)}",
            "label": record["symbol"],
            "gene_id": record["concept_id"],
        }

        # xrefs
        if "xrefs" in record and record["xrefs"]:
            params["xrefs"] = record["xrefs"]

        # alternate labels
        alt_labels = set()
        for key in ["previous_symbols", "aliases"]:
            if key in record and record[key]:
                val = record[key]
                if isinstance(val, str):
                    val = [val]
                alt_labels.update(val)
        if alt_labels:
            params["alternate_labels"] = list(alt_labels)

        # extensions
        extensions = list()
        extension_and_record_labels = [
            ("symbol_status", "symbol_status"),
            ("approved_name", "label"),
            ("associated_with", "associated_with"),
            ("previous_symbols", "previous_symbols"),
            ("location_annotations", "location_annotations"),
            ("strand", "strand"),
        ]
        for ext_label, record_label in extension_and_record_labels:
            if record_label in record and record[record_label]:
                extensions.append(Extension(name=ext_label, value=record[record_label]))

        record_locations = dict()
        if record["item_type"] == RecordType.IDENTITY:
            locs = record.get("locations")
            if locs:
                record_locations[f"{record['src_name'].lower()}_locations"] = locs
        elif record["item_type"] == RecordType.MERGER:
            for k, v in record.items():
                if k.endswith("locations") and v:
                    record_locations[k] = v

        for loc_name, locations in record_locations.items():
            transformed_locs = list()
            for loc in locations:
                transformed_locs.append(self._transform_location(loc))
            extensions.append(Extension(name=loc_name, value=transformed_locs))

        # handle gene types separately because they're wonky
        if record["item_type"] == RecordType.IDENTITY:
            gene_type = record.get("gene_type")
            if gene_type:
                extensions.append(
                    Extension(
                        name=GeneTypeFieldName[record["src_name"].upper()].value,
                        value=gene_type,
                    )
                )
        else:
            for f in GeneTypeFieldName:
                field_name = f.value
                values = record.get(field_name, [])
                for value in values:
                    extensions.append(Extension(name=field_name, value=value))
        if extensions:
            params["extensions"] = extensions

        # add warnings
        if possible_concepts:
            response = self._add_alt_matches(response, record, possible_concepts)

        response.gene_descriptor = GeneDescriptor(**params)
        response = self._add_merged_meta(response)
        response.match_type = match_type
        return response

    @staticmethod
    def _record_order(record: Dict) -> Tuple[int, str]:
        """Construct priority order for matching. Only called by sort().

        :param record: individual record item in iterable to sort
        :return: tuple with rank value and concept ID
        """
        src = record["src_name"].upper()
        source_rank = SourcePriority[src]
        return source_rank, record["concept_id"]

    @staticmethod
    def _handle_failed_merge_ref(record: Dict, response: Dict, query: str) -> Dict:
        """Log + fill out response for a failed merge reference lookup.

        :param record: record containing failed merge_ref
        :param response: in-progress response object
        :param query: original query value
        :return: response with no match
        """
        logger.error(
            f"Merge ref lookup failed for ref {record['merge_ref']} "
            f"in record {record['concept_id']} from query {query}"
        )
        response["match_type"] = MatchType.NO_MATCH
        return response

    def _prepare_normalized_response(self, query: str) -> Dict[str, Any]:
        """Provide base response object for normalize endpoints.

        :param query: user-provided query
        :return: basic normalization response boilerplate
        """
        return {
            "query": query,
            "match_type": MatchType.NO_MATCH,
            "warnings": self._emit_warnings(query),
            "service_meta_": ServiceMeta(
                version=__version__, response_datetime=str(datetime.now())
            ),
        }

    def normalize(self, query: str) -> NormalizeService:
        """Return normalized concept for query.

        Use to retrieve normalized gene concept records:

        >>> from gene.query import QueryHandler
        >>> from gene.database import create_db
        >>> q = QueryHandler(create_db())
        >>> result = q.normalize("BRAF")
        >>> result.gene_descriptor.gene_id
        'hgnc:1097'
        >>> result.xrefs
        ['ensembl:ENSG00000157764', 'ncbigene:673']

        :param query: String to find normalized concept for
        :return: Normalized gene concept
        """
        response = NormalizeService(**self._prepare_normalized_response(query))
        return self._perform_normalized_lookup(
            response, query, self._add_gene_descriptor
        )

    def _resolve_merge(
        self,
        response: NormService,
        record: Dict,
        match_type: MatchType,
        callback: Callable,
        possible_concepts: Optional[List[str]] = None,
    ) -> NormService:
        """Given a record, return the corresponding normalized record

        :param response: in-progress response object
        :param record: record to retrieve normalized concept for
        :param match_type: type of match that returned these records
        :param callback: response constructor method
        :param possible_concepts: alternate possible matches
        :return: Normalized response object
        """
        merge_ref = record.get("merge_ref")
        if merge_ref:
            # follow merge_ref
            merge = self.db.get_record_by_id(merge_ref, False, True)
            if merge is None:
                query = response.query
                logger.error(
                    f"Merge ref lookup failed for ref {record['merge_ref']} "
                    f"in record {record['concept_id']} from query `{query}`"
                )
                return response
            else:
                return callback(response, merge, match_type, possible_concepts)
        else:
            # record is sole member of concept group
            return callback(response, record, match_type, possible_concepts)

    def _perform_normalized_lookup(
        self, response: NormService, query: str, response_builder: Callable
    ) -> NormService:
        """Retrieve normalized concept, for use in normalization endpoints

        :param response: in-progress response object
        :param query: user-provided query
        :param response_builder: response constructor callback method
        :return: completed service response object
        """
        if query == "":
            return response
        query_str = query.lower().strip()

        # check merged concept ID match
        record = self.db.get_record_by_id(query_str, case_sensitive=False, merge=True)
        if record:
            return response_builder(response, record, MatchType.CONCEPT_ID)

        # check concept ID match
        record = self.db.get_record_by_id(query_str, case_sensitive=False)
        if record:
            return self._resolve_merge(
                response, record, MatchType.CONCEPT_ID, response_builder
            )

        for match_type in RefType:
            # get matches list for match tier
            matching_refs = self.db.get_refs_by_type(query_str, match_type)
            matching_records = [
                self.db.get_record_by_id(ref, False) for ref in matching_refs
            ]
            matching_records.sort(key=self._record_order)  # type: ignore

            if len(matching_refs) > 1:
                possible_concepts = [ref for ref in matching_refs]
            else:
                possible_concepts = None

            # attempt merge ref resolution until successful
            for match in matching_records:
                assert match is not None
                record = self.db.get_record_by_id(match["concept_id"], False)
                if record:
                    match_type_value = MatchType[match_type.value.upper()]
                    return self._resolve_merge(
                        response,
                        record,
                        match_type_value,
                        response_builder,
                        possible_concepts,
                    )
        return response

    def _add_normalized_records(
        self,
        response: UnmergedNormalizationService,
        normalized_record: Dict,
        match_type: MatchType,
        possible_concepts: Optional[List[str]] = None,
    ) -> UnmergedNormalizationService:
        """Add individual records to unmerged normalize response.

        :param response: in-progress response
        :param normalized_record: record associated with normalized concept, either
        merged or single identity
        :param match_type: type of match achieved
        :param possible_concepts: other possible results
        :return: Completed response object
        """
        response.match_type = match_type
        response.normalized_concept_id = normalized_record["concept_id"]
        if normalized_record["item_type"] == RecordType.IDENTITY:
            record_source = SourceName[normalized_record["src_name"].upper()]
            meta = self.db.get_source_metadata(record_source.value)
            response.source_matches[record_source] = MatchesNormalized(
                records=[BaseGene(**self._transform_locations(normalized_record))],
                source_meta_=meta,  # type: ignore
            )
        else:
            concept_ids = [normalized_record["concept_id"]] + normalized_record.get(
                "xrefs", []
            )
            for concept_id in concept_ids:
                record = self.db.get_record_by_id(concept_id, case_sensitive=False)
                if not record:
                    continue
                record_source = SourceName[record["src_name"].upper()]
                gene = BaseGene(**self._transform_locations(record))
                if record_source in response.source_matches:
                    response.source_matches[record_source].records.append(gene)
                else:
                    meta = self.db.get_source_metadata(record_source.value)
                    response.source_matches[record_source] = MatchesNormalized(
                        records=[gene],
                        source_meta_=meta,  # type: ignore
                    )
        if possible_concepts:
            response = self._add_alt_matches(
                response, normalized_record, possible_concepts
            )
        return response

    def normalize_unmerged(self, query: str) -> UnmergedNormalizationService:
        """Return all source records under the normalized concept for the
        provided query string.

        >>> from gene.query import QueryHandler
        >>> from gene.database import create_db
        >>> from gene.schemas import SourceName
        >>> q = QueryHandler(create_db())
        >>> response = q.normalize_unmerged("BRAF")
        >>> response.match_type
        <MatchType.CONCEPT_ID: 100>
        >>> response.source_matches[SourceName.ENSEMBL].concept_id
        'ensembl:ENSG00000157764'

        :param query: string to search against
        :return: Normalized response object
        """
        response = UnmergedNormalizationService(
            source_matches={}, **self._prepare_normalized_response(query)
        )
        return self._perform_normalized_lookup(
            response, query, self._add_normalized_records
        )
