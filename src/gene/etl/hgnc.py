"""Defines the HGNC ETL methods."""
import json
import logging
import re
import shutil
from datetime import datetime
from ftplib import FTP
from pathlib import Path
from typing import Dict

from dateutil import parser

from gene import APP_ROOT, PREFIX_LOOKUP
from gene.database import AbstractDatabase
from gene.etl.base import Base
from gene.etl.exceptions import (
    GeneFileVersionError,
    GeneNormalizerEtlError,
    GeneSourceFetchError,
)
from gene.schemas import (
    Annotation,
    Chromosome,
    NamespacePrefix,
    SourceMeta,
    SourceName,
    SymbolStatus,
)

logger = logging.getLogger("gene")
logger.setLevel(logging.DEBUG)


class HGNC(Base):
    """ETL the HGNC source into the normalized database."""

    def __init__(
        self,
        database: AbstractDatabase,
        host: str = "ftp.ebi.ac.uk",
        data_dir: str = "pub/databases/genenames/hgnc/json/",
        src_data_dir: Path = APP_ROOT / "data" / "hgnc",
        fn: str = "hgnc_complete_set.json",
    ) -> None:
        """Initialize HGNC ETL class.

        :param database: gene database for adding new data
        :param host: FTP host name
        :param data_dir: FTP data directory to use
        :param src_data_dir: Data directory for HGNC
        :param fn: Data file to download
        """
        super().__init__(database, host, data_dir, src_data_dir)
        self._data_file_pattern = re.compile(r"hgnc_(\d+)\.json")
        self._data_url = f"ftp://{host}/{data_dir}{fn}"
        self._fn = fn
        self._version = None

    def _is_up_to_date(self, data_file: Path) -> bool:
        """Verify whether local data is up-to-date with latest available remote file.

        :param data_file: path to latest local file
        :return: True if data is up-to-date
        :raise GeneFileVersionError: if unable to get version from local HGNC file
        :raise GeneSourceFetchError: if unable to get latest version available from HGNC
        """
        local_match = re.match(self._data_file_pattern, data_file.name)
        if not local_match:
            raise GeneFileVersionError(
                f"Unable to parse version number from local HGNC file: {data_file.absolute()}"
            )
        version = local_match.groups()[0]
        with FTP(self._host) as ftp:
            ftp.login()
            timestamp = ftp.voidcmd(f"MDTM {self._data_dir}{self._fn}")[4:].strip()
        date = str(parser.parse(timestamp)).split()[0]
        try:
            remote_version = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")
        except ValueError:
            raise GeneSourceFetchError(
                f"Unable to parse version number from remote HGNC timestamp: {date}"
            )
        return version == remote_version

    def _download_data(self) -> Path:
        """Download HGNC JSON data file.

        :return: path to newly-downloaded file
        """
        logger.info("Downloading HGNC data file...")

        tmp_fn = "hgnc_version.json"
        version = self._ftp_download(
            self._host, self._data_dir, tmp_fn, self.src_data_dir, self._fn
        )
        final_location = f"{self.src_data_dir}/hgnc_{version}.json"
        shutil.move(f"{self.src_data_dir}/{tmp_fn}", final_location)
        logger.info(f"Successfully downloaded HGNC data file to {final_location}.")
        return Path(final_location)

    def _extract_data(self, use_existing: bool) -> None:
        """Acquire HGNC data file and get metadata.

        :param use_existing: if True, use latest available local file
        """
        self._data_file = self._acquire_data_file(
            "hgnc_*.json", use_existing, self._is_up_to_date, self._download_data
        )
        match = self._data_file_pattern.match(self._data_file.name)
        self._version = match.groups()[0]

    def _transform_data(self) -> None:
        """Transform the HGNC source."""
        logger.info("Transforming HGNC...")
        with open(self._data_file, "r") as f:
            data = json.load(f)

        records = data["response"]["docs"]

        for r in records:
            gene = dict()
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
                self._get_location(r, gene)
            if "locus_type" in r:
                gene["gene_type"] = r["locus_type"]
                self._load_gene(gene)
        logger.info("Successfully transformed HGNC.")

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

    def _get_xrefs_associated_with(self, r: Dict, gene: Dict) -> None:
        """Store xrefs and/or associated_with refs in a gene record.

        :param r: A gene record in the HGNC data file
        :param gene: A transformed gene record
        """
        xrefs = list()
        associated_with = list()
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
                    if NamespacePrefix[key.upper()].value in PREFIX_LOOKUP.keys():
                        self._get_xref_associated_with(key, src, r, xrefs)
                    else:
                        self._get_xref_associated_with(key, src, r, associated_with)
                else:
                    logger.warning(f"{key} not in schemas.py")

        if xrefs:
            gene["xrefs"] = xrefs
        if associated_with:
            gene["associated_with"] = associated_with

    def _get_xref_associated_with(
        self, key: str, src: str, r: Dict, src_type: Dict
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
            src_type.append(f"{NamespacePrefix[key.upper()].value}" f":{r[src]}")

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

    def _set_annotation(self, loc: str, gene: Dict) -> None:
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
        if not all([self._version, self._data_url]):
            raise GeneNormalizerEtlError(
                "Source metadata unavailable -- was data properly acquired before attempting to load DB?"
            )
        metadata = SourceMeta(
            data_license="CC0",
            data_license_url="https://www.genenames.org/about/license/",
            version=self._version,
            data_url={"complete_set_archive": self._data_url},
            rdp_url=None,
            data_license_attributes={
                "non_commercial": False,
                "share_alike": False,
                "attribution": False,
            },
            genome_assemblies=[],
        )
        self._database.add_source_metadata(SourceName.HGNC, metadata)
