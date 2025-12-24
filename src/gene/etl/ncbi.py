"""Defines ETL methods for the NCBI data source."""

import csv
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

import gffutils
from wags_tails import NcbiGenomeData

from gene import PREFIX_LOOKUP, SEQREPO_ROOT_DIR
from gene.database import AbstractDatabase
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

if TYPE_CHECKING:
    from wags_tails.ncbi import NcbiGenePaths

_logger = logging.getLogger(__name__)


class NCBI(Base):
    """ETL class for NCBI source"""

    def __init__(
        self,
        database: AbstractDatabase,
        seqrepo_dir: Path = SEQREPO_ROOT_DIR,
        data_path: Path | None = None,
        silent: bool = True,
    ) -> None:
        """Instantiate Base class.

        :param database: database instance
        :param seqrepo_dir: Path to seqrepo directory
        :param data_path: path to app data directory
        :param silent: if True, don't print ETL result to console
        """
        super().__init__(database, seqrepo_dir, data_path, silent)
        self._genome_data_handler = NcbiGenomeData(data_path, silent)

    def _extract_data(self, use_existing: bool) -> None:
        """Acquire NCBI data file and get metadata.

        :param use_existing: if True, use latest available local file
        """
        _logger.info("Gathering %s data...", self._src_name.value)
        self._gff_src, self._assembly = self._genome_data_handler.get_latest(
            from_local=use_existing
        )
        gene_paths: NcbiGenePaths
        gene_paths, self._version = self._data_source.get_latest(
            from_local=use_existing
        )
        self._info_src = gene_paths.gene_info
        self._history_src = gene_paths.gene_history
        self._gene_url = (
            "ftp.ncbi.nlm.nih.govgene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz"
        )
        self._history_url = "ftp.ncbi.nlm.nih.govgene/DATA/gene_history.gz"
        self._assembly_url = "ftp.ncbi.nlm.nih.govgenomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/"

    def _get_prev_symbols(self) -> dict[str, str]:
        """Store a gene's symbol history.

        :return: A dictionary of a gene's previous symbols
        """
        # get symbol history
        history_file = self._history_src.open()
        history = csv.reader(history_file, delimiter="\t")
        next(history)
        prev_symbols = {}
        for row in history:
            # Only interested in rows that have homo sapiens tax id
            if row[0] == "9606":
                if row[1] != "-":
                    gene_id = row[1]
                    if gene_id in prev_symbols:
                        prev_symbols[gene_id].append(row[3])
                    else:
                        prev_symbols[gene_id] = [row[3]]
                else:
                    # Load discontinued genes
                    params = {
                        "concept_id": f"{NamespacePrefix.NCBI.value}:{row[2]}",
                        "symbol": row[3],
                        "symbol_status": SymbolStatus.DISCONTINUED.value,
                    }
                    self._load_gene(params)
        history_file.close()
        return prev_symbols

    def _add_xrefs_associated_with(self, val: list[str], params: dict) -> None:
        """Add xrefs and associated_with refs to a transformed gene.

        :param val: A list of source ids for a given gene
        :param params: A transformed gene record
        """
        params["xrefs"] = []
        params["associated_with"] = []
        for src in val:
            src_name = src.split(":")[0].upper()
            src_id = src.split(":")[-1]
            if src_name == "GENEID":
                params["concept_id"] = f"{NamespacePrefix.NCBI.value}:{src_id}"
            elif (
                src_name in NamespacePrefix.__members__
                and NamespacePrefix[src_name].value in PREFIX_LOOKUP
            ):
                params["xrefs"].append(f"{NamespacePrefix[src_name].value}:{src_id}")
            else:
                if src_name.startswith("MIM"):
                    prefix = NamespacePrefix.OMIM.value
                elif src_name.startswith("IMGT/GENE-DB"):
                    prefix = NamespacePrefix.IMGT_GENE_DB.value
                elif src_name.startswith("MIRBASE"):
                    prefix = NamespacePrefix.MIRBASE.value
                else:
                    prefix = None
                if prefix:
                    params["associated_with"].append(f"{prefix}:{src_id}")
                else:
                    _logger.info("%s is not in NameSpacePrefix.", src_name)
        if not params["xrefs"]:
            del params["xrefs"]
        if not params["associated_with"]:
            del params["associated_with"]

    def _get_gene_info(self, prev_symbols: dict[str, str]) -> dict[str, str]:
        """Store genes from NCBI info file.

        :param prev_symbols: A dictionary of a gene's previous symbols
        :return: A dictionary of gene's from the NCBI info file.
        """
        info_genes = {}

        # open info file, skip headers
        with self._info_src.open() as info_file:
            info = csv.reader(info_file, delimiter="\t")
            next(info)

            for row in info:
                params = {"locations": []}
                params["concept_id"] = f"{NamespacePrefix.NCBI.value}:{row[1]}"
                # get symbol
                params["symbol"] = row[2]
                # get aliases
                if row[4] != "-":
                    params["aliases"] = row[4].split("|")
                else:
                    params["aliases"] = []
                # get associated_with
                if row[5] != "-":
                    associated_with = row[5].split("|")
                    self._add_xrefs_associated_with(associated_with, params)
                # get chromosome location
                do_exclude = self._add_location_annotations(row, params)
                if do_exclude:
                    # Exclude genes with multiple distinct locations (e.g. OMS)
                    continue
                # get label
                if row[8] != "-":
                    params["label"] = row[8]
                # add prev symbols
                if row[1] in prev_symbols:
                    params["previous_symbols"] = prev_symbols[row[1]]
                info_genes[params["symbol"]] = params
                # get type
                params["gene_type"] = row[9]
        return info_genes

    def _get_gene_gff(self, db: gffutils.FeatureDB, info_genes: dict) -> None:
        """Store genes from NCBI gff file.

        :param db: GFF database
        :param info_genes: A dictionary of gene's from the NCBI info file.
        """
        for f in db.all_features():
            if f.attributes.get("ID"):
                f_id = f.attributes.get("ID")[0]
                if f_id.startswith("gene"):
                    symbol = f.attributes["Name"][0]
                    if symbol in info_genes:
                        # Just need to add SequenceLocation
                        params = info_genes.get(symbol)
                        vrs_sq_location = self._get_vrs_sq_location(db, params, f_id)
                        if vrs_sq_location:
                            params["locations"].append(vrs_sq_location)
                    else:
                        # Need to add entire gene
                        gene = self._add_gff_gene(db, f, f_id)
                        info_genes[gene["symbol"]] = gene

    def _add_gff_gene(
        self, db: gffutils.FeatureDB, f: gffutils.Feature, f_id: str
    ) -> dict | None:
        """Create a transformed gene recor from NCBI gff file.

        :param db: GFF database
        :param f: A gene from the gff data file
        :param f_id: The feature's ID
        :return: A gene dictionary if the ID attribute exists. Else return None.
        """
        params = {}
        params["src_name"] = SourceName.NCBI.value
        self._add_attributes(f, params)
        sq_loc = self._get_vrs_sq_location(db, params, f_id)
        if sq_loc:
            params["locations"] = [sq_loc]
        else:
            params["locations"] = []
        params["label_and_type"] = f"{params['concept_id'].lower()}##identity"
        return params

    def _add_attributes(self, f: gffutils.feature.Feature, gene: dict) -> None:
        """Add concept_id, symbol, and xrefs/associated_with to a gene record.

        :param gffutils.feature.Feature f: A gene from the data
        :param gene: A transformed gene record
        """
        attributes = ["ID", "Name", "description", "Dbxref"]

        for attribute in f.attributes.items():
            key = attribute[0]
            if key in attributes:
                val = attribute[1]

                if len(val) == 1 and key != "Dbxref":
                    val = val[0]

                if key == "Dbxref":
                    self._add_xrefs_associated_with(val, gene)
                elif key == "Name":
                    gene["symbol"] = val

    def _get_vrs_sq_location(
        self, db: gffutils.FeatureDB, params: dict, f_id: str
    ) -> dict:
        """Store GA4GH VRS SequenceLocation in a gene record.
        https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#sequencelocation

        :param db: GFF database
        :param params: A transformed gene record
        :param f_id: The feature's ID
        :return: A GA4GH VRS SequenceLocation
        """
        gene = db[f_id]
        params["strand"] = gene.strand
        return self._get_sequence_location(gene.seqid, gene, params)

    def _get_xref_associated_with(self, src_name: str, src_id: str) -> dict:
        """Get xref or associated_with ref.

        :param src_name: Source name
        :param src_id: The source's accession number
        :return: A dict containing an xref or associated_with ref
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

    def _add_location_annotations(self, row: list[str], params: dict) -> bool:
        """Add location annotations to ``params``

        :param row: A row in NCBI data file
        :param params: A transformed gene record. This may get mutated in place.
        :return: ``True`` if gene found with multiple distinct locations.
            ``False``, otherwise.
        """
        params["location_annotations"] = []
        chromosomes_locations = self._set_chromsomes_locations(row, params)
        locations = chromosomes_locations["locations"]
        chromosomes = chromosomes_locations["chromosomes"]
        if chromosomes_locations["exclude"]:
            return True

        if chromosomes and not locations:
            for chromosome in chromosomes:
                if chromosome == "MT":
                    params["location_annotations"].append(Chromosome.MITOCHONDRIA.value)
                else:
                    params["location_annotations"].append(chromosome.strip())
        elif locations:
            self._add_chromosome_location(locations, params)
        if not params["location_annotations"]:
            del params["location_annotations"]
        return False

    def _set_chromsomes_locations(self, row: list[str], params: dict) -> dict:
        """Set chromosomes and locations for a given gene record.

        :param row: A gene row in the NCBI data file
        :param params: A transformed gene record
        :return: A dictionary containing a gene's chromosomes and locations
        """
        chromosomes = None
        if row[6] != "-":
            chromosomes = row[6].split("|") if "|" in row[6] else [row[6]]

            if (
                len(chromosomes) >= 2  # noqa: PLR2004
                and chromosomes
                and "X" not in chromosomes
                and "Y" not in chromosomes
            ):
                _logger.info(
                    "%s contains multiple distinct chromosomes: %s", row[2], chromosomes
                )
                chromosomes = None

        locations = None
        exclude = False
        if row[7] != "-":
            if "|" in row[7]:
                locations = row[7].split("|")
            elif ";" in row[7]:
                locations = row[7].split(";")
            elif "and" in row[7]:
                locations = row[7].split("and")
            else:
                locations = [row[7]]

            # Sometimes locations will store the same location twice
            if len(locations) == 2 and locations[0] == locations[1]:  # noqa: PLR2004
                locations = [locations[0]]

            # Exclude genes where there are multiple distinct locations
            # i.e. OMS: '10q26.3', '19q13.42-q13.43', '3p25.3'
            if len(locations) > 2:  # noqa: PLR2004
                _logger.info(
                    "%s contains multiple distinct locations: %s", row[2], locations
                )
                locations = None
                exclude = True

            # NCBI sometimes contains invalid map locations
            if locations:
                for i in range(len(locations)):
                    loc = locations[i].strip()
                    if not re.match("^([1-9][0-9]?|X[pq]?|Y[pq]?)", loc):
                        _logger.info(
                            "%s contains invalid map location: %s", row[2], loc
                        )
                        params["location_annotations"].append(loc)
                        del locations[i]
        return {"locations": locations, "chromosomes": chromosomes, "exclude": exclude}

    def _add_chromosome_location(self, locations: list, params: dict) -> None:
        """Add a chromosome location to the location list.

        :param locations: NCBI map locations for a gene record.
        :param params: A transformed gene record
        """
        for i in range(len(locations)):
            loc = locations[i].strip()
            location = {}

            if Annotation.ALT_LOC.value in loc:
                loc = loc.split(f"{Annotation.ALT_LOC.value}")[0].strip()
                params["location_annotations"].append(Annotation.ALT_LOC.value)

            contains_centromere = False
            if "cen" in loc:
                contains_centromere = True

            arm_match = re.search("[pq]", loc)
            if arm_match and not contains_centromere:
                arm_ix = arm_match.start()
                chromosome = loc[:arm_ix].strip()

                # NCBI sometimes stores invalid map locations
                # i.e. 7637 stores 'map from Rosati ref via FISH [AFS]'
                if not re.match("^([1-9][0-9]?|X|Y|MT)$", chromosome):
                    continue
                location["chr"] = chromosome

                # Check to see if there is a band / sub band included
                if arm_ix != len(loc) - 1:
                    if "-" in loc:
                        self._set_cl_interval_range(loc, arm_ix, location)
                    else:
                        # Location only gives start
                        start = loc[arm_ix:]
                        location["start"] = start
                        location["end"] = start
                else:
                    # Only arm is included
                    location["start"] = loc[arm_ix]
                    location["end"] = loc[arm_ix]
            elif contains_centromere:
                self._set_centromere_location(loc, location)
            else:
                # Location only gives chr
                params["location_annotations"].append(loc)

    def _set_centromere_location(self, loc: str, location: dict) -> None:
        """Set centromere location for a gene.

        :param loc: A gene location
        :param location: GA4GH location
        """
        centromere_ix = re.search("cen", loc).start()
        if "-" in loc:
            # Location gives both start and end
            range_ix = re.search("-", loc).start()
            if "q" in loc:
                location["chr"] = loc[:centromere_ix].strip()
                location["start"] = "cen"
                location["end"] = loc[range_ix + 1 :]
            elif "p" in loc:
                p_ix = re.search("p", loc).start()
                location["chr"] = loc[:p_ix].strip()
                location["end"] = "cen"
                location["start"] = loc[:range_ix]
        else:
            location["chr"] = loc[:centromere_ix].strip()
            location["start"] = "cen"
            location["end"] = "cen"

    def _transform_data(self) -> None:
        """Modify data and pass to loading functions."""
        _logger.info("Transforming NCBI...")
        prev_symbols = self._get_prev_symbols()
        info_genes = self._get_gene_info(prev_symbols)

        # create db for gff file
        db = gffutils.create_db(
            str(self._gff_src),
            dbfn=":memory:",
            force=True,
            merge_strategy="create_unique",
            keep_order=True,
        )

        self._get_gene_gff(db, info_genes)

        for gene in info_genes:
            self._load_gene(info_genes[gene])
        _logger.info("Successfully transformed NCBI.")

    def _add_meta(self) -> None:
        """Add Ensembl metadata.

        :raise GeneNormalizerEtlError: if required metadata is unset
        """
        if not all(
            [
                self._version,
                self._gene_url,
                self._history_url,
                self._assembly_url,
                self._assembly,
            ]
        ):
            err_msg = "Source metadata unavailable -- was data properly acquired before attempting to load DB?"
            raise GeneNormalizerEtlError(err_msg)
        metadata = SourceMeta(
            data_license="custom",
            data_license_url="https://www.ncbi.nlm.nih.gov/home/about/policies/",
            version=self._version,
            data_url={
                "info_file": self._gene_url,
                "history_file": self._history_url,
                "assembly_file": self._assembly_url,
            },
            rdp_url="https://reusabledata.org/ncbi-gene.html",
            data_license_attributes=DataLicenseAttributes(
                non_commercial=False, share_alike=False, attribution=False
            ),
            genome_assemblies=[self._assembly],
        )

        self._database.add_source_metadata(SourceName.NCBI, metadata)
