"""Defines the HGNC ETL methods."""
import json
import logging
import re
from typing import Dict, List

from gene.etl.base import Base, GeneNormalizerEtlError
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
        _logger.info("Transforming HGNC data...")
        with open(self._data_file, "r") as f:  # type: ignore
            data = json.load(f)

        records = data["response"]["docs"]

        for r in records:
            gene = {
                "concept_id": r["hgnc_id"].lower(),
                "symbol": r["symbol"],
                "label": r["name"],
            }
            if r["status"]:
                if r["status"] == "Approved":
                    gene["symbol_status"] = SymbolStatus.APPROVED.value
                elif r["status"] == "Entry Withdrawn":
                    gene["symbol_status"] = SymbolStatus.WITHDRAWN.value

            # store alias, xref, prev_symbols, location
            self._get_aliases(r, gene)
            self._get_xrefs(r, gene)
            if "prev_symbol" in r:
                self._get_previous_symbols(r, gene)
            if "location" in r:
                self._get_location(r, gene)
            if "locus_type" in r:
                gene["gene_type"] = r["locus_type"]
                self._load_gene(gene)
        _logger.info("HGNC data transform complete.")

    def _get_aliases(self, r: Dict, gene: Dict) -> None:
        """Store aliases in a gene record.

        :param r: A gene record in the HGNC data file
        :param gene: A transformed gene record
        """
        alias_symbol = list()
        enzyme_id = list()
        if "alias_symbol" in r:
            alias_symbol = r["alias_symbol"]

        if "enzyme_id" in r:
            enzyme_id = r["enzyme_id"]

        if alias_symbol or enzyme_id:
            gene["aliases"] = list(set(alias_symbol + enzyme_id))

    def _get_previous_symbols(self, r: Dict, gene: Dict) -> None:
        """Store previous symbols in a gene record.

        :param r: A gene record in the HGNC data file
        :param gene: A transformed gene record
        """
        prev_symbols = r["prev_symbol"]
        if prev_symbols:
            gene["previous_symbols"] = list(set(prev_symbols))

    def _get_xrefs(self, record: Dict, gene: Dict) -> None:
        """Store xrefs in a gene record.

        :param record: A gene record in the HGNC data file
        :param gene: A transformed gene record
        """
        xrefs = list()
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
            if src in record:
                if "-" in src:
                    key = src.split("-")[0]
                elif "." in src:
                    key = src.split(".")[0]
                elif "_" in src:
                    key = src.split("_")[0]
                else:
                    key = src

                if key.upper() in NamespacePrefix.__members__:
                    self._get_xref(key, src, record, xrefs)
                else:
                    _logger.warning(f"{key} not in schemas.py")

        if xrefs:
            gene["xrefs"] = xrefs

    def _get_xref(self, key: str, src: str, r: Dict, xrefs: List[str]) -> None:
        """Add an xref to a gene record.

        :param key: The source's name
        :param src: HGNC's source field
        :param r: A gene record in the HGNC data file
        :param xrefs: xrefs list
        """
        if isinstance(r[src], list):
            for xref in r[src]:
                xrefs.append(f"{NamespacePrefix[key.upper()].value}:{xref}")
        else:
            if isinstance(r[src], str) and ":" in r[src]:
                r[src] = r[src].split(":")[-1].strip()
            xrefs.append(f"{NamespacePrefix[key.upper()].value}" f":{r[src]}")

    def _get_location(self, r: Dict, gene: Dict) -> None:
        """Store GA4GH VRS ChromosomeLocation in a gene record.
        https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#chromosomelocation

        :param r: A gene record in the HGNC data file
        :param gene: A transformed gene record
        """
        # Get list of a gene's map locations
        if "and" in r["location"]:
            locations = r["location"].split("and")
        else:
            locations = [r["location"]]

        location_list = list()
        gene["location_annotations"] = list()
        for loc in locations:
            loc = loc.strip()
            loc = self._set_annotation(loc, gene)

            if loc:
                if loc == "mitochondria":
                    gene["location_annotations"].append(Chromosome.MITOCHONDRIA.value)
                else:
                    location = dict()
                    self._set_location(loc, location, gene)
                    # chr_location = self._get_chromosome_location(location, gene)
                    # if chr_location:
                    #     location_list.append(chr_location)

        if location_list:
            gene["locations"] = location_list
        if not gene["location_annotations"]:
            del gene["location_annotations"]

    _annotation_types = {v.value for v in Annotation.__members__.values()}

    def _set_annotation(self, loc: str, gene: Dict) -> None:
        """Set the annotations attribute if one is provided.
        Return `True` if a location is provided, `False` otherwise.

        :param loc: A gene location
        :param gene: in-progress gene record
        :return: A bool whether or not a gene map location is provided
        """
        for annotation in self._annotation_types:
            if annotation in loc:
                gene["location_annotations"].append(annotation)
                # Check if location is also included
                loc = loc.split(annotation)[0].strip()
                if not loc:
                    return None
        return loc

    def _set_location(self, loc: str, location: Dict, gene: Dict) -> None:
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
            raise GeneNormalizerEtlError(
                "Source metadata unavailable -- was data properly acquired before attempting to load DB?"
            )
        metadata = SourceMeta(
            data_license="CC0",
            data_license_url="https://www.genenames.org/about/license/",
            version=self._version,
            data_url={
                "complete_set_archive": "ftp.ebi.ac.uk/pub/databases/genenames/hgnc/json/hgnc_complete_set.json"
            },
            rdp_url=None,
            data_license_attributes=DataLicenseAttributes(
                non_commercial=False,
                share_alike=False,
                attribution=False,
            ),
            genome_assemblies=[],
        )
        self._database.add_source_metadata(SourceName.HGNC, metadata)
