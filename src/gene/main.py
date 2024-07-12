"""Main application for FastAPI"""

import html

from fastapi import FastAPI, HTTPException, Query

from gene import __version__
from gene.database import create_db
from gene.query import InvalidParameterException, QueryHandler
from gene.schemas import NormalizeService, SearchService, UnmergedNormalizationService

db = create_db()
query_handler = QueryHandler(db)

description = """
The Gene Normalizer provides tools for resolving ambiguous gene references to
consistently-structured, normalized terms.

See the [documentation](https://gene-normalizer.readthedocs.io/latest/) for more
information.
"""

app = FastAPI(
    title="Gene Normalizer",
    description=description,
    version=__version__,
    contact={
        "name": "Alex H. Wagner",
        "email": "Alex.Wagner@nationwidechildrens.org",
        "url": "https://www.nationwidechildrens.org/specialties/institute-for-genomic-medicine/research-labs/wagner-lab",
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
incl_descr = """Optional. Comma-separated list of source names to include in
             response. Will exclude all other sources. Returns HTTP status code
             422: Unprocessable Entity if both 'incl' and 'excl' parameters
             are given."""
excl_descr = """Optional. Comma-separated list of source names to exclude in
             response. Will include all other sources. Returns HTTP status
             code 422: Unprocessable Entity if both 'incl' and 'excl'
             parameters are given."""
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
    q: str = Query(..., description=q_descr),
    incl: str | None = Query(None, description=incl_descr),
    excl: str | None = Query(None, description=excl_descr),
) -> SearchService:
    """Return strongest match concepts to query string provided by user.

    :param str q: gene search term
    :param Optional[str] incl: comma-separated list of sources to include,
        with all others excluded. Raises HTTPException if both `incl` and
        `excl` are given.
    :param Optional[str] excl: comma-separated list of sources exclude, with
        all others included. Raises HTTPException if both `incl` and `excl`
        are given.
    :return: JSON response with matched records and source metadata
    """
    try:
        resp = query_handler.search(html.unescape(q), incl=incl, excl=excl)
    except InvalidParameterException as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
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
    return query_handler.normalize(html.unescape(q))


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
    q: str = Query(..., description=normalize_q_descr),
) -> UnmergedNormalizationService:
    """Return all individual records associated with a normalized concept.

    :param q: Gene search term
    :returns: JSON response with matching normalized record and source metadata
    """
    return query_handler.normalize_unmerged(html.unescape(q))
