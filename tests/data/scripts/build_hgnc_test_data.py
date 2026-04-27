import json
from pathlib import Path

from wags_tails import HgncData

INPUT_JSON, _ = HgncData().get_latest()
OUTPUT_JSON = Path(__file__).resolve().parent.parent / "etl_data" / INPUT_JSON.name

KEEP_HGNC_IDS = {
    "HGNC:108",
    "HGNC:1097",
    "HGNC:11998",
    "HGNC:1838",
    "HGNC:1910",
    "HGNC:23170",
    "HGNC:2435",
    "HGNC:30005",
    "HGNC:31102",
    "HGNC:34692",
    "HGNC:36026",
    "HGNC:37133",
    "HGNC:37528",
    "HGNC:4059",
    "HGNC:4101",
    "HGNC:4641",
    "HGNC:500",
    "HGNC:7409",
    "HGNC:76",
    "HGNC:7603",
    "HGNC:8982",
    "HGNC:3829",
    "HGNC:5447",
}


with INPUT_JSON.open() as f:
    data = json.load(f)

docs = data.get("response", {}).get("docs", [])

filtered_docs = [doc for doc in docs if doc.get("hgnc_id") in KEEP_HGNC_IDS]

data["response"]["docs"] = filtered_docs
data["response"]["numFound"] = len(filtered_docs)

with OUTPUT_JSON.open("w") as f:
    json.dump(data, f, indent=2)
