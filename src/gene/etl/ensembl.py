"""Defines the Ensembl ETL methods."""

import logging
import re

import gffutils
from gffutils.feature import Feature

from gene.etl.base import Base
from gene.etl.exceptions import (
    GeneNormalizerEtlError,
)
from gene.schemas import (
    DataLicenseAttributes,
    NamespacePrefix,
    SourceMeta,
    SourceName,
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
        self._data_file, raw_version = self._data_source.get_latest(
            from_local=use_existing
        )
        match = re.match(r"(GRCh\d+)_(\d+)", raw_version)
        self._assembly = match.groups()[0]
        self._version = match.groups()[1]

    def _transform_data(self) -> None:
        """Transform the Ensembl source."""
        _logger.info("Transforming Ensembl...")
        db = gffutils.create_db(
            str(self._data_file),
            dbfn=":memory:",
            force=True,
            merge_strategy="create_unique",
            keep_order=True,
        )

        # Get accession numbers
        accession_numbers = {}
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
        _logger.info("Successfully transformed Ensembl.")

    def _add_gene(self, f: Feature, accession_numbers: dict) -> dict:
        """Create a transformed gene record.

        :param f: A gene from the data
        :param accession_numbers: Accession numbers for each chromosome and scaffold
        :return: A gene dictionary containing data if the ID attribute exists.
        """
        gene = {}
        if f.strand == "-":
            gene["strand"] = Strand.REVERSE.value
        elif f.strand == "+":
            gene["strand"] = Strand.FORWARD.value
        gene["src_name"] = SourceName.ENSEMBL.value

        self._add_attributes(f, gene)
        location = self._add_location(f, gene, accession_numbers)
        if location:
            gene["locations"] = [location]

        gene["label_and_type"] = f"{gene['concept_id'].lower()}##identity"
        gene["item_type"] = "identity"

        return gene

    def _add_attributes(self, f: Feature, gene: dict) -> None:
        """Add concept_id, symbol, xrefs, and associated_with to a gene record.

        :param f: A gene from the data
        :param gene: A transformed gene record
        """
        attributes = {
            "ID": "concept_id",
            "Name": "symbol",
            "description": "xrefs",
            "biotype": "gene_type",
        }

        for attribute in f.attributes.items():
            key = attribute[0]

            if key in attributes:
                val = attribute[1]

                if len(val) == 1:
                    val = val[0]
                    if key == "ID" and val.startswith("gene"):
                        val = f"{NamespacePrefix.ENSEMBL.value}:{val.split(':')[1]}"

                if key == "description":
                    gene["label"] = val.split("[")[0].strip()
                    if "Source:" in val:
                        src_name = (
                            val.split("[")[-1]
                            .split("Source:")[-1]
                            .split("Acc")[0]
                            .split(";")[0]
                        )
                        src_id = val.split("Acc:")[-1].split("]")[0]
                        if ":" in src_id:
                            src_id = src_id.split(":")[-1]
                        source = self._get_xref_associated_with(src_name, src_id)
                        if "xrefs" in source:
                            gene["xrefs"] = source["xrefs"]
                        elif "associated_with" in source:
                            gene["associated_with"] = source["associated_with"]
                    continue

                gene[attributes[key]] = val

    def _add_location(self, f: Feature, gene: dict, accession_numbers: dict) -> dict:
        """Add GA4GH SequenceLocation to a gene record.
        https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#sequencelocation

        :param f: A gene from the data
        :param gene: A transformed gene record
        :param accession_numbers: Accession numbers for each chromosome and scaffold
        :return: gene record dictionary with location added
        """
        return self._get_sequence_location(accession_numbers[f.seqid], f, gene)

    def _get_xref_associated_with(self, src_name: str, src_id: str) -> dict:
        """Get xref or associated_with concept.

        :param src_name: Source name
        :param src_id: The source's accession number
        :return: A dict containing an other identifier or xref
        """
        source = {}
        if src_name.startswith("HGNC"):
            source["xrefs"] = [f"{NamespacePrefix.HGNC.value}:{src_id}"]
        elif src_name.startswith("NCBI"):
            source["xrefs"] = [f"{NamespacePrefix.NCBI.value}:{src_id}"]
        elif src_name.startswith("UniProt"):
            source["associated_with"] = [f"{NamespacePrefix.UNIPROT.value}:{src_id}"]
        elif src_name.startswith("miRBase"):
            source["associated_with"] = [f"{NamespacePrefix.MIRBASE.value}:{src_id}"]
        elif src_name.startswith("RFAM"):
            source["associated_with"] = [f"{NamespacePrefix.RFAM.value}:{src_id}"]
        return source

    def _add_meta(self) -> None:
        """Add Ensembl metadata.

        :raise GeneNormalizerEtlError: if requisite metadata is unset
        """
        if not self._version or not self._assembly:
            err_msg = "Source metadata unavailable -- was data properly acquired before attempting to load DB?"
            raise GeneNormalizerEtlError(err_msg)
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
                non_commercial=False, share_alike=False, attribution=False
            ),
            genome_assemblies=[self._assembly],
        )

        self._database.add_source_metadata(self._src_name, metadata)
