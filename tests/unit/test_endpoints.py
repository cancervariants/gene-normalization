"""Perform basic tests of endpoint branches.

We already have tests and data validation to ensure correctness of the underlying
response objects -- here, we're checking for bad branch logic and for basic assurances
that routes integrate correctly with query methods.
"""

from pathlib import Path

import jsonschema
import pytest
import yaml
from fastapi.testclient import TestClient

from gene.main import app
from gene.query import QueryHandler


@pytest.fixture(scope="module")
def api_client(database):
    """Provide test client fixture."""
    app.state.query_handler = QueryHandler(database)
    return TestClient(app)


def test_search(api_client):
    """Test /search endpoint."""
    response = api_client.get("/gene/search?q=braf")
    assert response.status_code == 200
    assert (
        response.json()["source_matches"]["HGNC"]["records"][0]["concept_id"]
        == "hgnc:1097"
    )

    response = api_client.get("/gene/search?q=braf&incl=sdkl")
    assert response.status_code == 422


def test_normalize(api_client):
    """Test /normalize endpoint."""
    response = api_client.get("/gene/normalize?q=braf")
    assert response.status_code == 200
    assert response.json()["gene"]["primaryCoding"] == {
        "id": "hgnc:1097",
        "code": "HGNC:1097",
        "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
    }


def test_normalize_unmerged(api_client):
    """Test /normalize_unmerged endpoint."""
    response = api_client.get("/gene/normalize_unmerged?q=braf")
    assert response.status_code == 200
    assert response.json()["normalized_concept_id"] == "hgnc:1097"


def test_service_info(api_client: TestClient, test_data_dir: Path):
    response = api_client.get("/gene/service-info")
    response.raise_for_status()

    with (test_data_dir / "service_info_openapi.yaml").open() as f:
        spec = yaml.safe_load(f)

    resp_schema = spec["paths"]["/service-info"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]

    resolver = jsonschema.RefResolver.from_schema(spec)
    data = response.json()
    jsonschema.validate(instance=data, schema=resp_schema, resolver=resolver)
