"""Provides methods for handling queries."""
import logging
import re
from typing import List, Optional, Tuple

from gene.database import AbstractDatabase
from gene.schemas import (
    ITEM_TYPES,
    NAMESPACE_LOOKUP,
    PREFIX_LOOKUP,
    REF_TO_MATCH_MAP,
    Gene,
    GeneMatch,
    MatchType,
    NormalizeResult,
    NormalizeUnmergedMatches,
    NormalizeUnmergedResult,
    QueryWarning,
    RecordType,
    RefType,
    ResultSourceMeta,
    SearchResult,
    SourceName,
    SourcePriority,
    WarningType,
)

_logger = logging.getLogger(__name__)


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
    def _parse_query_input(raw_query: str) -> Tuple[str, List[QueryWarning]]:
        """Preprocess user query:
        * Strip white space
        * Check for non-breaking spaces.

        Return any necessary warnings.

        :param raw_str: raw query string
        :return: updated query and list of warnings
        """
        warning_list = []
        parsed_query = raw_query.strip()
        if raw_query != parsed_query:
            warning_list.append(
                QueryWarning(
                    type=WarningType.STRIPPED_QUERY,
                    description=f'Stripped query "{raw_query}" to "{parsed_query}"',
                )
            )
        nbsp = re.search("\xa0|&nbsp;", parsed_query)
        if nbsp:
            warning_list.append(
                QueryWarning(
                    type=WarningType.NBSP,
                    description="Query contains non-breaking space characters",
                )
            )
            _logger.warning(
                f"Query ({parsed_query}) contains non-breaking space characters."
            )
        return (parsed_query.lower(), warning_list)

    def _get_sources_meta(self, sources: List[SourceName]) -> ResultSourceMeta:
        """Fetch result source meta object.

        :param sources: List of requested sources
        :return: structured source metadata for requested sources
        """
        params = {}
        for name in sources:
            meta = self.db.get_source_metadata(name)
            params[name.value.lower()] = meta
        return ResultSourceMeta(**params)

    @staticmethod
    def _get_search_queries(query: str) -> List[Tuple[str, MatchType]]:
        """Construct list of individual queries and corresponding match types to
        perform.
        * Check if query is a CURIE from a stored source
        * Check if a namespace can be inferred  # TODO update warning somehow
        * Check if the query is a name/reference for any other known item type

        :param query: formatted query from user
        :return: List of queries to perform (search string and corresponding match type)
        """
        queries = []
        if query == "":
            return queries
        if [p for p in PREFIX_LOOKUP.keys() if query.startswith(str(p))]:
            queries.append((query, RecordType.IDENTITY.value))
        for prefix in [p for p in NAMESPACE_LOOKUP.keys() if query.startswith(p)]:
            term = f"{NAMESPACE_LOOKUP[prefix]}:{query}"
            queries.append((term, RecordType.IDENTITY.value))
        for match in ITEM_TYPES.values():
            queries.append((query, match))
        return queries

    def _perform_search_queries(
        self, search_queries: List[Tuple[str, MatchType]]
    ) -> List[Gene]:
        """Run all prepared queries.

        :param search_queries: list of queries (strings + match types) to perform
        :return: list of all matching Genes. Should be non-redundant and ordered by
        match type.
        """
        matched_concept_ids = []
        matched_genes = []
        for term, item_type in search_queries:
            if item_type == RecordType.IDENTITY.value:
                record = self.db.get_record_by_id(term, False)
                if record and record.id not in matched_concept_ids:
                    matched_concept_ids.append(record.id)
                    matched_genes.append(record)
            else:
                refs = self.db.get_ids_by_ref(term, RefType(item_type))
                for ref in refs:
                    if ref not in matched_concept_ids:
                        record = self.db.get_record_by_id(term, False)
                        if record and record.id not in matched_concept_ids:
                            matched_concept_ids.append(record.id)
                            matched_genes.append(record)
        return matched_genes

    def search(
        self, query: str, sources: Optional[List[SourceName]] = None
    ) -> SearchResult:
        """Return all matches for each source.

        >>> from gene.query import QueryHandler
        >>> from gene.database import create_db
        >>> q = QueryHandler(create_db())
        >>> result = q.search("BRAF")
        >>> result.source_matches[0].records[0].concept_id  # TODO update
        'ncbigene:673'

        :param query_str: query, a string, to search for
        :param sources: If given, only return records from these sources
        :return: search response class containing all matches found in sources.
        """
        if not sources:
            sources = list(SourceName.__members__.values())
        parsed_query, warnings = self._parse_query_input(query)
        response = SearchResult(
            warnings=warnings, source_meta=self._get_sources_meta(sources)
        )
        search_queries = self._get_search_queries(parsed_query)
        matched_genes = self._perform_search_queries(search_queries)

        for gene in matched_genes:
            field_name = f"{gene.id.split(':')[0]}_matches"  # type: ignore
            existing_matches = getattr(response, field_name)
            if not existing_matches:
                setattr(response, field_name, [gene])
            else:
                existing_matches.append(gene)

        return response

    def _get_normalized_record(
        self, query: str
    ) -> Optional[Tuple[Gene, MatchType, List[str]]]:
        """Get highest-priority available normalized record.

        :param query: user query
        :return: Tuple containing the normalized gene, the match type that produced it,
            and a list of alternate normalized objects
        """
        # check concept ID match
        record = self.db.get_normalized_record(query)
        if record:
            return (record, MatchType.CONCEPT_ID, [])

        # check each kind of match type
        for match_type in RefType:
            matching_concepts = self.db.get_ids_by_ref(query, match_type)
            matching_concepts.sort(
                key=lambda c: (SourcePriority[PREFIX_LOOKUP[c.split(":")[0]]], c)
            )
            while matching_concepts:
                record = self.db.get_normalized_record(matching_concepts[0])
                if record:
                    return (record, REF_TO_MATCH_MAP[match_type], matching_concepts[1:])
                matching_concepts = matching_concepts[1:]

        return None

    def normalize(self, query: str) -> NormalizeResult:
        """Return normalized concept for query.

        Use to retrieve normalized gene concept records:

        # TODO update this
        >>> from gene.query import QueryHandler
        >>> from gene.database import create_db
        >>> q = QueryHandler(create_db())
        >>> result = q.normalize("BRAF")
        >>> result.normalized_id
        'hgnc:1097'
        >>> result.aliases
        ['BRAF1', 'RAFB1', 'B-raf', 'NS7', 'B-RAF1']

        :param query: String to find normalized concept for
        :return: Normalized gene concept
        """
        parsed_query, warnings = self._parse_query_input(query)
        result = NormalizeResult(
            source_meta=ResultSourceMeta(),
            warnings=warnings,
        )
        normalized_gene = None
        normalized_match = self._get_normalized_record(parsed_query)
        if normalized_match:
            normalized_gene, match_type, alt_matches = normalized_match
            result.match = GeneMatch(gene=normalized_gene, match_type=match_type)
            result.normalized_id = normalized_gene.id[15:]  # type: ignore
            if alt_matches:
                result.warnings.append(  # type: ignore
                    QueryWarning(
                        type=WarningType.MULTIPLE_NORMALIZED_CONCEPTS,
                        description=f"Alternative possible normalized matches: {alt_matches}",
                    )
                )
            concept_ids: List[str] = [result.match.id]  # type: ignore
            if result.match.gene.mappings:
                for mapping in result.match.gene.mappings:
                    concept_ids.append(f"{mapping.coding.system}:{mapping.coding.code}")
            sources = set()
            for concept_id in concept_ids:
                prefix = concept_id.split(":", 1)[0]
                sources.add(SourceName(PREFIX_LOOKUP[prefix]))
            result.source_meta = self._get_sources_meta(list(sources))
        return result

    def _get_unmerged_matches(
        self, normalized_record: Gene
    ) -> NormalizeUnmergedMatches:
        """Acquire source records that make up provided normalized record.

        :param normalized_record: given normalized record
        :return: unmerged matches object with gene records grouped by source
        """
        grouped_genes = {}
        concept_ids: List[str] = [normalized_record.id]  # type: ignore
        if normalized_record.mappings:
            for mapping in normalized_record.mappings:
                concept_ids.append(f"{mapping.coding.system}:{mapping.coding.code}")
        for concept_id in concept_ids:
            record = self.db.get_record_by_id(concept_id)
            if record:
                prefix = record.id.split(":", 1)[0]  # type: ignore
                key = f"{PREFIX_LOOKUP[prefix].lower()}_matches"
                if key in grouped_genes:
                    grouped_genes[key].append(record)
                else:
                    grouped_genes[key] = [record]
        return NormalizeUnmergedMatches(**grouped_genes)

    def normalize_unmerged(self, query: str) -> NormalizeUnmergedResult:
        """Return all source records under the normalized concept for the
        provided query string.

        # TODO update this
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
        parsed_query, warnings = self._parse_query_input(query)
        result = NormalizeUnmergedResult(
            source_meta=ResultSourceMeta(),
            warnings=warnings,
            source_genes=NormalizeUnmergedMatches(),
        )
        normalized_gene = None
        normalized_match = self._get_normalized_record(parsed_query)
        if normalized_match:
            normalized_gene, match_type, alt_matches = normalized_match
            base_match = GeneMatch(gene=normalized_gene, match_type=match_type)
            result.normalized_id = normalized_gene.id[15:]  # type: ignore
            if alt_matches:
                result.warnings.append(  # type: ignore
                    QueryWarning(
                        type=WarningType.MULTIPLE_NORMALIZED_CONCEPTS,
                        description=f"Alternative possible normalized matches: {alt_matches}",
                    )
                )
            result.source_genes = self._get_unmerged_matches(base_match.gene)
            sources = list(result.source_genes.get_matches_by_source().keys())
            result.source_meta = self._get_sources_meta(sources)

        return result
