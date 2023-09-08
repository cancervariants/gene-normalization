"""This module defines the Ensembl ETL methods."""
import logging
from pathlib import Path
import re
from ftplib import FTP
from typing import Dict, List
from biocommons.seqrepo import SeqRepo

import gffutils
from gffutils.feature import Feature

from .base import Base
from gene import APP_ROOT
from gene.schemas import SourceName, NamespacePrefix, Strand, SourceMeta
from gene.database import AbstractDatabase


logger = logging.getLogger("gene")
logger.setLevel(logging.DEBUG)


class Ensembl(Base):
    """ETL the Ensembl source into the normalized database."""

    def __init__(self, database: AbstractDatabase, host: str = "ftp.ensembl.org",
                 data_dir: str = "pub/current_gff3/homo_sapiens/",
                 src_data_dir: Path = APP_ROOT / "data" / "ensembl") -> None:
        """Initialize Ensembl ETL class.

        :param database: DynamoDB database
        :param host: FTP host name
        :param data_dir: FTP data directory to use
        :param src_data_dir: Data directory for Ensembl
        """
        super().__init__(database, host, data_dir, src_data_dir)
        self._version = None
        self._fn = None
        self._data_url = None
        self._assembly = None

    def _download_data(self) -> None:
        """Download latest Ensembl GFF3 data file."""
        logger.info("Downloading latest Ensembl data file...")
        self._create_data_directory()
        regex_pattern = r"Homo_sapiens\.(?P<assembly>GRCh\d+)\.(?P<version>\d+)\.gff3\.gz"  # noqa: E501
        regex = re.compile(regex_pattern)
        with FTP(self._host) as ftp:
            ftp.login()
            ftp.cwd(self._data_dir)
            files = ftp.nlst()
            for f in files:
                match = regex.match(f)
                if match:
                    resp = match.groupdict()
                    self._assembly = resp["assembly"]
                    self._version = resp["version"]
                    self._fn = f
                    self._data_url = f"ftp://{self._host}/{self._data_dir}{self._fn}"  # noqa: E501
                    new_fn = f"ensembl_{self._version}.gff3"
                    if not (self.src_data_dir / new_fn).exists():
                        self._ftp_download_file(ftp, self._fn, self.src_data_dir,
                                                new_fn)
                        logger.info(f"Successfully downloaded Ensembl {self._version}"
                                    f" data.")
                    else:
                        logger.info(f"Ensembl {self._version} data already exists.")
                    break

    def _extract_data(self, *args, **kwargs):
        """Extract data from the Ensembl source."""
        if "data_path" in kwargs:
            self._data_src = kwargs["data_path"]
        else:
            self._data_src = sorted(list(self.src_data_dir.iterdir()))[-1]

    def _transform_data(self, *args, **kwargs):
        """Transform the Ensembl source."""
        logger.info("Transforming Ensembl...")
        db = gffutils.create_db(str(self._data_src),
                                dbfn=":memory:",
                                force=True,
                                merge_strategy="create_unique",
                                keep_order=True)

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
                    gene = \
                        self._add_gene(f, self.seqrepo, accession_numbers)
                    if gene:
                        self._load_gene(gene)
        logger.info("Successfully transformed Ensembl.")

    def _add_gene(self, f: Feature, sr: SeqRepo, accession_numbers: Dict) -> Dict:
        """Create a transformed gene record.

        :param f: A gene from the data
        :param sr: Access to the seqrepo
        :param accession_numbers: Accession numbers for each chromosome and scaffold
        :return: A gene dictionary containing data if the ID attribute exists.
        """
        gene = dict()
        if f.strand == "-":
            gene["strand"] = Strand.REVERSE.value
        elif f.strand == "+":
            gene["strand"] = Strand.FORWARD.value
        gene["src_name"] = SourceName.ENSEMBL.value

        self._add_attributes(f, gene)
        location = self._add_location(f, gene, sr, accession_numbers)
        if location:
            gene["locations"] = [location]

        gene["label_and_type"] = \
            f"{gene['concept_id'].lower()}##identity"
        gene["item_type"] = "identity"

        return gene

    def _add_attributes(self, f: Feature, gene: Dict) -> None:
        """Add concept_id, symbol, xrefs, and associated_with to a gene record.

        :param f: A gene from the data
        :param gene: A transformed gene record
        """
        attributes = {
            "ID": "concept_id",
            "Name": "symbol",
            "description": "xrefs",
            "biotype": "gene_type"
        }

        for attribute in f.attributes.items():
            key = attribute[0]

            if key in attributes.keys():
                val = attribute[1]

                if len(val) == 1:
                    val = val[0]
                    if key == "ID":
                        if val.startswith("gene"):
                            val = f"{NamespacePrefix.ENSEMBL.value}:" \
                                  f"{val.split(':')[1]}"

                if key == "description":
                    gene["label"] = val.split("[")[0].strip()
                    if "Source:" in val:
                        src_name = val.split("[")[-1].split(
                            "Source:")[-1].split("Acc")[0].split(";")[0]
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

    def _add_location(
        self, f: Feature, gene: Dict, sr: SeqRepo, accession_numbers: Dict
    ) -> Dict:
        """Add GA4GH SequenceLocation to a gene record.
        https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#sequencelocation

        :param f: A gene from the data
        :param gene: A transformed gene record
        :param sr: Access to the seqrepo
        :param accession_numbers: Accession numbers for each chromosome and scaffold
        :return: gene record dictionary with location added
        """
        return self._get_sequence_location(accession_numbers[f.seqid], f, gene, sr)

    def _get_xref_associated_with(self, src_name: str, src_id: str) -> Dict:
        """Get xref or associated_with concept.

        :param src_name: Source name
        :param src_id: The source's accession number
        :return: A dict containing an other identifier or xref
        """
        source = dict()
        if src_name.startswith("HGNC"):
            source["xrefs"] = \
                [f"{NamespacePrefix.HGNC.value}:{src_id}"]
        elif src_name.startswith("NCBI"):
            source["xrefs"] = \
                [f"{NamespacePrefix.NCBI.value}:{src_id}"]
        elif src_name.startswith("UniProt"):
            source["associated_with"] = [f"{NamespacePrefix.UNIPROT.value}:{src_id}"]
        elif src_name.startswith("miRBase"):
            source["associated_with"] = [f"{NamespacePrefix.MIRBASE.value}:{src_id}"]
        elif src_name.startswith("RFAM"):
            source["associated_with"] = [f"{NamespacePrefix.RFAM.value}:{src_id}"]
        return source

    def perform_etl(self, *args, **kwargs) -> List[str]:
        """Extract, Transform, and Load data into DynamoDB database.

        :return: Concept IDs of concepts successfully loaded
        """
        self._download_data()
        self._extract_data()
        self._add_meta()
        self._transform_data()
        self._database.complete_write_transaction()
        return self._processed_ids

    def _add_meta(self, *args, **kwargs) -> None:
        """Add Ensembl metadata."""
        metadata = SourceMeta(
            data_license="custom",
            data_license_url="https://useast.ensembl.org/info/about"
                             "/legal/disclaimer.html",
            version=self._version,
            data_url=self._data_url,
            rdp_url=None,
            data_license_attributes={
                "non_commercial": False,
                "share_alike": False,
                "attribution": False
            },
            genome_assemblies=[self._assembly]
        )

        self._database.add_source_metadata(self._src_name, metadata)
