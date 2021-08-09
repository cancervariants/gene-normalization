"""This module provides methods for handling queries."""
import re
from typing import List, Dict, Set
from urllib.parse import quote
from uvicorn.config import logger
from .version import __version__
from gene import NAMESPACE_LOOKUP, PREFIX_LOOKUP, ITEM_TYPES
from gene.database import Database
from gene.schemas import Gene, SourceMeta, MatchType, SourceName, \
    ServiceMeta, GeneDescriptor, GeneValueObject, Extension, SourcePriority, \
    NormalizeService, SearchService
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from datetime import datetime


class InvalidParameterException(Exception):
    """Exception for invalid parameter args provided by the user."""

    def __init__(self, message: str):
        """Create new instance

        :param str message: string describing the nature of the error
        """
        super().__init__(message)


class QueryHandler:
    """Class for normalizer management. Stores reference to database instance
    and normalizes query input.
    """

    def __init__(self, db_url: str = '', db_region: str = 'us-east-2'):
        """Initialize QueryHandler instance.

        :param str db_url: URL to database source.
        :param str db_region: AWS default region.
        """
        self.db = Database(db_url=db_url, region_name=db_region)

    def emit_warnings(self, query_str: str) -> List:
        """Emit warnings if query contains non breaking space characters.

        :param str query_str: query string
        :return: List of warnings
        """
        warnings = []
        nbsp = re.search('\xa0|&nbsp;', query_str)
        if nbsp:
            warnings = [
                {
                    "non_breaking_space_characters":
                        "Query contains non-breaking space characters"
                }
            ]
            logger.warning(
                f'Query ({query_str}) contains non-breaking space characters.'
            )
        return warnings

    def fetch_meta(self, src_name: str) -> SourceMeta:
        """Fetch metadata for src_name.

        :param str src_name: name of source to get metadata for
        :return: SourceMeta object containing source metadata
        """
        if src_name in self.db.cached_sources.keys():
            return self.db.cached_sources[src_name]
        else:
            try:
                db_response = self.db.metadata.get_item(Key={'src_name':
                                                             src_name})
                response = SourceMeta(**db_response['Item'])
                self.db.cached_sources[src_name] = response
                return response
            except ClientError as e:
                logger.error(e.response['Error']['Message'])

    def add_record(self,
                   response: Dict[str, Dict],
                   item: Dict,
                   match_type: MatchType) -> (Dict, str):
        """Add individual record (i.e. Item in DynamoDB) to response object

        :param Dict[str, Dict] response: in-progress response object to return
            to client
        :param Dict item: Item retrieved from DynamoDB
        :param MatchTy pe match_type: type of query match
        :return: Tuple containing updated response object, and string
            containing name of the source of the match
        """
        del item['label_and_type']
        # DynamoDB Numbers get converted to Decimal
        if 'locations' in item:
            for loc in item['locations']:
                if loc['interval']['type'] == "SimpleInterval":
                    loc['interval']['start'] = int(loc['interval']['start'])
                    loc['interval']['end'] = int(loc['interval']['end'])
        gene = Gene(**item)
        src_name = item['src_name']

        matches = response['source_matches']
        if src_name not in matches.keys():
            pass
        elif matches[src_name] is None:
            matches[src_name] = {
                'match_type': match_type,
                'records': [gene],
                'source_meta_': self.fetch_meta(src_name)
            }
        elif matches[src_name]['match_type'].value == match_type.value:
            matches[src_name]['records'].append(gene)

        return (response, src_name)

    def fetch_records(self,
                      response: Dict[str, Dict],
                      concept_ids: List[str],
                      match_type: MatchType) -> (Dict, Set):
        """Return matched Gene records as a structured response for a given
        collection of concept IDs.

        :param Dict[str, Dict] response: in-progress response object to return
            to client.
        :param List[str] concept_ids: List of concept IDs to build from.
            Should be all lower-case.
        :param MatchType match_type: record should be assigned this type of
            match.
        :return: response Dict with records filled in via provided concept
            IDs, and Set of source names of matched records
        """
        matched_sources = set()
        for concept_id in concept_ids:
            try:
                pk = f'{concept_id.lower()}##identity'
                filter_exp = Key('label_and_type').eq(pk)
                result = self.db.genes.query(KeyConditionExpression=filter_exp)
                match = result['Items'][0]
                (response, src) = self.add_record(response, match, match_type)
                matched_sources.add(src)
            except ClientError as e:
                logger.error(e.response['Error']['Message'])

        return (response, matched_sources)

    def fill_no_matches(self, resp: Dict) -> Dict:
        """Fill all empty source_matches slots with NO_MATCH results.

        :param Dict resp: incoming response object
        :return: response object with empty source slots filled with
                NO_MATCH results and corresponding source metadata
        """
        for src_name in resp['source_matches'].keys():
            if resp['source_matches'][src_name] is None:
                resp['source_matches'][src_name] = {
                    'match_type': MatchType.NO_MATCH,
                    'records': [],
                    'source_meta_': self.fetch_meta(src_name)
                }
        return resp

    def check_concept_id(self,
                         query: str,
                         resp: Dict,
                         sources: Set[str]) -> (Dict, Set):
        """Check query for concept ID match. Should only find 0 or 1 matches,
        but stores them as a collection to be safe.

        :param str query: search string
        :param Dict resp: in-progress response object to return to client
        :param Set[str] sources: remaining unmatched sources
        :return: Tuple with updated resp object and updated set of unmatched
            sources
        """
        concept_id_items = []
        if [p for p in PREFIX_LOOKUP.keys() if query.startswith(p)]:
            pk = f'{query}##identity'
            filter_exp = Key('label_and_type').eq(pk)
            try:
                result = self.db.genes.query(KeyConditionExpression=filter_exp)
                if len(result['Items']) > 0:
                    concept_id_items += result['Items']
            except ClientError as e:
                logger.error(e.response['Error']['Message'])
        for prefix in [p for p in NAMESPACE_LOOKUP.keys() if
                       query.startswith(p)]:
            pk = f'{NAMESPACE_LOOKUP[prefix].lower()}:{query}##identity'
            filter_exp = Key('label_and_type').eq(pk)
            try:
                result = self.db.genes.query(
                    KeyConditionExpression=filter_exp
                )
                if len(result['Items']) > 0:  # TODO remove check?
                    concept_id_items += result['Items']
            except ClientError as e:
                logger.error(e.response['Error']['Message'])

        for item in concept_id_items:
            (resp, src_name) = self.add_record(resp, item,
                                               MatchType.CONCEPT_ID)
            sources = sources - {src_name}
        return (resp, sources)

    def check_match_type(self,
                         query: str,
                         resp: Dict,
                         sources: Set[str],
                         match: str) -> (Dict, Set):
        """Check query for selected match type.

        :param str query: search string
        :param Dict resp: in-progress response object to return to client
        :param Set[str] sources: remaining unmatched sources
        :param str match: Match type name
        :return: Tuple with updated resp object and updated set of unmatched
                 sources
        """
        filter_exp = Key('label_and_type').eq(f'{query}##{match}')
        try:
            db_response = self.db.genes.query(
                KeyConditionExpression=filter_exp
            )
            if 'Items' in db_response.keys():
                concept_ids = [i['concept_id'] for i in db_response['Items']]
                (resp, matched_srcs) = self.fetch_records(
                    resp, concept_ids, MatchType[match.upper()]
                )
                sources = sources - matched_srcs
        except ClientError as e:
            logger.error(e.response['Error']['Message'])
        return (resp, sources)

    def response_keyed(self, query: str, sources: List[str]) -> Dict:
        """Return response as dict where key is source name and value
        is a list of records. Corresponds to `keyed=true` API parameter.

        :param str query: string to match against
        :param List[str] sources: sources to match from
        :return: completed response object to return to client
        """
        resp = {
            'query': query,
            'warnings': self.emit_warnings(query),
            'source_matches': {
                source: None for source in sources
            }
        }
        if query == '':
            resp = self.fill_no_matches(resp)
            return resp
        query_l = query.lower()

        # check if concept ID match
        (resp, sources) = self.check_concept_id(query_l, resp, sources)
        if len(sources) == 0:
            return resp

        for match in ITEM_TYPES.values():
            (resp, sources) = self.check_match_type(
                query_l, resp, sources, match)
            if len(sources) == 0:
                return resp

        # remaining sources get no match
        resp = self.fill_no_matches(resp)

        return resp

    def response_list(self, query: str, sources: List[str]) -> Dict:
        """Return response as list, where the first key-value in each item
        is the source name. Corresponds to `keyed=false` API parameter.

        :param str query: string to match against
        :param List[str] sources: sources to match from
        :return: completed response object to return to client
        """
        response_dict = self.response_keyed(query, sources)
        source_list = []
        for src_name in response_dict['source_matches'].keys():
            src = {
                "source": src_name,
            }
            to_merge = response_dict['source_matches'][src_name]
            src.update(to_merge)

            source_list.append(src)
        response_dict['source_matches'] = source_list

        return response_dict

    def _get_service_meta(self) -> ServiceMeta:
        """Return metadata about gene-normalizer service.

        :return: Service Meta
        """
        return ServiceMeta(
            version=__version__,
            response_datetime=datetime.now()
        )

    def search(self, query_str: str, keyed: bool = False,
               incl: str = '', excl: str = '', **params):
        """Return highest match for each source.

        :param str query_str: query, a string, to search for
        :param bool keyed: if true, return response as dict keying source names
            to source objects; otherwise, return list of source objects
        :param str incl: str containing comma-separated names of sources to
            use. Will exclude all other sources. Case-insensitive. Raises
            InvalidParameterException if both incl and excl args are
            provided, or if invalid source names are given.
        :param str excl: str containing comma-separated names of source to
            exclude. Will include all other source. Case-insensitive. Raises
            InvalidParameterException if both incl and excl args are
            provided, or if invalid source names are given.
        :return: dict containing all matches found in sources.
        """
        possible_sources = {name.value.lower(): name.value for name in
                            SourceName.__members__.values()}
        sources = dict()
        for k, v in possible_sources.items():
            if self.db.metadata.get_item(Key={'src_name': v}).get('Item'):
                sources[k] = v

        if not incl and not excl:
            query_sources = set(sources.values())
        elif incl and excl:
            detail = "Cannot request both source inclusions and exclusions."
            raise InvalidParameterException(detail)
        elif incl:
            req_sources = [n.strip() for n in incl.split(',')]
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
            req_exclusions = [n.strip() for n in excl.lower().split(',')]
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
            resp = self.response_keyed(query_str, query_sources)
        else:
            resp = self.response_list(query_str, query_sources)

        resp['service_meta_'] = self._get_service_meta()
        assert SearchService(**resp)
        return resp

    def _add_merged_meta(self, response: Dict) -> Dict:
        """Add source metadata to response object.

        :param Dict response: in-progress response object
        :return: completed response object.
        """
        sources_meta = {}
        gene_descr = response['gene_descriptor']
        ids = [gene_descr['value']['id']] + gene_descr.get('xrefs', [])
        for concept_id in ids:
            prefix = concept_id.split(':')[0]
            src_name = PREFIX_LOOKUP[prefix.lower()]
            if src_name not in sources_meta:
                sources_meta[src_name] = self.fetch_meta(src_name)
        response['source_meta_'] = sources_meta
        return response

    def add_gene_descriptor(self, response, record, match_type,
                            possible_concepts=[]):
        """Add gene descriptor to response.

        :param Dict response: Response object
        :param Dict record: Gene record
        :param MatchType match_type: query's match type
        :param list possible_concepts: List of other normalized concepts
            found
        :return: Response with gene descriptor
        """
        params = {
            "id": f"normalize.gene:{quote(response['query'])}",
            "label": record["symbol"],
            "value": GeneValueObject(id=record["concept_id"])
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
            ("chromosome_location", "locations"),
            ("associated_with", "associated_with"),
            ("previous_symbols", "previous_symbols")
        ]
        for ext_label, record_label in extension_and_record_labels:
            if record_label in record and record[record_label]:
                if ext_label == 'chromosome_location':
                    record[record_label] = record[record_label][0]
                extensions.append(Extension(
                    name=ext_label,
                    value=record[record_label]
                ))
        if extensions:
            params["extensions"] = extensions

        # add warnings
        if possible_concepts:
            norm_concepts = set()
            for concept_id in possible_concepts:
                r = self.db.get_record_by_id(concept_id, True)
                if r:
                    merge_ref = r.get("merge_ref")
                    if merge_ref:
                        norm_concepts.add(merge_ref)
            norm_concepts = norm_concepts - {record["concept_id"]}
            if norm_concepts:
                response["warnings"].append(
                    {
                        "multiple_normalized_concepts_found":
                            list(norm_concepts)
                    }
                )
        response["gene_descriptor"] = \
            GeneDescriptor(**params).dict(exclude_none=True)
        response = self._add_merged_meta(response)
        response["match_type"] = match_type
        return response

    def _record_order(self, record: Dict) -> (int, str):
        """Construct priority order for matching. Only called by sort().

        :param Dict record: individual record item in iterable to sort
        :return: tuple with rank value and concept ID
        """
        src = record['src_name'].upper()
        source_rank = SourcePriority[src]
        return source_rank, record['concept_id']

    def _handle_failed_merge_ref(self, record, response, query) -> Dict:
        """Log + fill out response for a failed merge reference lookup.

        :param Dict record: record containing failed merge_ref
        :param Dict response: in-progress response object
        :param str query: original query value
        :return: response with no match
        """
        logger.error(f"Merge ref lookup failed for ref {record['merge_ref']} "
                     f"in record {record['concept_id']} from query {query}")
        response['match_type'] = MatchType.NO_MATCH
        return response

    def normalize(self, query: str) -> Dict:
        """Return normalized concept for query.

        :param str query: String to find normalized concept for
        :return: Normalized gene concept
        """
        response = {
            "query": query,
            "warnings": self.emit_warnings(query),
            "service_meta_": self._get_service_meta()
        }

        if query == '':
            response['match_type'] = MatchType.NO_MATCH
            return response
        query_str = query.lower().strip()

        # check merged concept ID match
        record = self.db.get_record_by_id(query_str, case_sensitive=False,
                                          merge=True)
        if record:
            return self.add_gene_descriptor(response, record,
                                            MatchType.CONCEPT_ID)

        # check concept ID match
        record = self.db.get_record_by_id(query_str, case_sensitive=False)
        if record:
            merge_ref = record.get('merge_ref')
            if not merge_ref:
                return self.add_gene_descriptor(response, record,
                                                MatchType.CONCEPT_ID)
            merge = self.db.get_record_by_id(merge_ref,
                                             case_sensitive=False,
                                             merge=True)
            if merge is None:
                return self._handle_failed_merge_ref(record, response,
                                                     query_str)
            else:
                return self.add_gene_descriptor(response, merge,
                                                MatchType.CONCEPT_ID)

        # check other match types
        matching_records = None
        for match_type in ITEM_TYPES.values():
            # get matches list for match tier
            matching_refs = self.db.get_records_by_type(query_str, match_type)
            matching_records = \
                [self.db.get_record_by_id(m['concept_id'], False)
                 for m in matching_refs]
            matching_records.sort(key=self._record_order)

            if len(matching_refs) > 1:
                possible_concepts = \
                    [ref["concept_id"] for ref in matching_refs]
            else:
                possible_concepts = []

            # attempt merge ref resolution until successful
            for match in matching_records:
                record = self.db.get_record_by_id(match['concept_id'], False)
                if record:
                    merge_ref = record.get('merge_ref')
                    if not merge_ref:
                        return self.add_gene_descriptor(
                            response, record,
                            MatchType[match_type.upper()],
                            possible_concepts
                        )
                    merge = self.db.get_record_by_id(record['merge_ref'],
                                                     case_sensitive=False,
                                                     merge=True)
                    if merge is None:
                        return self._handle_failed_merge_ref(record, response,
                                                             query_str)
                    else:
                        return self.add_gene_descriptor(
                            response, merge,
                            MatchType[match_type.upper()],
                            possible_concepts
                        )

        if not matching_records:
            response['match_type'] = MatchType.NO_MATCH
        assert NormalizeService(**response)
        return response
