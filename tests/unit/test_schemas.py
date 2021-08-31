"""Module to test validators in the schemas module."""
import pytest
import pydantic
from gene.schemas import Gene
from ga4gh.vrsatile.pydantic.vrs_model import ChromosomeLocation, \
    SequenceLocation, Gene as GeneValueObject, CytobandInterval, \
    SequenceInterval, Number


@pytest.fixture(scope='module')
def cytoband_interval():
    """Create a valid cytoband interval test fixture."""
    return CytobandInterval(
        start='q34',
        end='q34'
    )


@pytest.fixture(scope='module')
def chromosome_location(cytoband_interval):
    """Create a valid chromosome location test fixture."""
    return ChromosomeLocation(
        species_id='taxonomy:9606',
        chr='7',
        interval=cytoband_interval
    )


@pytest.fixture(scope='module')
def sequence_interval():
    """Create a valid simple interval test fixture."""
    return SequenceInterval(
        start=Number(value=140719327),
        end=Number(value=140924929)
    )


@pytest.fixture(scope='module')
def sequence_location(sequence_interval):
    """Create a valid sequence location test fixture."""
    return SequenceLocation(
        sequence_id='ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul',
        interval=sequence_interval
    )


@pytest.fixture(scope='module')
def gene():
    """Create a valid gene test fixture."""
    return Gene(
        concept_id='hgnc:1097',
        symbol='BRAF'
    )


def test_gene(gene, chromosome_location, sequence_location):
    """Test that validators for gene work correctly."""
    assert gene
    assert Gene(
        concept_id='ensembl:1',
        symbol='GENE',
        locations=[chromosome_location, sequence_location]
    )
    assert Gene(
        concept_id='ensembl:1',
        symbol='GENE',
        locations=[sequence_location]
    )
    assert Gene(
        concept_id='ensembl:1',
        symbol='GENE',
        locations=[sequence_location]
    )

    # id not a valid curie
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Gene(
            concept_id='hgnc1096',
            symbol='BRAF'
        )

    # symbol not a str
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Gene(
            concept_id='hgnc:1096',
            symbol=1
        )

    # strand not -/+
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Gene(
            concept_id='hgnc:1096',
            symbol='BRAF',
            strand='positive'
        )

    # xrefs not a valid curie
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Gene(
            concept_id='hgnc:1096',
            symbol='BRAF',
            xrefs=['hgnc', 'hgnc:1']
        )

    # associated_with not a valid curie
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Gene(
            concept_id='hgnc:1096',
            symbol='BRAF',
            associated_with=['hgnc', 'hgnc:1']
        )

    # symbol status invalid
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Gene(
            concept_id='hgnc:1096',
            symbol='BRAF',
            symbol_status='nothing'
        )

    # locations not a sequence or chromosome location
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Gene(
            concept_id='hgnc:1096',
            symbol='BRAF',
            locations=[GeneValueObject(id='hgnc:1')]
        )

    # location not a list
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Gene(
            concept_id='hgnc:1096',
            symbol='BRAF',
            locations=chromosome_location
        )
