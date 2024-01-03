"""Defines the Ensembl ETL methods."""
import logging
import re
from typing import Dict, Optional

import gffutils
from gffutils.feature import Feature

from gene.etl.base import Base, GeneNormalizerEtlError
from gene.schemas import (
    DataLicenseAttributes,
    NamespacePrefix,
    SourceMeta,
    Strand,
)

_logger = logging.getLogger(__name__)


class Ensembl(Base):
    """ETL the Ensembl source into the normalized database."""

    def _extract_data(self, use_existing: bool) -> None:
        """Acquire source data.

        This method is responsible for initializing an instance of a data handler and,
        in most cases, setting ``self._data_file`` and ``self._version``.

        :param use_existing: if True, don't try to fetch latest source data
        """
        _logger.info("Gathering Ensembl data...")
        self._data_file, raw_version = self._data_source.get_latest(
            from_local=use_existing
        )
        match = re.match(r"(GRCh\d+)_(\d+)", raw_version)
        self._assembly = match.groups()[0]
        self._version = match.groups()[1]
        _logger.info(f"Acquired data for Ensembl: {self._data_file}")

    def _transform_data(self) -> None:
        """Transform the Ensembl source."""
        _logger.info("Transforming Ensembl data...")
        db = gffutils.create_db(
            str(self._data_file),
            dbfn=":memory:",
            force=True,
            merge_strategy="create_unique",
            keep_order=True,
        )

        # Get accession numbers
        accession_numbers = dict()
        for item in db.features_of_type("scaffold"):
            accession_numbers[item[0]] = item[8]["Alias"][-1]
        for item in db.features_of_type("chromosome"):
            accession_numbers[item[0]] = item[8]["Alias"][-1]

        for f in db.all_features():
            if f.attributes.get("ID"):
                f_id = f.attributes.get("ID")[0].split(":")[0]
                if f_id == "gene":
                    gene = self._add_gene(f, accession_numbers)
                    if gene:
                        self._load_gene(gene)
        _logger.info("Ensembl data transform complete.")

    def _add_gene(self, f: Feature, accession_numbers: Dict) -> Dict:
        """Create a transformed gene record.

        :param f: A gene from the data
        :param accession_numbers: Accession numbers for each chromosome and scaffold
        :return: A gene dictionary containing data if the ID attribute exists.
        """
        gene_params = dict()
        if f.strand == "-":
            gene_params["strand"] = Strand.REVERSE.value
        elif f.strand == "+":
            gene_params["strand"] = Strand.FORWARD.value

        self._add_attributes(f, gene_params)
        location = self._build_sequence_location(
            accession_numbers[f.seqid], f, gene_params["concept_id"]
        )
        if location:
            gene_params["locations"] = [location]

        gene_params["label_and_type"] = f"{gene_params['concept_id'].lower()}##identity"
        gene_params["item_type"] = "identity"

        return gene_params

    def _add_attributes(self, f: Feature, gene: Dict) -> None:
        """Add concept_id, symbol, and xrefs to a gene record.

        :param f: A gene from the data
        :param gene: A transformed gene record
        """
        attributes_map = {
            "ID": "concept_id",
            "Name": "symbol",
            "description": "xrefs",
            "biotype": "gene_type",
        }

        for key, value in f.attributes.items():
            if key not in attributes_map:
                continue

            if key == "ID" and value[0].startswith("gene"):
                gene[
                    "concept_id"
                ] = f"{NamespacePrefix.ENSEMBL.value}:{value[0].split(':')[1]}"
            elif key == "description":
                pattern = "^(.*) \\[Source:.*;Acc:(.*):(.*)\\]$"
                matches = re.findall(pattern, value[0])
                if matches:
                    gene["label"] = matches[0][0]
                    gene["xrefs"] = [self._get_xref(matches[0][1], matches[0][2])]
            else:
                gene[attributes_map[key]] = value
            # key = attribute[0]
            #
            # if key in attributes_map.keys():
            #     val = attribute[1]
            #
            #     if len(val) == 1:
            #         val = val[0]
            #         if key == "ID":
            #             if val.startswith("gene"):
            #                 val = (
            #                     f"{NamespacePrefix.ENSEMBL.value}:"
            #                     f"{val.split(':')[1]}"
            #                 )
            #
            #     if key == "description":
            #         gene["label"] = val.split("[")[0].strip()
            #         if "Source:" in val:
            #             src_name = (
            #                 val.split("[")[-1]
            #                 .split("Source:")[-1]
            #                 .split("Acc")[0]
            #                 .split(";")[0]
            #             )
            #             src_id = val.split("Acc:")[-1].split("]")[0]
            #             if ":" in src_id:
            #                 src_id = src_id.split(":")[-1]
            #             gene["xrefs"] = self._get_xref(src_name, src_id)
            #         continue
            #
            #     gene[attributes_map[key]] = val

    def _get_xref(self, src_name: str, src_id: str) -> Optional[str]:
        """Get xref.

        :param src_name: Source name
        :param src_id: The source's accession number
        :return: xref, if successfully parsed
        """
        for prefix, constrained_prefix in (
            ("HGNC", NamespacePrefix.HGNC),
            ("NCBI", NamespacePrefix.NCBI),
            ("UniProt", NamespacePrefix.UNIPROT),
            ("miRBase", NamespacePrefix.MIRBASE),
            ("RFAM", NamespacePrefix.RFAM),
        ):
            if src_name.startswith(prefix):
                return f"{constrained_prefix.value}:{src_id}"
        _logger.warning("Unrecognized source name: %:%", src_name, src_id)
        return None

    def _add_meta(self) -> None:
        """Add Ensembl metadata.

        :raise GeneNormalizerEtlError: if requisite metadata is unset
        """
        if not self._version or not self._assembly:
            raise GeneNormalizerEtlError(
                "Source metadata unavailable -- was data properly acquired before attempting to load DB?"
            )
        metadata = SourceMeta(
            data_license="custom",
            data_license_url="https://useast.ensembl.org/info/about"
            "/legal/disclaimer.html",
            version=self._version,
            data_url={
                "genome_annotations": f"ftp://ftp.ensembl.org/pub/release-{self._version}/gff3/homo_sapiens/Homo_sapiens.{self._assembly}.{self._version}.gff3.gz"
            },
            rdp_url=None,
            data_license_attributes=DataLicenseAttributes(
                non_commercial=False,
                share_alike=False,
                attribution=False,
            ),
            genome_assemblies=[self._assembly],
        )

        self._database.add_source_metadata(self._src_name, metadata)
