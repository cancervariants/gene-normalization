"""Provide useful utilities."""

import logging
from collections.abc import Generator
from logging.handlers import RotatingFileHandler

from gene.database import AbstractDatabase
from gene.schemas import RecordType, SourceName


def initialize_logs(log_level: int = logging.INFO) -> None:
    """Configure logging.

    :param log_level: app log level to set
    """
    root = logging.getLogger()
    if root.handlers:
        return

    root.setLevel(log_level)
    formatter = logging.Formatter(
        "[%(asctime)s] - %(name)s - %(levelname)s : %(message)s"
    )
    fh = RotatingFileHandler(f"{__package__}.log", maxBytes=5_000_000, backupCount=3)
    fh.setFormatter(formatter)
    root.addHandler(fh)


def get_term_mappings(
    database: AbstractDatabase,
    scope: RecordType | SourceName,
    protein_coding_only: bool = False,
) -> Generator[dict, None, None]:
    """Produce dict objects for known concepts (name + ID) plus other possible referents

    Use in downstream applications such as autocompletion.

    :param database: instance of DB connection to get records from
    :param scope: constrain record scope, either to a kind of record or to a specific source
    :param protein_coding_only: whether to constrain just to protein coding genes
    :return: Generator yielding mapping objects
    """
    if isinstance(scope, SourceName):
        record_type = RecordType.IDENTITY
        src_name = scope
    elif isinstance(scope, RecordType):
        record_type = scope
        src_name = None
    else:
        raise TypeError

    protein_coding_gene_types = {
        "gene with protein product",  # HGNC
        "protein-coding",  # NCBI
        "protein_coding",  # Ensembl
    }
    for record in database.get_all_records(record_type=record_type):
        if src_name and record["src_name"] != src_name:
            continue
        if protein_coding_only and (
            (
                record_type == RecordType.IDENTITY
                and record.get("gene_type") not in protein_coding_gene_types
            )
            or (
                record_type == RecordType.MERGER
                and (
                    "ensembl_biotype" not in record
                    or record.get("ensembl_biotype") == "protein_coding"
                )
                and (
                    "ncbi_gene_type" not in record
                    or record["ncbi_gene_type"] == "protein_coding"
                )
                and (
                    "hgnc_locus_type" not in record
                    or record["hgnc_locus_type"] == "gene with protein product"
                )
            )
        ):
            continue

        yield {
            "concept_id": record["concept_id"],
            "symbol": record["symbol"],
            "label": record.get("label"),
            "aliases": record.get("aliases", []),
            "xrefs": record.get("xrefs", []) + record.get("associated_with", []),
            "previous_symbols": record.get("previous_symbols", []),
        }
