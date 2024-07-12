"""Generate normalized concept graph figure.

Executing this should be straightforward. Given an available Gene Normalizer database,
just call like so: ::
    python3 docs/scripts/generate_normalize_figure.py

Embeddable HTML for the normalization figure should be deposited in the correct
location, within docs/source/_static/html/.
"""  # noqa: INP001

import json

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


def create_gjgf(result: UnmergedNormalizationService) -> dict:
    """Create gravis input.

    :param result: result from Unmerged Normalization search
    """
    graph = {
        "graph": {
            "label": "tmp",
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

    for i, (_, matches) in enumerate(result.source_matches.items()):
        for match in matches.records:
            graph["graph"]["nodes"][match.concept_id] = {
                "metadata": {
                    "color": COLORS[i],
                    "hover": f"{match.concept_id}\n{match.symbol}\n<i>{match.label}</i>",
                    "click": f"<p color='black'>{json.dumps(match.model_dump(), indent=2)}</p>",
                }
            }
            for xref in match.xrefs:
                graph["graph"]["edges"].append(
                    {"source": match.concept_id, "target": xref}
                )

    included_edges = [
        edge
        for edge in graph["graph"]["edges"]
        if (
            edge["target"] in graph["graph"]["nodes"]
            and edge["source"] in graph["graph"]["nodes"]
        )
    ]

    graph["graph"]["edges"] = included_edges

    included_nodes = {k["source"] for k in graph["graph"]["edges"]}.union(
        {k["target"] for k in graph["graph"]["edges"]}
    )
    new_nodes = {
        key: value
        for key, value in graph["graph"]["nodes"].items()
        if key in included_nodes
    }
    graph["graph"]["nodes"] = new_nodes

    return graph


def gen_norm_figure() -> None:
    """Generate normalized graph figure for docs."""
    q = QueryHandler(create_db())

    otx2p1 = "OTX2P1"
    otx2p2 = "OTX2P2"

    otx2p1_result = q.normalize_unmerged(otx2p1)
    otx2p2_result = q.normalize_unmerged(otx2p2)

    otx2p1_graph = create_gjgf(otx2p1_result)
    otx2p2_graph = create_gjgf(otx2p2_result)

    nodes = otx2p1_graph["graph"]["nodes"]
    nodes.update(otx2p2_graph["graph"]["nodes"])

    graph = {
        "graph": {
            "label": f"Reference network for {otx2p1} and {otx2p2}",
            "metadata": otx2p1_graph["graph"]["metadata"],
            "nodes": nodes,
            "edges": otx2p1_graph["graph"]["edges"] + otx2p2_graph["graph"]["edges"],
        }
    }

    fig = gv.d3(
        data=graph,
        graph_height=250,
        node_hover_neighborhood=True,
        node_label_font="arial",
    )
    fig.export_html(
        (
            APP_ROOT.parents[0]
            / "docs"
            / "source"
            / "_static"
            / "html"
            / "normalize_example.html"
        ).absolute(),
        overwrite=True,
    )


if __name__ == "__main__":
    gen_norm_figure()
