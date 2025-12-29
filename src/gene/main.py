"""Main application for FastAPI"""

import html
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from enum import Enum
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request

from gene import __version__
from gene.config import get_config
from gene.database import create_db
from gene.query import InvalidParameterException, QueryHandler
from gene.schemas import (
    NormalizeService,
    SearchService,
    ServiceInfo,
    ServiceOrganization,
    ServiceType,
    UnmergedNormalizationService,
)
from gene.utils import initialize_logs


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Perform operations that interact with the lifespan of the FastAPI instance.

    See https://fastapi.tiangolo.com/advanced/events/#lifespan.

    :param app: FastAPI instance
    """
    log_level = logging.DEBUG if get_config().debug else logging.INFO
    initialize_logs(log_level=log_level)
    db = create_db()
    app.state.query_handler = QueryHandler(db)

    yield


class _Tag(str, Enum):
    """Define tag names for endpoints."""

    META = "Meta"
    QUERY = "Query"


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
    lifespan=lifespan,
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
    "For each source, return strongest-match concepts for query string provided by user"
)


@app.get(
    "/gene/search",
    summary=read_query_summary,
    response_description=response_description,
    description=search_description,
    tags=[_Tag.QUERY],
)
def search(
    request: Request,
    q: Annotated[str, Query(..., description=q_descr)],
    incl: Annotated[str | None, Query(..., description=incl_descr)] = None,
    excl: Annotated[str | None, Query(..., description=excl_descr)] = None,
) -> SearchService:
    """Return strongest match concepts to query string provided by user."""
    try:
        resp = request.app.state.query_handler.search(
            html.unescape(q), incl=incl, excl=excl
        )
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
    response_model_exclude_none=True,
    description=normalize_descr,
    tags=[_Tag.QUERY],
)
def normalize(
    request: Request, q: Annotated[str, Query(..., description=normalize_q_descr)]
) -> NormalizeService:
    """Return strongest match concepts to query string provided by user."""
    return request.app.state.query_handler.normalize(html.unescape(q))


unmerged_matches_summary = (
    "Given query, provide source records corresponding to normalized concept."
)
unmerged_response_descr = (
    "Response containing source records contained within normalized concept."
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
    description=unmerged_normalize_description,
    tags=["Query"],
)
def normalize_unmerged(
    request: Request,
    q: Annotated[str, Query(..., description=normalize_q_descr)],
) -> UnmergedNormalizationService:
    """Return all individual records associated with a normalized concept."""
    return request.app.state.query_handler.normalize_unmerged(html.unescape(q))


@app.get(
    "/gene/service-info",
    summary="Get basic service information",
    description="Retrieve service metadata, such as versioning and contact info. Structured in conformance with the [GA4GH service info API specification](https://www.ga4gh.org/product/service-info/)",
    tags=[_Tag.META],
)
def service_info() -> ServiceInfo:
    """Provide service info per GA4GH Service Info spec"""
    return ServiceInfo(
        organization=ServiceOrganization(),
        type=ServiceType(),
        environment=get_config().env,
    )
