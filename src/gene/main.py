"""Main application for FastAPI"""

import html
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from enum import Enum
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request

from gene import __version__
from gene.database.database import (
    AWS_ENV_VAR_NAME,
    VALID_AWS_ENV_NAMES,
    AwsEnvName,
    create_db,
)
from gene.logging import initialize_logs
from gene.query import InvalidParameterException, QueryHandler
from gene.schemas import (
    NormalizeService,
    SearchService,
    ServiceInfo,
    ServiceOrganization,
    ServiceType,
    UnmergedNormalizationService,
)


class _Tag(str, Enum):
    """Define tag names for endpoints."""

    QUERY = "Query"
    META = "Meta"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Perform operations that interact with the lifespan of the FastAPI instance.
    See https://fastapi.tiangolo.com/advanced/events/#lifespan.

    :param app: FastAPI instance
    """
    initialize_logs()

    db = create_db()
    app.state.query_handler = QueryHandler(db)
    yield


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
    description=search_description,
    tags=[_Tag.QUERY],
)
def search(
    request: Request,
    q: Annotated[str, Query(..., description=q_descr)],
    incl: Annotated[str | None, Query(description=incl_descr)] = None,
    excl: Annotated[str | None, Query(description=excl_descr)] = None,
) -> SearchService:
    """Return strongest match concepts to query string provided by user.

    :param request: the HTTP request context, supplied by FastAPI, used to get
        query response class
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
    request: Request,
    q: Annotated[str, Query(..., description=normalize_q_descr)],
) -> NormalizeService:
    """Return strongest match concepts to query string provided by user.

    :param request: the HTTP request context, supplied by FastAPI, used to get
        query response class
    :param str q: gene search term
    :return: JSON response with normalized gene concept
    """
    return request.app.state.query_handler.normalize(html.unescape(q))


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
    description=unmerged_normalize_description,
    tags=[_Tag.QUERY],
)
def normalize_unmerged(
    request: Request,
    q: Annotated[str, Query(..., description=normalize_q_descr)],
) -> UnmergedNormalizationService:
    """Return all individual records associated with a normalized concept.

    :param request: the HTTP request context, supplied by FastAPI, used to get
        query response class
    :param q: Gene search term
    :returns: JSON response with matching normalized record and source metadata
    """
    return request.app.state.query_handler.normalize_unmerged(html.unescape(q))


@app.get(
    "/gene/service_info",
    summary="Get basic service information",
    description="Retrieve service metadata, such as versioning and contact info. Structured in conformance with the [GA4GH service info API specification](https://www.ga4gh.org/product/service-info/)",
    tags=[_Tag.META],
)
def service_info() -> ServiceInfo:
    """Provide service info per GA4GH Service Info spec

    :return: conformant service info description
    """
    if not os.environ.get(AWS_ENV_VAR_NAME):
        env = None
    else:
        raw_env_var = os.environ[AWS_ENV_VAR_NAME]
        if raw_env_var not in VALID_AWS_ENV_NAMES:
            env = None
        else:
            env = AwsEnvName(raw_env_var)

    return ServiceInfo(
        organization=ServiceOrganization(), type=ServiceType(), environment=env
    )
