"""Test FastAPI endpoint function."""

import re
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from gene.main import app


@pytest.fixture(scope="module")
def api_client():
    """Provide test API client"""
    return TestClient(app)


def test_service_info(api_client: TestClient):
    """Test /service_info endpoint"""
    response = api_client.get("/gene/service_info")
    assert response.status_code == 200
    expected_version_pattern = r"\d\.\d\."
    response_json = response.json()
    assert response_json["id"] == "org.genomicmedlab.gene-normalizer"
    assert response_json["name"] == "Gene Normalizer"
    assert response_json["type"]["group"] == "org.genomicmedlab"
    assert response_json["type"]["artifact"] == "Gene Normalizer API"
    assert re.match(expected_version_pattern, response_json["type"]["version"])
    assert (
        response_json["description"]
        == "Tools for resolving ambiguous gene symbols to richly-annotated concepts"
    )
    assert response_json["organization"] == {
        "name": "Genomic Medicine Lab at Nationwide Children's Hospital",
        "url": "https://www.nationwidechildrens.org/specialties/institute-for-genomic-medicine/research-labs/wagner-lab",
    }
    assert response_json["contactUrl"] == "Alex.Wagner@nationwidechildrens.org"
    assert (
        response_json["documentationUrl"] == "https://gene-normalizer.readthedocs.io/"
    )
    assert datetime.fromisoformat(response_json["createdAt"])
    assert re.match(expected_version_pattern, response_json["version"])
