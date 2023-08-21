"""Defines ETL methods for the NCBI data source."""
import csv
import logging
import re
from datetime import datetime
from ftplib import FTP
from pathlib import Path
from typing import Dict, List, Optional

import gffutils
from biocommons.seqrepo import SeqRepo

from gene import APP_ROOT, PREFIX_LOOKUP
from gene.database import AbstractDatabase
from gene.etl.base import Base, FileUnavailableError, NormalizerEtlError
from gene.etl.vrs_locations import ChromosomeLocation, SequenceLocation
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

TODAY = datetime.today().strftime("%Y%m%d")


class NCBI(Base):
    """ETL class for NCBI source"""

    def __init__(
        self,
        database: AbstractDatabase,
        host: str = "ftp.ncbi.nlm.nih.gov",
        data_dir: str = "gene/DATA/",
        src_data_dir: Path = APP_ROOT / "data" / "ncbi",
    ) -> None:
        """Construct the NCBI ETL instance.

        :param database: gene database for adding new data
        :param host: FTP host name
        :param data_dir: FTP data directory to use
        :param src_data_dir: Data directory for NCBI
        """
        super().__init__(database, host, data_dir, src_data_dir)
        self._sequence_location = SequenceLocation()
        self._chromosome_location = ChromosomeLocation()
        self._ftp_hostname = host
        self._assembly = None
        self._gene_url = None
        self._history_url = None
        self._assembly_url = None

    @staticmethod
    def _navigate_ftp_genome_assembly(ftp: FTP) -> None:
        """Navigate NCBI FTP filesystem to directory containing latest assembly annotation data.

        :param ftp: logged-in FTP instance
        :return: None, but modifies FTP connection in-place
        :raise FileUnavailableError: if navigation fails
        """
        major_annotation_pattern = r"GCF_\d+\.\d+_GRCh\d+.+"
        ftp.cwd(
            "genomes/refseq/vertebrate_mammalian/Homo_sapiens/"
            "latest_assembly_versions"
        )
        try:
            grch_dirs = [d for d in ftp.nlst() if re.match(major_annotation_pattern, d)]
            grch_dir = grch_dirs[0]
        except (IndexError, AttributeError):
            raise FileUnavailableError(
                "No directories matching expected latest assembly version pattern"
            )
        ftp.cwd(grch_dir)

    def _gff_is_up_to_date(self, gff: Path) -> bool:
        """Verify whether local GRCh38 annotation file is up-to-date. Currently, their
        API endpoints require auth keys (adding complexity for new users) and may or may not
        give us exactly what we want, so we ascertain version availability by manually
        checking what's listed in the FTP filesystem.

        :param gff: path to local GFF file (file should be saved like `ncbi_GRCh38.p14.gff`)
        :return: True if file version matches most recent known remote version
        """
        try:
            version = re.match(r"ncbi_(.+)", gff.stem).groups()[0]
        except (IndexError, AttributeError):
            raise FileUnavailableError(
                f"Unable to parse version from NCBI GRCh38 annotation file: {gff.absolute()}"
            )

        genomic_gff_pattern = r"GCF_\d+\.\d+_(GRCh\d+\.\w\d+)_genomic.gff.gz"
        with FTP(self._host) as ftp:
            ftp.login()
            self._navigate_ftp_genome_assembly(ftp)
            for file in ftp.nlst():
                match = re.match(genomic_gff_pattern, file)
                if match and match.groups():
                    latest_version = match.groups()[0]
                    return version == latest_version
        raise FileUnavailableError(
            "Unable to parse latest available NCBI GRCh38 annotation version"
        )

    def _download_gff(self) -> Path:
        """Download NCBI GRCh38 annotation file.

        :return: Path to downloaded file
        """
        logger.info("Downloading NCBI genome annotation file...")
        genomic_gff_pattern = r"GCF_\d+\.\d+_(GRCh\d+\.\w\d+)_genomic.gff.gz"
        with FTP(self._host) as ftp:
            ftp.login()
            self._navigate_ftp_genome_assembly(ftp)
            genomic_filename = None
            version = None
            for f in ftp.nlst():
                gff_match = re.match(genomic_gff_pattern, f)
                if gff_match and gff_match.groups():
                    genomic_filename = f
                    version = gff_match.groups()[0]
            if not version or not genomic_filename:
                raise FileUnavailableError(
                    "Unable to parse latest available NCBI GRCh38 annotation"
                )
            new_filename = f"ncbi_{version}.gff"
            self._ftp_download_file(
                ftp, genomic_filename, self.src_data_dir, new_filename
            )
        logger.info(
            f"Downloaded NCBI genome annotation file to {self.src_data_dir / new_filename}"
        )
        return self.src_data_dir / new_filename

    def _history_file_is_up_to_date(self, history_file: Path) -> bool:
        """Verify whether local NCBI name history file is up-to-date. It should be recalculated daily, so we can just perform a check against today's date.

        :param history_file: path to local history file (file should be saved like `ncbi_history_20230315.tsv`)
        :return: True if file version matches most recent expected remote version
        :raise FileUnavailableError: if parsing version from local file fails
        """
        try:
            version = re.match(r"ncbi_history_(\d+).tsv", history_file.name).groups()[0]
        except (IndexError, AttributeError):
            raise FileUnavailableError(
                f"Unable to parse version from NCBI history file: {history_file.absolute()}"
            )
        with FTP(self._host) as ftp:
            ftp.login()
            ftp.cwd("gene/DATA/")
            file_changed_date = ftp.sendcmd("MDTM gene_history.gz")[4:12]
        return version == file_changed_date

    def _download_history_file(self) -> Path:
        """Download NCBI gene name history file

        :return: Path to downloaded file
        """
        fn = f"ncbi_history_{TODAY}.tsv"
        data_fn = "gene_history.gz"
        logger.info("Downloading NCBI gene_history...")
        self._ftp_download(self._host, self._data_dir, fn, self.src_data_dir, data_fn)
        logger.info(
            f"Successfully downloaded NCBI gene_history to {self.src_data_dir / fn}."
        )
        return self.src_data_dir / fn

    def _gene_file_is_up_to_date(self, gene_file: Path) -> bool:
        """Verify whether local NCBI gene info file is up-to-date. It appears to be recalculated daily,
        so we can just perform a check against today's date.

        :param gene_file: path to local NCBI info file (file should be saved like `ncbi_info_20230315.tsv`)
        :return: True if file version matches most recent known remote version
        :raise FileUnavailableError: if parsing version from local file fails
        """
        try:
            version = re.match(r"ncbi_history_(\d+).tsv", gene_file.name).groups()[0]
        except (IndexError, AttributeError):
            raise FileUnavailableError(
                f"Unable to parse version from NCBI gene file: {gene_file.absolute()}"
            )
        with FTP(self._host) as ftp:
            ftp.login()
            ftp.cwd("gene/DATA/GENE_INFO/Mammalia/")
            file_changed_date = ftp.sendcmd("MDTM Homo_sapiens.gene_info.gz")[4:12]
        return version == file_changed_date

    def _download_gene_file(self) -> Path:
        """Download NCBI gene info file

        :return: Path to downloaded file
        """
        data_dir = f"{self._data_dir}GENE_INFO/Mammalia/"
        fn = f"ncbi_info_{TODAY}.tsv"
        data_fn = "Homo_sapiens.gene_info.gz"
        logger.info("Downloading NCBI gene_info....")
        self._ftp_download(self._host, data_dir, fn, self.src_data_dir, data_fn)
        logger.info(
            f"Successfully downloaded NCBI gene_info to {self.src_data_dir / fn}."
        )
        return self.src_data_dir / fn

    def _extract_data(self, use_existing: bool) -> None:
        """Acquire NCBI data file and get metadata.

        :param use_existing: if True, use latest available local file
        """
        self._gff_src = self.acquire_data_file(
            "ncbi_GRCh*.gff", use_existing, self._gff_is_up_to_date, self._download_gff
        )
        self._info_src = self.acquire_data_file(
            "ncbi_info_*.tsv",
            use_existing,
            self._gene_file_is_up_to_date,
            self._download_gene_file,
        )
        self._version = self._info_src.stem.split("_")[-1]
        self._history_src = self.acquire_data_file(
            f"ncbi_history_{self._version}.tsv",
            use_existing,
            self._history_file_is_up_to_date,
            self._download_history_file,
        )

        self._assembly = self._gff_src.stem.split("_")[-1]
        self._gene_url = (
            f"{self._host}gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz"
        )
        self._history_url = f"{self._host}gene/DATA/gene_history.gz"
        self._assembly_url = f"{self._host}genomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/"  # TODO

    def _get_prev_symbols(self) -> Dict[str, str]:
        """Store a gene's symbol history.

        :return: A dictionary of a gene's previous symbols
        """
        # get symbol history
        history_file = open(self._history_src, "r")
        history = csv.reader(history_file, delimiter="\t")
        next(history)
        prev_symbols = {}
        for row in history:
            # Only interested in rows that have homo sapiens tax id
            if row[0] == "9606":
                if row[1] != "-":
                    gene_id = row[1]
                    if gene_id in prev_symbols.keys():
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

    def _add_xrefs_associated_with(self, val: List[str], params: Dict) -> None:
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
                params["xrefs"].append(
                    f"{NamespacePrefix[src_name].value}" f":{src_id}"
                )
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
                    logger.info(f"{src_name} is not in NameSpacePrefix.")
        if not params["xrefs"]:
            del params["xrefs"]
        if not params["associated_with"]:
            del params["associated_with"]

    def _get_gene_info(self, prev_symbols: Dict[str, str]) -> Dict[str, str]:
        """Store genes from NCBI info file.

        :param prev_symbols: A dictionary of a gene's previous symbols
        :return: A dictionary of gene's from the NCBI info file.
        """
        # open info file, skip headers
        info_file = open(self._info_src, "r")
        info = csv.reader(info_file, delimiter="\t")
        next(info)

        info_genes = dict()
        for row in info:
            params = dict()
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
            vrs_chr_location = self._get_vrs_chr_location(row, params)
            if "exclude" in vrs_chr_location:
                # Exclude genes with multiple distinct locations (e.g. OMS)
                continue
            if not vrs_chr_location:
                vrs_chr_location = []
            params["locations"] = vrs_chr_location
            # get label
            if row[8] != "-":
                params["label"] = row[8]
            # add prev symbols
            if row[1] in prev_symbols.keys():
                params["previous_symbols"] = prev_symbols[row[1]]
            info_genes[params["symbol"]] = params
            # get type
            params["gene_type"] = row[9]
        return info_genes

    def _get_gene_gff(
        self, db: gffutils.FeatureDB, info_genes: Dict, sr: SeqRepo
    ) -> None:
        """Store genes from NCBI gff file.

        :param db: GFF database
        :param info_genes: A dictionary of gene's from the NCBI info file.
        :param sr: Access to the seqrepo
        """
        for f in db.all_features():
            if f.attributes.get("ID"):
                f_id = f.attributes.get("ID")[0]
                if f_id.startswith("gene"):
                    symbol = f.attributes["Name"][0]
                    if symbol in info_genes:
                        # Just need to add SequenceLocation
                        params = info_genes.get(symbol)
                        vrs_sq_location = self._get_vrs_sq_location(
                            db, sr, params, f_id
                        )
                        if vrs_sq_location:
                            params["locations"].append(vrs_sq_location)  # type: ignore
                    else:
                        # Need to add entire gene
                        gene = self._add_gff_gene(db, f, sr, f_id)
                        info_genes[gene["symbol"]] = gene

    def _add_gff_gene(
        self, db: gffutils.FeatureDB, f: gffutils.Feature, sr: SeqRepo, f_id: str
    ) -> Optional[Dict]:
        """Create a transformed gene recor from NCBI gff file.

        :param db: GFF database
        :param f: A gene from the gff data file
        :param sr: Access to the seqrepo
        :param f_id: The feature's ID
        :return: A gene dictionary if the ID attribute exists. Else return None.
        """
        params = dict()
        params["src_name"] = SourceName.NCBI.value
        self._add_attributes(f, params)
        sq_loc = self._get_vrs_sq_location(db, sr, params, f_id)
        if sq_loc:
            params["locations"] = [sq_loc]
        else:
            params["locations"] = list()
        params["label_and_type"] = f"{params['concept_id'].lower()}##identity"
        return params

    def _add_attributes(self, f: gffutils.Feature, gene: Dict) -> None:
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
        self, db: gffutils.FeatureDB, sr: SeqRepo, params: Dict, f_id: str
    ) -> Dict:
        """Store GA4GH VRS SequenceLocation in a gene record.
        https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#sequencelocation

        :param db: GFF database
        :param sr: Access to the seqrepo
        :param params: A transformed gene record
        :param f_id: The feature's ID
        :return: A GA4GH VRS SequenceLocation
        """
        gene = db[f_id]
        params["strand"] = gene.strand
        return self._sequence_location.add_location(gene.seqid, gene, params, sr)

    def _get_xref_associated_with(self, src_name: str, src_id: str) -> Dict:
        """Get xref or associated_with ref.

        :param src_name: Source name
        :param src_id: The source's accession number
        :return: A dict containing an xref or associated_with ref
        """
        source = dict()
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

    def _get_vrs_chr_location(self, row: List[str], params: Dict) -> List:
        """Store GA4GH VRS ChromosomeLocation in a gene record.
        https://vr-spec.readthedocs.io/en/1.1/terms_and_model.html#chromosomelocation

        :param row: A row in NCBI data file
        :param params: A transformed gene record
        :return: A list of GA4GH VRS ChromosomeLocations
        """
        params["location_annotations"] = list()
        chromosomes_locations = self._set_chromsomes_locations(row, params)
        locations = chromosomes_locations["locations"]
        chromosomes = chromosomes_locations["chromosomes"]
        if chromosomes_locations["exclude"]:
            return ["exclude"]

        location_list = list()
        if chromosomes and not locations:
            for chromosome in chromosomes:
                if chromosome == "MT":
                    params["location_annotations"].append(Chromosome.MITOCHONDRIA.value)
                else:
                    params["location_annotations"].append(chromosome.strip())
        elif locations:
            self._add_chromosome_location(locations, location_list, params)
        if not params["location_annotations"]:
            del params["location_annotations"]
        return location_list

    def _set_chromsomes_locations(self, row: List[str], params: Dict) -> Dict:
        """Set chromosomes and locations for a given gene record.

        :param row: A gene row in the NCBI data file
        :param params: A transformed gene record
        :return: A dictionary containing a gene's chromosomes and locations
        """
        chromosomes = None
        if row[6] != "-":
            if "|" in row[6]:
                chromosomes = row[6].split("|")
            else:
                chromosomes = [row[6]]

            if len(chromosomes) >= 2:
                if chromosomes and "X" not in chromosomes and "Y" not in chromosomes:
                    logger.info(
                        f"{row[2]} contains multiple distinct "
                        f"chromosomes: {chromosomes}."
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
            if len(locations) == 2:
                if locations[0] == locations[1]:
                    locations = [locations[0]]

            # Exclude genes where there are multiple distinct locations
            # i.e. OMS: '10q26.3', '19q13.42-q13.43', '3p25.3'
            if len(locations) > 2:
                logger.info(
                    f"{row[2]} contains multiple distinct " f"locations: {locations}."
                )
                locations = None
                exclude = True

            # NCBI sometimes contains invalid map locations
            if locations:
                for i in range(len(locations)):
                    loc = locations[i].strip()
                    if not re.match("^([1-9][0-9]?|X[pq]?|Y[pq]?)", loc):
                        logger.info(
                            f"{row[2]} contains invalid map location:" f"{loc}."
                        )
                        params["location_annotations"].append(loc)
                        del locations[i]
        return {"locations": locations, "chromosomes": chromosomes, "exclude": exclude}

    def _add_chromosome_location(
        self, locations: List, location_list: List, params: Dict
    ) -> None:
        """Add a chromosome location to the location list.

        :param locations: NCBI map locations for a gene record.
        :param location_list: A list to store chromosome locations.
        :param params: A transformed gene record
        """
        for i in range(len(locations)):
            loc = locations[i].strip()
            location = dict()

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
                        self._chromosome_location.set_interval_range(
                            loc, arm_ix, location
                        )
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

            chr_location = self._chromosome_location.get_location(location, params)
            if chr_location:
                location_list.append(chr_location)

    def _set_centromere_location(self, loc: str, location: Dict) -> None:
        """Set centromere location for a gene.

        :param loc: A gene location
        :param location: GA4GH location
        """
        centromere_ix = re.search("cen", loc).start()  # type: ignore
        if "-" in loc:
            # Location gives both start and end
            range_ix = re.search("-", loc).start()  # type: ignore
            if "q" in loc:
                location["chr"] = loc[:centromere_ix].strip()
                location["start"] = "cen"
                location["end"] = loc[range_ix + 1 :]
            elif "p" in loc:
                p_ix = re.search("p", loc).start()  # type: ignore
                location["chr"] = loc[:p_ix].strip()
                location["end"] = "cen"
                location["start"] = loc[:range_ix]
        else:
            location["chr"] = loc[:centromere_ix].strip()
            location["start"] = "cen"
            location["end"] = "cen"

    def _transform_data(self) -> None:
        """Modify data and pass to loading functions."""
        logger.info("Transforming NCBI...")
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

        self._get_gene_gff(db, info_genes, self.seqrepo)

        for gene in info_genes.keys():
            self._load_gene(info_genes[gene])
        logger.info("Successfully transformed NCBI.")

    def _add_meta(self) -> None:
        """Add Ensembl metadata.

        :raise NormalizerEtlError: if requisite metadata is unset
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
            raise NormalizerEtlError(
                "Source metadata unavailable -- was data properly acquired before attempting to load DB?"
            )
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
            data_license_attributes={
                "non_commercial": False,
                "share_alike": False,
                "attribution": False,
            },
            genome_assemblies=[self._assembly],
        )

        self._database.add_source_metadata(SourceName.NCBI, metadata)
