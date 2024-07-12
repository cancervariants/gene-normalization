"""Perform basic tests of endpoint branches.

We already have tests and data validation to ensure correctness of the underlying
response objects -- here, we're checking for bad branch logic and for basic assurances
that routes integrate correctly with query methods.
"""

import pytest
from fastapi.testclient import TestClient

from gene.main import app


@pytest.fixture(scope="module")
def api_client():
    """Provide test client fixture."""
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
    assert response.json()["normalized_id"] == "hgnc:1097"


def test_normalize_unmerged(api_client):
    """Test /normalize_unmerged endpoint."""
    response = api_client.get("/gene/normalize_unmerged?q=braf")
    assert response.status_code == 200
    assert response.json()["normalized_concept_id"] == "hgnc:1097"
