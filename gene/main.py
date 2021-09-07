"""Main application for FastAPI"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.openapi.utils import get_openapi
from typing import Optional
from gene import __version__
from gene.query import QueryHandler, InvalidParameterException
from gene.schemas import SearchService, NormalizeService
import html


query_handler = QueryHandler()
app = FastAPI(docs_url='/gene', openapi_url='/gene/openapi.json')


def custom_openapi():
    """Generate custom fields for OpenAPI response"""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="The VICC Gene Normalizer",
        version=__version__,
        openapi_version="3.0.3",
        description="Normalize gene terms.",
        routes=app.routes
    )
    # openapi_schema['info']['license'] = {  # TODO
    #     "name": "name of our license",
    #     "url": "http://www.our-license-tbd.com"
    # }
    openapi_schema['info']['contact'] = {  # TODO
        "name": "Alex H. Wagner",
        "email": "Alex.Wagner@nationwidechildrens.org"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

# endpoint description text
read_query_summary = """Given query, provide matches and match ratings from
                     aggregated sources"""
response_description = "A response to a validly-formed query"
q_descr = "Gene to normalize."
keyed_descr = """Optional. If true, return response as key-value pairs of
              sources to source matches. False by default."""
incl_descr = """Optional. Comma-separated list of source names to include in
             response. Will exclude all other sources. Returns HTTP status code
             422: Unprocessable Entity if both 'incl' and 'excl' parameters
             are given."""
excl_descr = """Optional. Comma-separated list of source names to exclude in
             response. Will include all other sources. Returns HTTP status
             code 422: Unprocessable Entity if both 'incl' and 'excl'
             parameters are given."""
search_description = ("For each source, return strongest-match concepts "
                      "for query string provided by user")


@app.get("/gene/search",
         summary=read_query_summary,
         response_description=response_description,
         response_model=SearchService,
         description=search_description
         )
def search(q: str = Query(..., description=q_descr),  # noqa: D103
           keyed: Optional[bool] = Query(False, description=keyed_descr),
           incl: Optional[str] = Query(None, description=incl_descr),
           excl: Optional[str] = Query(None, description=excl_descr)):
    """Return strongest match concepts to query string provided by user.

    :param str q: gene search term
    :param Optional[bool] keyed: if true, response is structured as key/value
        pair of sources to source match lists.
    :param Optional[str] incl: comma-separated list of sources to include,
        with all others excluded. Raises HTTPException if both `incl` and
        `excl` are given.
    :param Optional[str] excl: comma-separated list of sources exclude, with
        all others included. Raises HTTPException if both `incl` and `excl`
        are given.
    :return: JSON response with matched records and source metadata
    """
    try:
        resp = query_handler.search(html.unescape(q), keyed=keyed,
                                    incl=incl, excl=excl)
    except InvalidParameterException as e:
        raise HTTPException(status_code=422, detail=str(e))

    return resp


normalize_summary = "Given query, provide merged normalized record."
normalize_response_descr = "A response to a validly-formed query."
normalize_descr = "Return merged highest-match concept for query."
normalize_q_desecr = "Gene to normalize."


@app.get("/gene/normalize",
         summary=normalize_summary,
         response_description=normalize_response_descr,
         response_model=NormalizeService,
         description=normalize_descr)
def normalize(q: str = Query(..., description=normalize_q_desecr)):
    """Return strongest match concepts to query string provided by user.

    :param str q: gene search term
    :return: JSON response with normalized gene concept
    """
    try:
        resp = query_handler.normalize(html.unescape(q))
    except InvalidParameterException as e:
        raise HTTPException(status_code=422, detail=str(e))
    return resp
