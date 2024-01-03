"""Defines ETL methods for the NCBI data source."""
import csv
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

import click
import gffpandas.gffpandas as gffpd
import pandas as pd
from tqdm import tqdm
from wags_tails import NcbiGenomeData
from wags_tails.ncbi import NcbiGenePaths

from gene.database import AbstractDatabase
from gene.etl.base import SEQREPO_ROOT_DIR, Base, GeneNormalizerEtlError
from gene.schemas import (
    PREFIX_LOOKUP,
    Annotation,
    Chromosome,
    DataLicenseAttributes,
    NamespacePrefix,
    SourceMeta,
    SourceName,
    StoredSequenceLocation,
    SymbolStatus,
)

_logger = logging.getLogger(__name__)


class NCBI(Base):
    """ETL class for NCBI source"""

    def __init__(
        self,
        database: AbstractDatabase,
        seqrepo_dir: Path = SEQREPO_ROOT_DIR,
        data_path: Optional[Path] = None,
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
        _logger.info(f"Gathering {self._src_name} data...")
        self._gff_src, self._assembly = self._genome_data_handler.get_latest(
            from_local=use_existing
        )
        gene_paths: NcbiGenePaths
        gene_paths, self._version = self._data_source.get_latest(
            from_local=use_existing
        )  # type: ignore
        self._info_src = gene_paths.gene_info
        self._history_src = gene_paths.gene_history
        self._gene_url = "ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz"
        self._history_url = "ftp.ncbi.nlm.nih.gov/gene/DATA/gene_history.gz"
        self._assembly_url = "ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/"
        _logger.info(
            f"Acquired data for {self._src_name}: {self._gff_src}, {self._info_src}, {self._history_src}"
        )

    def _get_prev_symbols(self) -> Dict[str, str]:
        """Store a gene's symbol history.

        :return: A dictionary of a gene's previous symbols
        """
        # get symbol history
        length = sum(1 for _ in csv.reader(open(self._history_src, "r")))
        with open(self._history_src, "r") as history_file:
            history = csv.reader(history_file, delimiter="\t")
            next(history)
            prev_symbols = {}
            if not self._silent:
                click.echo(f"Gathering previous symbols from {self._history_src}")
            for row in tqdm(history, total=length, ncols=80, disable=self._silent):
                if row[0] != "9606":
                    continue  # humans only
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
        return prev_symbols

    def _add_xrefs(self, val: List[str], params: Dict) -> None:
        """Add xrefs to a transformed gene.

        :param val: A list of source ids for a given gene
        :param params: A transformed gene record (modified in place)
        """
        params["xrefs"] = []
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
                    _logger.info(f"{src_name} is not in NameSpacePrefix.")
                    continue
                params["xrefs"].append(f"{prefix}:{src_id}")
        if not params["xrefs"]:
            del params["xrefs"]

    def _get_gene_info(self, prev_symbols: Dict[str, str]) -> Dict[str, Dict]:
        """Store genes from NCBI info file.

        :param prev_symbols: A dictionary of a gene's previous symbols
        :return: A dictionary of genes from the NCBI info file.
        """
        length = sum(1 for _ in csv.reader(open(self._info_src, "r")))

        info_genes = {}
        with open(self._info_src, "r") as info_file:
            info = csv.reader(info_file, delimiter="\t")
            next(info)

            if not self._silent:
                click.echo(f"Extracting genes from {self._info_src}")
            for row in tqdm(info, total=length, ncols=80, disable=self._silent):
                params: Dict[str, Any] = {
                    "concept_id": f"{NamespacePrefix.NCBI.value}:{row[1]}",
                    "symbol": row[2],
                }

                # get aliases
                if row[4] != "-":
                    params["aliases"] = row[4].split("|")
                else:
                    params["aliases"] = []
                # get xrefs
                if row[5] != "-":
                    xrefs = row[5].split("|")
                    self._add_xrefs(xrefs, params)
                # get chromosome location
                try:
                    vrs_chr_location = self._get_vrs_chr_location(row, params)
                except ValueError:
                    # Exclude genes with multiple distinct locations (e.g. OMS)
                    pass
                else:
                    if vrs_chr_location:
                        params["locations"] = vrs_chr_location
                # get label
                if row[8] != "-":
                    params["label"] = row[8]
                # add prev symbols
                if row[1] in prev_symbols.keys():
                    params["previous_symbols"] = prev_symbols[row[1]]
                # get type
                params["gene_type"] = row[9]

                info_genes[params["symbol"]] = params
        return info_genes

    def _build_sequence_location(
        self, seq_id: str, row: pd.Series, concept_id: str
    ) -> Optional[StoredSequenceLocation]:
        """Construct a sequence location for storing in a DB.

        :param seq_id: The sequence ID.
        :param row: A gene from the source file.
        :param concept_id: record ID from source
        :return: A storable SequenceLocation containing relevant params for returning a
        VRS SequenceLocation, or None if unable to retrieve valid parameters
        """
        aliases = self._get_seq_id_aliases(seq_id)
        if not aliases or row.start is None or row.end is None:
            return None

        sequence = aliases[0]

        if row.start != "." and row.end != "." and sequence:
            if 0 <= row.start <= row.end:
                return StoredSequenceLocation(
                    start=row.start - 1,
                    end=row.end,
                    sequence_id=sequence,
                )
            else:
                _logger.warning(
                    f"{concept_id} has invalid interval: start={row.start - 1} end={row.end}"
                )

    def _get_gene_gff(self, df: pd.DataFrame, info_genes: Dict) -> None:
        """Store genes from NCBI gff file.

        :param db: GFF database
        :param info_genes: A dictionary of gene's from the NCBI info file.
        """
        genes_df = df[df["ID"].str.startswith("gene", na=False)]
        if not self._silent:
            click.echo(f"Extracting genes from {self._info_src}")
        for _, row in tqdm(
            genes_df.iterrows(), total=genes_df.shape[0], ncols=80, disable=self._silent
        ):
            symbol = row.Name
            if symbol in info_genes:
                params = info_genes[symbol]
                vrs_sq_location = self._build_sequence_location(
                    row.seq_id, row, params["concept_id"]
                )
                if vrs_sq_location:
                    params["locations"].append(vrs_sq_location)
            else:
                gene = self._add_gff_gene(row)
                if gene:
                    info_genes[gene["symbol"]] = gene

    def _add_gff_gene(self, row: pd.Series) -> Optional[Dict]:
        """Create a transformed gene recor from NCBI gff file.

        :param row: A gene from the gff data file
        :return: A gene dictionary if the ID attribute exists. Else return None.
        """
        params = dict()
        self._add_attributes(row, params)
        sq_loc = self._build_sequence_location(row.seq_id, row, params["concept_id"])
        if sq_loc:
            params["locations"] = [sq_loc]
        else:
            params["locations"] = list()
        return params

    def _add_attributes(self, row: pd.Series, gene: Dict) -> None:
        """Add concept_id, symbol, and xrefs to a gene record.

        :param row: gene record from GFF file
        :param gene: in-progress gene object
        """
        gene["symbol"] = row.ID[5:]
        if row.Dbxref:
            xrefs = []
            for split_ref in row.Dbxref.split(","):
                if split_ref.startswith("GeneID"):
                    gene[
                        "concept_id"
                    ] = f"{NamespacePrefix.NCBI.value}:{split_ref.split(':')[1]}"
                else:
                    xref = self._get_xref(split_ref)
                    if xref:
                        xrefs.append(xref)
            gene["xrefs"] = xrefs
        if row.description:
            gene["label"] = unquote(row.description)

    def _get_xref(self, raw_xref: str) -> Optional[str]:
        """Get xref.

        :param raw_xref:
        :return: an xref
        """
        for prefix, constrained_prefix in (
            ("HGNC", NamespacePrefix.HGNC),
            ("UniProt", NamespacePrefix.UNIPROT),
            ("miRBase", NamespacePrefix.MIRBASE),
            ("RFAM", NamespacePrefix.RFAM),
        ):
            if raw_xref.startswith(prefix):
                src_id = raw_xref.split(":")[-1]
                return f"{constrained_prefix.value}:{src_id}"
        _logger.warning("Unrecognized source name: %s", raw_xref)
        return None

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
        :raise ValueError: if gene contains multiple distinct locations
        """
        chromosomes = None
        if row[6] != "-":
            if "|" in row[6]:
                chromosomes = row[6].split("|")
            else:
                chromosomes = [row[6]]

            if len(chromosomes) >= 2:
                if chromosomes and "X" not in chromosomes and "Y" not in chromosomes:
                    _logger.info(
                        f"{row[2]} contains multiple distinct "
                        f"chromosomes: {chromosomes}."
                    )
                    chromosomes = None

        locations = None
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
                _logger.info(
                    f"{row[2]} contains multiple distinct locations: {locations}."
                )
                locations = None
                raise ValueError

            # NCBI sometimes contains invalid map locations
            if locations:
                for i in range(len(locations)):
                    loc = locations[i].strip()
                    if not re.match("^([1-9][0-9]?|X[pq]?|Y[pq]?)", loc):
                        _logger.info(f"{row[2]} contains invalid map location: {loc}.")
                        params["location_annotations"].append(loc)
                        del locations[i]
        return {"locations": locations, "chromosomes": chromosomes}

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

            # chr_location = self._get_chromosome_location(location, params)
            # if chr_location:
            #     location_list.append(chr_location)

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
        _logger.info("Transforming NCBI data...")
        prev_symbols = self._get_prev_symbols()
        info_genes = self._get_gene_info(prev_symbols)

        df = gffpd.read_gff3(self._gff_src).attributes_to_columns()
        self._get_gene_gff(df, info_genes)

        if not self._silent:
            click.echo("Loading completed gene objects...")
        for gene in tqdm(
            info_genes.values(), total=len(info_genes), disable=self._silent, ncols=80
        ):
            self._load_gene(gene)
        _logger.info("NCBI data transform complete.")

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
            raise GeneNormalizerEtlError(
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
            data_license_attributes=DataLicenseAttributes(
                non_commercial=False,
                share_alike=False,
                attribution=False,
            ),
            genome_assemblies=[self._assembly],
        )

        self._database.add_source_metadata(SourceName.NCBI, metadata)
