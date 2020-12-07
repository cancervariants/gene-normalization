"""Main application for FastAPI"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.openapi.utils import get_openapi
from typing import Optional
from gene.query import Normalizer, InvalidParameterException
import html


normalizer = Normalizer()
app = FastAPI(docs_url='/')


def custom_openapi():
    """Generate custom fields for OpenAPI response"""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="The VICC Gene Normalizer",
        version="0.1.0",
        openapi_version="3.0.3",
        description="Normalize gene terms.",  # TODO
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


@app.get("/search",
         summary=read_query_summary,
         operation_id="getQueryResponse",
         response_description=response_description,
         )
def read_query(q: str = Query(..., description=q_descr),  # noqa: D103
               keyed: Optional[bool] = Query(False, description=keyed_descr),
               incl: Optional[str] = Query('', description=incl_descr),
               excl: Optional[str] = Query('', description=excl_descr)):
    """Return strongest match concepts to query string provided by user.

    Args:
        q: gene search term
        keyed: if true, response is structured as key/value pair of
            sources to source match lists.
        incl: comma-separated list of sources to include, with all others
            excluded. Raises HTTPException if both `incl` and `excl` are given.
        excl: comma-separated list of sources exclude, with all others
            included. Raises HTTPException if both `incl` and `excl` are given.

    Returns:
        JSON response with matched records and source metadata
    """
    try:
        resp = Normalizer.normalize(html.unescape(q), keyed=keyed, incl=incl,
                                    excl=excl)
    except InvalidParameterException as e:
        raise HTTPException(status_code=422, detail=str(e))

    return resp
