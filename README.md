<h1 align="center">
Gene Normalizer
</h1>

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gene-normalizer?color=gr) [![tests](https://github.com/cancervariants/gene-normalization/actions/workflows/github-actions.yml/badge.svg)](https://github.com/cancervariants/gene-normalization/actions/workflows/github-actions.yml) [![DOI](https://zenodo.org/badge/309797998.svg)](https://zenodo.org/badge/latestdoi/309797998)

## Overview
<!-- description -->
The Gene Normalizer provides tools for resolving ambiguous human gene references to consistently-structured, normalized terms. For gene concepts extracted from [NCBI Gene](https://www.ncbi.nlm.nih.gov/gene/), [Ensembl](https://useast.ensembl.org/index.html), and [HGNC](https://www.genenames.org/), it designates a [CURIE](https://en.wikipedia.org/wiki/CURIE), and provides additional metadata like current and previously-used symbols, aliases, database cross-references, and coordinates.
<!-- /description -->
---

**[Live service](https://normalize.cancervariants.org/gene)**

**[Documentation](https://gene-normalizer.readthedocs.io/en/latest/)** · [Installation](https://gene-normalizer.readthedocs.io/en/latest/install.html) · [Usage](https://gene-normalizer.readthedocs.io/en/latest/usage.html) · [API reference](https://gene-normalizer.readthedocs.io/en/latest/api/api.html)

---

## Install

The Gene Normalizer is available on [PyPI](https://pypi.org/project/gene-normalizer/):

```shell
python3 -m pip install gene-normalizer
```

See [installation instruction](https://gene-normalizer.readthedocs.io/en/latest/install.html) in the documentation for a description of installation options and data setup requirements.

## Examples

Use the [live service](https://normalize.cancervariants.org/gene) to programmatically normalize gene terms, as in the following truncated example:

```shell
$ curl 'https://normalize.cancervariants.org/gene/normalize?q=BRAF' | python -m json.tool
{
    "query": "BRAF",
    "match_type": 100,
    "normalized_id": "hgnc:1097",
    "gene": {
        "type": "Gene",
        "id": "normalize.gene.hgnc:1097"
        "label": "BRAF",
        "gene_id": "hgnc:1097",
        "aliases": [
            "BRAF1",
            "B-RAF1",
            "NS7",
            "RAFB1",
            "B-raf",
            "BRAF-1"
        ]
    }
    # ...
}
```

Or utilize the [Python API](https://gene-normalizer.readthedocs.io/en/latest/api/query_api.html) for fast access:

```python
>>> from gene.database import get_db
>>> from gene.query import QueryHandler
>>> q = QueryHandler(get_db())
>>> result = q.normalize("KRAS")
>>> result.normalized_id
'hgnc:6407'
```

See the [usage](https://gene-normalizer.readthedocs.io/en/latest/usage.html) and [normalization](https://gene-normalizer.readthedocs.io/en/latest/normalizing_data/normalization.html) entries in the documentation for more.

## Feedback and contributing

We welcome bug reports, feature requests, and code contributions from users and interested collaborators. The [documentation](https://gene-normalizer.readthedocs.io/en/latest/contributing.html) contains guidance for submitting feedback and contributing new code.
