"""Provides methods for handling queries."""

import datetime
import logging
import re
from collections.abc import Callable
from typing import Any, TypeVar

from ga4gh.core import ga4gh_identify
from ga4gh.core.models import (
    Coding,
    ConceptMapping,
    Extension,
    MappableConcept,
    Relation,
    code,
)
from ga4gh.vrs.models import SequenceLocation, SequenceReference

from gene import ITEM_TYPES, NAMESPACE_LOOKUP, PREFIX_LOOKUP, __version__
from gene.database import AbstractDatabase, DatabaseReadException
from gene.schemas import (
    NAMESPACE_TO_SYSTEM_URI,
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
    SourceMeta,
    SourceName,
    SourcePriority,
    UnmergedNormalizationService,
)

_logger = logging.getLogger(__name__)

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
    def _emit_warnings(query_str: str) -> list:
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
            _logger.warning(
                "Query (%s) contains non-breaking space characters.", query_str
            )
        return warnings

    @staticmethod
    def _transform_sequence_location(loc: dict) -> SequenceLocation:
        """Transform a sequence location to VRS sequence location

        :param loc: GeneSequenceLocation represented as a dict
        :return: VRS sequence location
        """
        refget_ac = loc["sequence_id"].split("ga4gh:")[-1]

        return SequenceLocation(
            sequenceReference=SequenceReference(refgetAccession=refget_ac),
            start=int(loc["start"]),
            end=int(loc["end"]),
        )

    def _transform_location(self, loc: dict) -> dict:
        """Transform a sequence location to VRS sequence location

        :param loc: Sequence location
        :return: VRS sequence location represented as a dictionary
        """
        transformed_loc = self._transform_sequence_location(loc)
        transformed_loc.id = ga4gh_identify(transformed_loc)
        return transformed_loc.model_dump(exclude_none=True)

    def _transform_locations(self, record: dict) -> dict:
        """Transform gene locations to VRS Sequence Locations

        :param record: original record
        :return: record with transformed locations attributes, if applicable
        """
        record_locations = []
        if "locations" in record:
            record_locations.extend(
                self._transform_location(loc)
                for loc in record["locations"]
                if loc["type"] == "SequenceLocation"
            )
        record["locations"] = record_locations
        return record

    def _add_record(
        self, response: dict[str, dict], item: dict, match_type: MatchType
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
        if src_name not in matches:
            pass
        elif matches[src_name] is None:
            matches[src_name] = {
                "records": [gene],
                "source_meta_": self.db.get_source_metadata(src_name),
            }
        else:
            matches[src_name]["records"].append(gene)

    def _fetch_record(
        self, response: dict[str, dict], concept_id: str, match_type: MatchType
    ) -> None:
        """Add fetched record to response

        :param response: in-progress response object to return to client.
        :param concept_id: Concept id to fetch record for. Should be all lower-case.
        :param match_type: match type for record
        """
        try:
            match = self.db.get_record_by_id(concept_id, case_sensitive=False)
        except DatabaseReadException:
            _logger.exception(
                "Encountered DatabaseReadException looking up %s", concept_id
            )
        else:
            if match:
                self._add_record(response, match, match_type)
            else:
                _logger.error(
                    "Unable to find expected record for %s matching as %s",
                    concept_id,
                    match_type,
                )

    def _post_process_resp(self, resp: dict) -> dict:
        """Fill all empty source_matches slots with NO_MATCH results and
        sort source records by descending `match_type`.

        :param resp: incoming response object
        :return: response object with empty source slots filled with NO_MATCH results
            and corresponding source metadata
        """
        for src_name in resp["source_matches"]:
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

    def _get_search_response(self, query: str, sources: set[str]) -> dict:
        """Return response as dict where key is source name and value is a list of
        records.

        :param query: string to match against
        :param sources: sources to match from
        :return: completed response object to return to client
        """
        resp = {
            "query": query,
            "warnings": self._emit_warnings(query),
            "source_matches": dict.fromkeys(sources),
        }
        if query == "":
            return self._post_process_resp(resp)
        query_l = query.lower()

        queries = []
        if [p for p in PREFIX_LOOKUP if query_l.startswith(p)]:
            queries.append((query_l, RecordType.IDENTITY.value))

        for prefix in [p for p in NAMESPACE_LOOKUP if query_l.startswith(p)]:
            term = f"{NAMESPACE_LOOKUP[prefix].lower()}:{query_l}"
            queries.append((term, RecordType.IDENTITY.value))

        queries.extend((query_l, match) for match in ITEM_TYPES.values())

        matched_concept_ids = []
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

            except DatabaseReadException:
                _logger.exception(
                    "Encountered DatabaseReadException looking up %s %s: ",
                    item_type,
                    term,
                )
                continue

        # remaining sources get no match
        return self._post_process_resp(resp)

    @staticmethod
    def _get_service_meta() -> ServiceMeta:
        """Return metadata about gene-normalizer service.

        :return: Service Meta
        """
        return ServiceMeta(
            version=__version__,
            response_datetime=str(datetime.datetime.now(tz=datetime.UTC)),
        )

    def search(
        self,
        query_str: str,
        incl: str = "",
        excl: str = "",
    ) -> SearchService:
        """Return highest match for each source.

        >>> from gene.query import QueryHandler
        >>> from gene.database import create_db
        >>> q = QueryHandler(create_db())
        >>> result = q.search("BRAF")
        >>> result.source_matches[0].records[0].concept_id
        'ncbigene:673'

        :param query_str: query, a string, to search for
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
        sources = {
            k: v for k, v in possible_sources.items() if self.db.get_source_metadata(v)
        }

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
                if source.lower() in sources:
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
                if req_l not in sources:
                    invalid_sources.append(req)
            for src_l, src in sources.items():
                if src_l not in req_excl_dict:
                    query_sources.add(src)
            if invalid_sources:
                detail = f"Invalid source name(s): {invalid_sources}"
                raise InvalidParameterException(detail)

        query_str = query_str.strip()

        resp = self._get_search_response(query_str, query_sources)

        resp["service_meta_"] = self._get_service_meta()
        return SearchService(**resp)

    def _add_merged_meta(self, response: NormalizeService) -> NormalizeService:
        """Add source metadata to response object.

        :param response: in-progress response object
        :return: completed response object.
        """
        sources_meta = {}
        gene = response.gene

        sources = []
        for m in gene.mappings or []:
            ns = m.coding.id.split(":")[0]
            if ns in PREFIX_LOOKUP:
                sources.append(PREFIX_LOOKUP[ns])

        # Add metadata for primaryCoding id
        sources.append(PREFIX_LOOKUP[gene.primaryCoding.id.split(":")[0]])

        for src in sources:
            if src not in sources_meta:
                _source_meta = self.db.get_source_metadata(src)
                sources_meta[SourceName(src)] = SourceMeta(**_source_meta)
        response.source_meta_ = sources_meta
        return response

    def _add_alt_matches(
        self, response: NormService, record: dict, possible_concepts: list[str]
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

    def _add_gene(
        self,
        response: NormalizeService,
        record: dict,
        match_type: MatchType,
        possible_concepts: list[str] | None = None,
    ) -> NormalizeService:
        """Add core Gene object to response.

        :param response: Response object
        :param record: Gene record
        :param match_type: query's match type
        :param possible_concepts: List of other normalized concepts found
        :raises ValueError: If source of record's concept ID or xrefs/associated with
            sources is not a valid ``NamespacePrefix``
        :return: Response with core Gene
        """

        def _get_coding_object(concept_id: str) -> Coding:
            """Get coding object for CURIE identifier

            ``system`` will use system prefix URL or system homepage

            :param concept_id: A lowercase concept identifier represented as a curie
            :return: Coding object for identifier
            :raises ValueError: If source of concept ID is not a valid
                ``NamespacePrefix``
            """
            source, source_code = concept_id.split(":")

            try:
                source = NamespacePrefix(source)
            except ValueError as e:
                err_msg = f"Namespace prefix not supported: {source}"
                raise ValueError(err_msg) from e

            if source == NamespacePrefix.HGNC:
                source_code = concept_id.upper()

            return Coding(
                id=concept_id,
                code=code(source_code),
                system=NAMESPACE_TO_SYSTEM_URI[source],
            )

        def _get_concept_mapping(
            concept_id: str, relation: Relation = Relation.RELATED_MATCH
        ) -> ConceptMapping:
            """Get concept mapping for Coding object

            :param concept_id: A lowercase concept identifier represented as a curie
            :param relation: SKOS mapping relationship, default is relatedMatch
            :return: Concept mapping for identifier
            """
            return ConceptMapping(
                coding=_get_coding_object(concept_id),
                relation=relation,
            )

        gene_obj = MappableConcept(
            id=f"normalize.gene.{record['concept_id']}",
            primaryCoding=_get_coding_object(record["concept_id"]),
            name=record["symbol"],
            conceptType="Gene",
        )

        xrefs = [record["concept_id"], *record.get("xrefs", [])]
        gene_obj.mappings = [
            _get_concept_mapping(xref_id, relation=Relation.EXACT_MATCH)
            for xref_id in xrefs
            if xref_id != record["concept_id"]
        ]

        associated_with = record.get("associated_with", [])
        gene_obj.mappings.extend(
            _get_concept_mapping(associated_with_id, relation=Relation.RELATED_MATCH)
            for associated_with_id in associated_with
        )

        # extensions
        extensions = []

        # aliases
        aliases = set()
        for key in ["previous_symbols", "aliases"]:
            if record.get(key):
                val = record[key]
                if isinstance(val, str):
                    val = [val]
                aliases.update(val)
        if aliases:
            extensions.append(Extension(name="aliases", value=list(aliases)))

        extension_and_record_labels = [
            ("symbol_status", "symbol_status"),
            ("approved_name", "label"),
            ("previous_symbols", "previous_symbols"),
            ("location_annotations", "location_annotations"),
            ("strand", "strand"),
        ]
        for ext_label, record_label in extension_and_record_labels:
            if record.get(record_label):
                extensions.append(Extension(name=ext_label, value=record[record_label]))

        record_locations = {}
        if record["item_type"] == RecordType.IDENTITY:
            locs = record.get("locations")
            if locs:
                record_locations[f"{record['src_name'].lower()}_locations"] = locs
        elif record["item_type"] == RecordType.MERGER:
            record_locations.update(
                {k: v for k, v in record.items() if k.endswith("locations") and v}
            )

        for loc_name, locations in record_locations.items():
            transformed_locs = [
                self._transform_location(loc)
                for loc in locations
                if loc["type"] == "SequenceLocation"
            ]

            if transformed_locs:
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
                extensions.extend(
                    Extension(name=field_name, value=value) for value in values
                )
        if extensions:
            gene_obj.extensions = extensions

        # add warnings
        if possible_concepts:
            response = self._add_alt_matches(response, record, possible_concepts)

        response.gene = gene_obj
        response = self._add_merged_meta(response)
        response.match_type = match_type
        return response

    @staticmethod
    def _record_order(record: dict) -> tuple[int, str]:
        """Construct priority order for matching. Only called by sort().

        :param record: individual record item in iterable to sort
        :return: tuple with rank value and concept ID
        """
        src = record["src_name"].upper()
        source_rank = SourcePriority[src]
        return source_rank, record["concept_id"]

    def _prepare_normalized_response(self, query: str) -> dict[str, Any]:
        """Provide base response object for normalize endpoints.

        :param query: user-provided query
        :return: basic normalization response boilerplate
        """
        return {
            "query": query,
            "match_type": MatchType.NO_MATCH,
            "warnings": self._emit_warnings(query),
            "service_meta_": ServiceMeta(
                version=__version__,
                response_datetime=str(datetime.datetime.now(tz=datetime.UTC)),
            ),
        }

    def normalize(self, query: str) -> NormalizeService:
        """Return normalized concept for query.

        Use to retrieve normalized gene concept records:

        >>> from gene.query import QueryHandler
        >>> from gene.database import create_db
        >>> q = QueryHandler(create_db())
        >>> result = q.normalize("BRAF")
        >>> result.gene.primaryCoding.id
        'hgnc:1097'
        >>> next(ext for ext in result.gene.extensions if ext.name == "aliases").value
        ['BRAF1', 'RAFB1', 'B-raf', 'NS7', 'B-RAF1']

        :param query: String to find normalized concept for
        :return: Normalized gene concept
        """
        response = NormalizeService(**self._prepare_normalized_response(query))
        return self._perform_normalized_lookup(response, query, self._add_gene)

    def _resolve_merge(
        self,
        response: NormService,
        record: dict,
        match_type: MatchType,
        callback: Callable,
        possible_concepts: list[str] | None = None,
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
                _logger.error(
                    "Merge ref lookup failed for ref %s in record %s from query `%s`",
                    record["merge_ref"],
                    record["concept_id"],
                    query,
                )
                return response

            return callback(response, merge, match_type, possible_concepts)

        # record is sole member of concept group
        return callback(response, record, match_type, possible_concepts)

    def _perform_normalized_lookup(
        self, response: NormService, query: str, response_builder: Callable
    ) -> NormService:
        """Retrieve normalized concept, for use in normalization endpoints

        :param response: in-progress response object
        :param query: user-provided query
        :param response_builder: response constructor callback method
        :raises ValueError: If a matching record is null
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
            matching_records.sort(key=self._record_order)

            possible_concepts = list(matching_refs) if len(matching_refs) > 1 else None

            # attempt merge ref resolution until successful
            for match in matching_records:
                if match is None:
                    err_msg = "Matching record must be nonnull"
                    raise ValueError(err_msg)
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
        normalized_record: dict,
        match_type: MatchType,
        possible_concepts: list[str] | None = None,
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
                source_meta_=meta,
            )
        else:
            xrefs = normalized_record.get("xrefs") or []
            concept_ids = [normalized_record["concept_id"], *xrefs]
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
                        records=[gene], source_meta_=meta
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
