from pathlib import Path

from wags_tails import NcbiGeneData, NcbiGeneSummaryData, NcbiGenomeData

KEEP_GENE_IDS = {
    "25",
    "43",
    "290",
    "293",
    "673",
    "8193",
    "4625",
    "7637",
    "9646",
    "10036",
    "10251",
    "25782",
    "30849",
    "54704",
    "403313",
    "104793947",
    "106783576",
    # discontinued
    "544580",
    "103344718",
}
NCBI_DATA_PATHS, _ = NcbiGeneData().get_latest()

### Gene summary file

INPUT_SUMMARY_TSV, _ = NcbiGeneSummaryData().get_latest()
OUTPUT_SUMMARY_TSV = (
    Path(__file__).resolve().parent.parent / "etl_data" / INPUT_SUMMARY_TSV.name
)

with INPUT_SUMMARY_TSV.open() as fin, OUTPUT_SUMMARY_TSV.open("w") as fout:
    header = next(fin)
    fout.write(header)

    for line in fin:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 2 and parts[0] == "9606" and parts[1] in KEEP_GENE_IDS:
            fout.write(line)

### Gene info file

INPUT_INFO_FILE = NCBI_DATA_PATHS.gene_info
OUTPUT_INFO_FILE = (
    Path(__file__).resolve().parent.parent / "etl_data" / INPUT_INFO_FILE.name
)

with INPUT_INFO_FILE.open() as fin, OUTPUT_INFO_FILE.open("w") as fout:
    header = next(fin)
    fout.write(header)

    for line in fin:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 2 and parts[0] == "9606" and parts[1] in KEEP_GENE_IDS:
            fout.write(line)

### Gene features file

INPUT_GFF, _ = NcbiGenomeData().get_latest()
OUTPUT_GFF = Path(__file__).resolve().parent.parent / "etl_data" / INPUT_GFF.name


def extract_gene_id(attr: str) -> str | None:
    for field in attr.split(";"):
        if field.startswith("Dbxref"):
            for xref in field.split("=")[1].split(","):
                if xref.startswith("GeneID"):
                    return xref.split(":")[1]
    return None


with INPUT_GFF.open() as fin, OUTPUT_GFF.open("w") as fout:
    for line in fin:
        # skip sequence-region/species
        if line.startswith(("##sequence-region", "##species")):
            continue

        # keep header/comments as-is
        if line.startswith("#"):
            fout.write(line)
            continue

        parts = line.rstrip("\n").split("\t")
        if len(parts) < 9:
            continue  # skip malformed lines

        if parts[8].startswith("ID=NC_"):
            fout.write(line)
            continue

        if not parts[8].startswith("ID=gene"):
            continue

        gene_id = extract_gene_id(parts[8])
        if gene_id in KEEP_GENE_IDS:
            fout.write(line)

### Gene history file

INPUT_HISTORY_FILE = NCBI_DATA_PATHS.gene_history
OUTPUT_HISTORY_FILE = (
    Path(__file__).resolve().parent.parent / "etl_data" / INPUT_HISTORY_FILE.name
)

with INPUT_HISTORY_FILE.open() as fin, OUTPUT_HISTORY_FILE.open("w") as fout:
    header = next(fin)
    fout.write(header)

    for line in fin:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3 and (parts[1] in KEEP_GENE_IDS or parts[2] in KEEP_GENE_IDS):
            fout.write(line)
