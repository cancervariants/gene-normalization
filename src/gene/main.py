"""Main application for FastAPI"""
import html
from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from gene import SOURCES, __version__
from gene.database import create_db
from gene.query import QueryHandler
from gene.schemas import (
    NormalizeService,
    SearchService,
    SourceName,
    UnmergedNormalizationService,
)

db = create_db()
query_handler = QueryHandler(db)

description = """
The Gene Normalizer provides tools for resolving ambiguous gene references to
consistently-structured, normalized terms.

See the [documentation](https://gene-normalizer.readthedocs.io/en/latest/) for more
information.
"""

app = FastAPI(
    title="Gene Normalizer",
    description=description,
    version=__version__,
    contact={
        "name": "Alex H. Wagner",
        "email": "Alex.Wagner@nationwidechildrens.org",
        "url": "https://www.nationwidechildrens.org/specialties/institute-for-genomic-medicine/research-labs/wagner-lab",  # noqa: E501
    },
    license={
        "name": "MIT",
        "url": "https://github.com/cancervariants/gene-normalization/blob/main/LICENSE",
    },
    docs_url="/gene",
    openapi_url="/gene/openapi.json",
    swagger_ui_parameters={"tryItOutEnabled": True},
)


read_query_summary = "Given query, provide best-matching source records."
response_description = "A response to a validly-formed query"
q_descr = "Gene to normalize."
sources_descr = (
    "Optional. Comma-separated list of source names to include in response, if given. "
    "Will exclude all other sources."
)
search_description = (
    "For each source, return strongest-match concepts "
    "for query string provided by user"
)


@app.get(
    "/gene/search",
    summary=read_query_summary,
    response_description=response_description,
    response_model=SearchService,
    description=search_description,
    tags=["Query"],
)
def search(
    q: str = Query(..., description=q_descr),  # noqa: D103
    sources: Optional[str] = Query(None, description=sources_descr),
) -> SearchService:
    """Return strongest match concepts to query string provided by user.

    :param q: gene search term
    :param sources: If given, search only for records from these sources.
        Provide as string of source names separated by commas.
    :return: JSON response with matched records and source metadata
    """
    parsed_sources = []
    if sources:
        for candidate_source in sources.split(","):
            try:
                parsed_source = SourceName[
                    SOURCES[candidate_source.strip().lower()].upper()
                ]
            except KeyError:
                raise HTTPException(
                    status_code=422,
                    detail=f"Unable to parse source name: {candidate_source}",
                )
            parsed_sources.append(parsed_source)
    resp = query_handler.search(html.unescape(q), sources=parsed_sources)
    return resp


normalize_summary = "Given query, provide merged normalized record."
normalize_response_descr = "A response to a validly-formed query."
normalize_descr = "Return merged highest-match concept for query."
normalize_q_descr = "Gene to normalize."


@app.get(
    "/gene/normalize",
    summary=normalize_summary,
    response_description=normalize_response_descr,
    response_model=NormalizeService,
    response_model_exclude_none=True,
    description=normalize_descr,
    tags=["Query"],
)
def normalize(q: str = Query(..., description=normalize_q_descr)) -> NormalizeService:
    """Return strongest match concepts to query string provided by user.

    :param str q: gene search term
    :return: JSON response with normalized gene concept
    """
    resp = query_handler.normalize(html.unescape(q))
    return resp


unmerged_matches_summary = (
    "Given query, provide source records corresponding to " "normalized concept."
)
unmerged_response_descr = (
    "Response containing source records contained within " "normalized concept."
)
unmerged_normalize_description = (
    "Return unmerged records associated with the "
    "normalized result of the user-provided query "
    "string."
)


@app.get(
    "/gene/normalize_unmerged",
    summary=unmerged_matches_summary,
    operation_id="getUnmergedRecords",
    response_description=unmerged_response_descr,
    response_model=UnmergedNormalizationService,
    description=unmerged_normalize_description,
    tags=["Query"],
)
def normalize_unmerged(
    q: str = Query(..., description=normalize_q_descr)
) -> UnmergedNormalizationService:
    """Return all individual records associated with a normalized concept.

    :param q: Gene search term
    :returns: JSON response with matching normalized record and source metadata
    """
    response = query_handler.normalize_unmerged(html.unescape(q))
    return response
