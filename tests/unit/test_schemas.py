"""Module to test validators in the schemas module."""

import pydantic
import pytest
from ga4gh.vrs import models

from gene.schemas import Gene


@pytest.fixture(scope="module")
def sequence_location():
    """Create a valid sequence location test fixture."""
    return models.SequenceLocation(
        sequenceReference=models.SequenceReference(
            refgetAccession="SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"
        ),
        start=140719327,
        end=140924929,
    )


@pytest.fixture(scope="module")
def gene():
    """Create a valid gene test fixture."""
    return Gene(match_type=100, concept_id="hgnc:1097", symbol="BRAF")


def test_gene(gene, sequence_location):
    """Test that validators for gene work correctly."""
    assert gene
    assert Gene(
        match_type=100,
        concept_id="ensembl:1",
        symbol="GENE",
        # locations=[chromosome_location, sequence_location]
        locations=[sequence_location],
    )
    assert Gene(
        match_type=100,
        concept_id="ensembl:1",
        symbol="GENE",
        locations=[sequence_location],
    )
    assert Gene(
        match_type=100,
        concept_id="ensembl:1",
        symbol="GENE",
        locations=[sequence_location],
    )

    # id not a valid curie
    with pytest.raises(pydantic.ValidationError):
        Gene(match_type=100, concept_id="hgnc1096", symbol="BRAF")

    # symbol not a str
    with pytest.raises(pydantic.ValidationError):
        Gene(match_type=100, concept_id="hgnc:1096", symbol=1)

    # strand not -/+
    with pytest.raises(pydantic.ValidationError):
        Gene(match_type=100, concept_id="hgnc:1096", symbol="BRAF", strand="positive")

    # xrefs not a valid curie
    with pytest.raises(pydantic.ValidationError):
        Gene(
            match_type=100,
            concept_id="hgnc:1096",
            symbol="BRAF",
            xrefs=["hgnc", "hgnc:1"],
        )

    # associated_with not a valid curie
    with pytest.raises(pydantic.ValidationError):
        Gene(
            match_type=100,
            concept_id="hgnc:1096",
            symbol="BRAF",
            associated_with=["hgnc", "hgnc:1"],
        )

    # symbol status invalid
    with pytest.raises(pydantic.ValidationError):
        Gene(
            match_type=100,
            concept_id="hgnc:1096",
            symbol="BRAF",
            symbol_status="nothing",
        )

    # locations not a sequence or chromosome location
    with pytest.raises(pydantic.ValidationError):
        Gene(
            match_type=100,
            concept_id="hgnc:1096",
            symbol="BRAF",
            locations=["GRCh38:chr1"],
        )

    # location not a list
    with pytest.raises(pydantic.ValidationError):
        Gene(
            match_type=100,
            concept_id="hgnc:1096",
            symbol="BRAF",
            locations=sequence_location,
        )
