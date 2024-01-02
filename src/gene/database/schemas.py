"""Provide schemas for database storage, as well as associated helper methods."""
from typing import List, Optional

from ga4gh.core._internal.models import Mapping
from ga4gh.vrs._internal.models import SequenceLocation, SequenceReference
from pydantic import BaseModel, ConfigDict, StrictInt, StrictStr, constr

from gene.schemas import (
    ApprovedNameExtension,
    Gene,
    GeneTypeExtension,
    GeneTypeExtensionName,
    LocationAnnotationsExtension,
    PreviousSymbolsExtension,
    SequenceLocationExtension,
    SequenceLocationExtensionName,
    Strand,
    SymbolStatus,
    SymbolStatusExtension,
)


class StoredSequenceLocation(BaseModel):
    """Flattened SequenceLocation object for easier storage."""

    name: SequenceLocationExtensionName
    start: StrictInt
    end: StrictInt
    sequence_id: constr(pattern=r"^ga4gh:SQ.[0-9A-Za-z_\-]{32}$")


# class GeneChromosomeLocation(BaseModel):
#     """Chromosome Location model when storing in DynamDB."""

#     type: Literal["ChromosomeLocation"] = "ChromosomeLocation"
#     species_id: Literal["taxonomy:9606"] = "taxonomy:9606"
#     chr: StrictStr
#     start: StrictStr
#     end: StrictStr


class StoredGeneType(BaseModel):
    """Flattened gene type extension object for easier storage."""

    name: GeneTypeExtensionName
    value: StrictStr


class StoredGene(BaseModel):
    """Flatted gene object for easier storage.

    The full GA4GH core Gene object is quite verbose and includes a lot of redundant
    information. This is fine for machine-readable output, but unnecessary/unwieldy
    when storing in a DB. This class represents the minimum information in a flatter
    structure, and should be expanded out to a full gene object by database
    implementation classes.
    """

    concept_id: StrictStr
    label: Optional[StrictStr] = None  # symbol
    aliases: Optional[List[str]] = None
    xrefs: Optional[List[str]] = None

    symbol_status: Optional[SymbolStatus] = None
    approved_name: Optional[StrictStr] = None  # full name
    previous_symbols: Optional[List[StrictStr]] = None
    strand: Optional[Strand] = None
    location_annotations: Optional[List[StrictStr]] = None
    locations: Optional[List[StoredSequenceLocation]] = None
    gene_types: Optional[List[StoredGeneType]] = None

    normalized_id: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


def convert_to_vrs_location(location: StoredSequenceLocation) -> SequenceLocation:
    """Convert collapsed DB sequence location object to valid VRS SequenceLocation.

    :param location: stored location object
    :return: Corresponding VRS location
    """
    refget_ac = location.sequence_id.split("ga4gh:")[-1]
    return SequenceLocation(
        sequenceReference=SequenceReference(refgetAccession=refget_ac),
        start=location.start,
        end=location.end,
    )


def convert_to_gene(stored_gene: StoredGene) -> Gene:
    """Convert gene from stored format to GA4GH core Gene object.

    :param stored_gene: gene record, as retrieved from database
    :return: equivalent Gene object
    """
    mappings = []
    if stored_gene.xrefs:
        for xref in stored_gene.xrefs:
            split = xref.split(":", maxsplit=1)
            mappings.append(
                Mapping(
                    relation="relatedMatch",
                    coding={"system": split[0], "code": split[1]},
                )
            )

    extensions = []
    if stored_gene.symbol_status:
        extensions.append(SymbolStatusExtension(value=stored_gene.symbol_status))
    if stored_gene.approved_name:
        extensions.append(ApprovedNameExtension(value=stored_gene.approved_name))
    if stored_gene.previous_symbols:
        extensions.append(PreviousSymbolsExtension(value=stored_gene.previous_symbols))
    if stored_gene.strand:
        extensions.append(PreviousSymbolsExtension(value=stored_gene.strand))
    if stored_gene.location_annotations:
        extensions += LocationAnnotationsExtension(
            value=stored_gene.location_annotations
        )
    if stored_gene.locations:
        locations = [convert_to_vrs_location(loc) for loc in stored_gene.locations]
        extensions += SequenceLocationExtension(value=locations)
    if stored_gene.gene_types:
        gene_types = [
            GeneTypeExtension(**gt.model_dump()) for gt in stored_gene.gene_types
        ]
        extensions += gene_types

    gene = Gene(
        id=stored_gene.concept_id,
        label=stored_gene.label,
        aliases=stored_gene.aliases,
        extensions=extensions,
        mappings=mappings,
    )
    return gene
