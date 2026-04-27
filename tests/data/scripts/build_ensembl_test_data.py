from pathlib import Path

from wags_tails import EnsemblData

INPUT_GFF, _ = EnsemblData().get_latest()
OUTPUT_GFF = Path(__file__).resolve().parent.parent / "etl_data" / INPUT_GFF.name

KEEP_GENES = {
    "ENSG00000223972",
    "ENSG00000118873",
    "ENSG00000283502",
    "ENSG00000196455",
    "ENSG00000087085",
    "ENSG00000157764",
    "ENSG00000097007",
    "ENSG00000198730",
    "ENSG00000166825",
    "ENSG00000141510",
    "ENSG00000272920",
    "ENSG00000167670",
    "ENSG00000197180",
    "ENSG00000168939",
}


def extract_gene_id(attr: str) -> str | None:
    """
    Extract ENSG ID from attributes field like:
    ID=gene:ENSG00000168939;...
    """
    for field in attr.split(";"):
        if field.startswith("ID=gene:"):
            return field.split(":", 1)[1]
    return None


with INPUT_GFF.open() as fin, OUTPUT_GFF.open("w") as fout:
    for line in fin:
        # keep header/comments as-is
        if line.startswith("#") and line != "###\n":
            fout.write(line)
            continue

        parts = line.rstrip("\n").split("\t")
        if len(parts) < 9:
            continue  # skip malformed lines

        if parts[1] == "GRCh38" and parts[2] == "chromosome":
            fout.write(line)
            continue

        gene_id = extract_gene_id(parts[8])
        if gene_id in KEEP_GENES:
            fout.write(line)
