"""Main application for FastAPI"""
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Optional


app = FastAPI()


def custom_openapi():
    """Generate custom fields for OpenAPI response"""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Gene Normalizer",
        version="0.1.0",
        description="TODO Description here",  # TODO
        routes=app.routes
    )
    # openapi_schema['info']['license'] = {  # TODO
    #     "name": "name of our license",
    #     "url": "link to it"
    # }
    # openapi_schema['info']['contact'] = {  # TODO
    #     "name": "alex wagner",
    #     "email": "his email"
    # }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/search",
         summary="Given query, provide matches and match ratings from "
                 "aggregated sources",
         operation_id="getQueryResponse",
         response_description="A response to a validly-formed query",  # TODO
         )
def read_query(q: str,  # noqa: D103
               keyed: Optional[bool] = False,
               incl: Optional[str] = '',
               excl: Optional[str] = ''):
    return {"TODO"}
