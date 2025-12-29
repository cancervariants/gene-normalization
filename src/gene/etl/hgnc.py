"""Defines the HGNC ETL methods."""

import json
import logging
import re

from gene import PREFIX_LOOKUP
from gene.etl.base import Base
from gene.etl.exceptions import (
    GeneNormalizerEtlError,
)
from gene.schemas import (
    Annotation,
    Chromosome,
    DataLicenseAttributes,
    NamespacePrefix,
    SourceMeta,
    SourceName,
    SymbolStatus,
)

_logger = logging.getLogger(__name__)


class HGNC(Base):
    """ETL the HGNC source into the normalized database."""

    def _transform_data(self) -> None:
        """Transform the HGNC source."""
        _logger.info("Transforming HGNC...")
        with self._data_file.open() as f:
            data = json.load(f)

        records = data["response"]["docs"]

        for r in records:
            gene = {}
            gene["concept_id"] = r["hgnc_id"].lower()
            gene["label_and_type"] = f"{gene['concept_id']}##identity"
            gene["item_type"] = "identity"
            gene["symbol"] = r["symbol"]
            gene["label"] = r["name"]
            gene["src_name"] = SourceName.HGNC.value
            if r["status"]:
                if r["status"] == "Approved":
                    gene["symbol_status"] = SymbolStatus.APPROVED.value
                elif r["status"] == "Entry Withdrawn":
                    gene["symbol_status"] = SymbolStatus.WITHDRAWN.value
            gene["src_name"] = SourceName.HGNC.value

            # store alias, xref, associated_with, prev_symbols, location
            self._get_aliases(r, gene)
            self._get_xrefs_associated_with(r, gene)
            if "prev_symbol" in r:
                self._get_previous_symbols(r, gene)
            if "location" in r:
                self._add_location_annotations(r, gene)
            if "locus_type" in r:
                gene["gene_type"] = r["locus_type"]
                self._load_gene(gene)
        _logger.info("Successfully transformed HGNC.")

    def _get_aliases(self, r: dict, gene: dict) -> None:
        """Store aliases in a gene record.

        :param r: A gene record in the HGNC data file
        :param gene: A transformed gene record
        """
        alias_symbol = []
        enzyme_id = []
        if "alias_symbol" in r:
            alias_symbol = r["alias_symbol"]

        if "enzyme_id" in r:
            enzyme_id = r["enzyme_id"]

        if alias_symbol or enzyme_id:
            gene["aliases"] = list(set(alias_symbol + enzyme_id))

    def _get_previous_symbols(self, r: dict, gene: dict) -> None:
        """Store previous symbols in a gene record.

        :param r: A gene record in the HGNC data file
        :param gene: A transformed gene record
        """
        prev_symbols = r["prev_symbol"]
        if prev_symbols:
            gene["previous_symbols"] = list(set(prev_symbols))

    def _get_xrefs_associated_with(self, r: dict, gene: dict) -> None:
        """Store xrefs and/or associated_with refs in a gene record.

        :param r: A gene record in the HGNC data file
        :param gene: A transformed gene record
        """
        xrefs = []
        associated_with = []
        sources = [
            "entrez_id",
            "ensembl_gene_id",
            "vega_id",
            "ucsc_id",
            "ccds_id",
            "uniprot_ids",
            "pubmed_id",
            "cosmic",
            "omim_id",
            "mirbase",
            "homeodb",
            "snornabase",
            "orphanet",
            "horde_id",
            "merops",
            "imgt",
            "iuphar",
            "kznf_gene_catalog",
            "mamit-trnadb",
            "cd",
            "lncrnadb",
            "ena",
            "pseudogene.org",
            "refseq_accession",
        ]

        for src in sources:
            if src in r:
                if "-" in src:
                    key = src.split("-")[0]
                elif "." in src:
                    key = src.split(".")[0]
                elif "_" in src:
                    key = src.split("_")[0]
                else:
                    key = src

                if key.upper() in NamespacePrefix.__members__:
                    if NamespacePrefix[key.upper()].value in PREFIX_LOOKUP:
                        self._get_xref_associated_with(key, src, r, xrefs)
                    else:
                        self._get_xref_associated_with(key, src, r, associated_with)
                else:
                    _logger.warning("%s not in schemas.py", key)

        if xrefs:
            gene["xrefs"] = xrefs
        if associated_with:
            gene["associated_with"] = associated_with

    def _get_xref_associated_with(
        self, key: str, src: str, r: dict, src_type: dict
    ) -> None:
        """Add an xref or associated_with ref to a gene record.

        :param key: The source's name
        :param src: HGNC's source field
        :param r: A gene record in the HGNC data file
        :param src_type: Either xrefs or associated_with list
        """
        if isinstance(r[src], list):
            for xref in r[src]:
                src_type.append(f"{NamespacePrefix[key.upper()].value}:{xref}")
        else:
            if isinstance(r[src], str) and ":" in r[src]:
                r[src] = r[src].split(":")[-1].strip()
            src_type.append(f"{NamespacePrefix[key.upper()].value}:{r[src]}")

    def _add_location_annotations(self, r: dict, gene: dict) -> None:
        """Add location annotations to ``gene``

        :param r: A gene record in the HGNC data file
        :param gene: A transformed gene record. This may get mutated in place.
        """
        # Get list of a gene's map locations
        if "and" in r["location"]:
            locations = r["location"].split("and")
        else:
            locations = [r["location"]]

        gene["location_annotations"] = []
        for loc in locations:
            loc = loc.strip()  # noqa: PLW2901
            loc = self._set_annotation(loc, gene)  # noqa: PLW2901

            if loc:
                if loc == "mitochondria":
                    gene["location_annotations"].append(Chromosome.MITOCHONDRIA.value)
                else:
                    location = {}
                    self._set_location(loc, location, gene)

        if not gene["location_annotations"]:
            del gene["location_annotations"]

    def _set_annotation(self, loc: str, gene: dict) -> None:
        """Set the annotations attribute if one is provided.
        Return `True` if a location is provided, `False` otherwise.

        :param loc: A gene location
        :param gene: in-progress gene record
        :return: A bool whether or not a gene map location is provided
        """
        annotations = {v.value for v in Annotation.__members__.values()}

        for annotation in annotations:
            if annotation in loc:
                gene["location_annotations"].append(annotation)
                # Check if location is also included
                loc = loc.split(annotation)[0].strip()
                if not loc:
                    return None
        return loc

    def _set_location(self, loc: str, location: dict, gene: dict) -> None:
        """Set a gene's location.

        :param loc: A gene location
        :param location: GA4GH location
        :param gene: A transformed gene record
        """
        arm_match = re.search("[pq]", loc)

        if arm_match:
            # Location gives arm and sub / sub band
            arm_ix = arm_match.start()
            location["chr"] = loc[:arm_ix]

            if "-" in loc:
                # Location gives both start and end
                self._set_cl_interval_range(loc, arm_ix, location)
            else:
                # Location only gives start
                start = loc[arm_ix:]
                location["start"] = start
                location["end"] = start
        else:
            # Only gives chromosome
            gene["location_annotations"].append(loc)

    def _add_meta(self) -> None:
        """Add HGNC metadata.

        :raise GeneNormalizerEtlError: if requisite metadata is unset
        """
        if not self._version:
            err_msg = "Source metadata unavailable -- was data properly acquired before attempting to load DB?"
            raise GeneNormalizerEtlError(err_msg)
        metadata = SourceMeta(
            data_license="CC0",
            data_license_url="https://www.genenames.org/about/license/",
            version=self._version,
            data_url={
                "complete_set_archive": "ftp.ebi.ac.uk/pub/databases/genenames/hgnc/json/hgnc_complete_set.json"
            },
            rdp_url=None,
            data_license_attributes=DataLicenseAttributes(
                non_commercial=False, share_alike=False, attribution=False
            ),
            genome_assemblies=[],
        )
        self._database.add_source_metadata(SourceName.HGNC, metadata)
