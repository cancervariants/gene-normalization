"""Module to test validators in the schemas module."""
import pytest
import pydantic
from gene.schemas import ChromosomeLocation, SequenceLocation, Gene, \
    GeneDescriptor, CytobandInterval, SimpleInterval, GeneValueObject, \
    Extension


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
def simple_interval():
    """Create a valid simple interval test fixture."""
    return SimpleInterval(
        start=140719327,
        end=140924929
    )


@pytest.fixture(scope='module')
def sequence_location(simple_interval):
    """Create a valid sequence location test fixture."""
    return SequenceLocation(
        sequence_id='ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul',
        interval=simple_interval
    )


@pytest.fixture(scope='module')
def gene_value_object():
    """Create a valid gene value object test fixture."""
    return GeneValueObject(
        id='hgnc:1097'
    )


@pytest.fixture(scope='module')
def gene_descriptor(gene_value_object):
    """Create a valid gene descriptor test fixture."""
    return GeneDescriptor(
        id='normalize.gene:BRAF',
        value=gene_value_object
    )


@pytest.fixture(scope='module')
def extension():
    """Create a valid extension test fixture."""
    return Extension(
        name="associated_with",
        value=[
            "ucsc:uc003vwc.5",
            "pubmed:1565476",
            "omim:164757"
        ]
    )


@pytest.fixture(scope='module')
def gene():
    """Create a valid gene test fixture."""
    return Gene(
        concept_id='hgnc:1097',
        symbol='BRAF'
    )


def test_chromosome_location(chromosome_location, cytoband_interval):
    """Test that validators for Chromosome Location work correctly."""
    assert chromosome_location

    # species_id not a valid curie
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        ChromosomeLocation(
            species_id='taxonomy9606',
            chr='7',
            interval=cytoband_interval
        )

    # chromosome not a str
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        ChromosomeLocation(
            species_id='taxonomy:9606',
            chr=7,
            interval=cytoband_interval
        )

    # cytoband interval does not match regex pattern
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        ChromosomeLocation(
            species_id='taxonomy9:606',
            chr='7',
            interval=CytobandInterval(
                end='end',
                start='q34'
            )
        )

    # cytoband interval does not match regex pattern
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        ChromosomeLocation(
            species_id='taxonomy9:606',
            chr='7',
            interval=CytobandInterval(
                end=5,
                start=2
            )
        )

    with pytest.raises(pydantic.error_wrappers.ValidationError):
        ChromosomeLocation(
            species_ud='taxonomy:4232', chr='5',
            interval=CytobandInterval(
                start=17,
                end=18
            )
        )


def test_sequence_location(sequence_location, simple_interval):
    """Test that validators for Sequence Location work correctly."""
    assert sequence_location

    # sequence_id is not a valid curie
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        SequenceLocation(
            sequence_id='ga4ghSQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul',
            interval=simple_interval
        )

    # Simple interval start/end not int
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        SequenceLocation(
            sequence_id='ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul',
            interval=SimpleInterval(
                start='140719327',
                end='140924929'
            )
        )

    with pytest.raises(pydantic.error_wrappers.ValidationError):
        SequenceLocation(
            sequence_id='ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul',
            interval=SimpleInterval(
                start='s',
                end='q'
            )
        )

    with pytest.raises(pydantic.error_wrappers.ValidationError):
        SequenceLocation(
            sequence_id='ncbiNC_000001.11',
            interval=SimpleInterval(
                start='s',
                end='p'
            )
        )


def test_gene_value_object(gene_value_object):
    """Test that validators for gene value object work correctly."""
    assert gene_value_object

    with pytest.raises(pydantic.error_wrappers.ValidationError):
        GeneValueObject(
            id='hgnc1097'
        )


def test_extension(extension):
    """Test that validators for extension work correctly."""
    assert extension

    assert Extension(name='strand', value='-')

    # name is not a str
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Extension(name=3, value=['ucsc:uc003vwc.5'])


def test_gene_descriptor(gene_descriptor):
    """Test that validators for gene descriptor work correctly."""
    assert gene_descriptor
    assert GeneDescriptor(
        id='test:g1',
        value=GeneValueObject(id='hgnc:1497', type='Gene'),
        label='G1',
        xrefs=['ncbi:g1'],
        alternate_labels=['gen1']
    )

    with pytest.raises(pydantic.error_wrappers.ValidationError):
        GeneDescriptor(
            id=1,
            value=GeneValueObject(id='hgnc1497', type='Gene'),
            label='G1',
            xrefs=['ncbi:g1'],
            alternate_labels=['gen1']
        )

    # No value or value_id
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        GeneDescriptor(
            id='normalize.gene:BRAF'
        )

    # id not a valid curie
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        GeneDescriptor(
            id='normalize.geneBRAF',
            value_id='hgnc:1'
        )

    # value_id not a valid curie
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        GeneDescriptor(
            id='normalize.gene:BRAF',
            value_id='value_id'
        )

    # value not a gene value object
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        GeneDescriptor(
            id='normalize.gene:BRAF',
            value=['value']
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
