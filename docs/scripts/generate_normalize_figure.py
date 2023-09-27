"""Generate normalized concept graph figure.

Executing this should be straightforward. Given an available Gene Normalizer database,
just call like so: ::
    python3 docs/scripts/generate_normalize_figure.py

Embeddable HTML for the normalization figure should be deposited in the correct
location, at docs/source/_static/html/normalize_her2.html.
"""
import json
from typing import Dict

import gravis as gv

from gene import APP_ROOT
from gene.database import create_db
from gene.query import QueryHandler
from gene.schemas import UnmergedNormalizationService

COLORS = [
    "#F8766D",
    "#00BA38",
    "#00B9E3",
]

GENE = "OTX2P1"


def create_gjgf(result: UnmergedNormalizationService) -> Dict:
    """Create gravis input.

    :param result: result from Unmerged Normalization search
    """
    graph = {
        "graph": {
            "label": f"Reference Network for Search Term '{GENE}'",
            "nodes": {},
            "edges": [],
            "metadata": {
                "arrow_size": 15,
                "node_size": 15,
                "node_label_size": 20,
                "edge_size": 2,
            },
        }
    }

    for i, (source, matches) in enumerate(result.source_matches.items()):
        for match in matches.records:
            graph["graph"]["nodes"][match.concept_id] = {
                "metadata": {
                    "color": COLORS[i],
                    "hover": f"{match.concept_id}\n{match.symbol}\n<i>{match.label}</i>",  # noqa: E501
                    "click": f"<p color='black'>{json.dumps(match.model_dump(), indent=2)}</p>",  # noqa: E501
                }
            }
            for xref in match.xrefs:
                graph["graph"]["edges"].append(
                    {"source": match.concept_id, "target": xref}
                )

    included_edges = []
    for edge in graph["graph"]["edges"]:
        if (
            edge["target"] in graph["graph"]["nodes"]
            and edge["source"] in graph["graph"]["nodes"]
        ):
            included_edges.append(edge)
    graph["graph"]["edges"] = included_edges

    included_nodes = {k["source"] for k in graph["graph"]["edges"]}.union(
        {k["target"] for k in graph["graph"]["edges"]}
    )
    new_nodes = {}
    for key, value in graph["graph"]["nodes"].items():
        if key in included_nodes:
            new_nodes[key] = value
    graph["graph"]["nodes"] = new_nodes

    return graph


def gen_norm_figure() -> None:
    """Generate normalized graph figure for docs."""
    q = QueryHandler(create_db())
    result = q.normalize_unmerged(GENE)

    graph = create_gjgf(result)

    fig = gv.d3(
        data=graph,
        graph_height=200,
        node_hover_neighborhood=True,
        use_links_force=True,
        links_force_distance=0.01,
        links_force_strength=0.01,
        node_label_font="arial",
    )
    fig.export_html(
        (
            APP_ROOT.parents[0]
            / "docs"
            / "source"
            / "_static"
            / "html"
            / f"normalize_{GENE.lower()}.html"
        ).absolute(),  # noqa: E501
        overwrite=True,
    )


if __name__ == "__main__":
    gen_norm_figure()
