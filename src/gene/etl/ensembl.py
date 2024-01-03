"""Defines the Ensembl ETL methods."""
import logging
import re
from typing import Dict, Optional
from urllib.parse import unquote

import click
import gffpandas.gffpandas as gffpd
import pandas as pd
from tqdm import tqdm

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
        df = gffpd.read_gff3(self._data_file).attributes_to_columns()
        df["seq_id"] = df["seq_id"].astype(str)
        df["description"] = df["description"].apply(
            lambda d: unquote(d) if d is not None else None
        )
        accession_numbers = {}
        for _, row in df[df["type"].isin(["chromosome", "scaffold"])].iterrows():
            accession_numbers[row.seq_id] = row.Alias.split(",")[-1]

        gene_df = df[df["ID"].str.startswith("gene", na=False)]

        if not self._silent:
            click.echo(f"Loading rows from {self._data_file}:")
        for _, row in tqdm(
            gene_df.iterrows(), total=gene_df.shape[0], disable=self._silent, ncols=80
        ):
            gene = self._add_gene(row, accession_numbers)
            self._load_gene(gene)
        _logger.info("Ensembl data transform complete.")

    def _add_gene(self, row: pd.Series, accession_numbers: Dict) -> Dict:
        """Create a transformed gene record.

        :param row: A row from the gene data table
        :param accession_numbers: Accession numbers for each chromosome and scaffold
        :return: A gene dictionary containing data if the ID attribute exists.
        """
        gene_params = dict()
        if row.strand == "-":
            gene_params["strand"] = Strand.REVERSE.value
        elif row.strand == "+":
            gene_params["strand"] = Strand.FORWARD.value

        self._add_attributes(row, gene_params)
        location = self._build_sequence_location(
            accession_numbers[row.seq_id], row, gene_params["concept_id"]
        )
        if location:
            gene_params["locations"] = [location]

        gene_params["label_and_type"] = f"{gene_params['concept_id'].lower()}##identity"
        gene_params["item_type"] = "identity"

        return gene_params

    def _add_attributes(self, row: pd.Series, gene: Dict) -> None:
        """Add concept_id, symbol, and xrefs to a gene record.

        :param row: A gene from the data
        :param gene: A transformed gene record
        """
        gene["concept_id"] = f"{NamespacePrefix.ENSEMBL.value}:{row.ID.split(':')[1]}"
        gene["symbol"] = row.Name
        gene["gene_type"] = row.biotype

        if row.description:
            pattern = "^(.*) \\[Source:([^\\s]*)?( .*)?Acc:(.*:)?(.*)?\\]$"
            matches = re.findall(pattern, row.description)
            if matches:
                gene["label"] = matches[0][0]
                if matches[0][1] and matches[0][4]:
                    gene["xrefs"] = [self._get_xref(matches[0][1], matches[0][4])]

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
        _logger.warning("Unrecognized source name: %s:%s", src_name, src_id)
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
