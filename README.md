<h1 align="center">
Gene Normalizer
</h1>

[![image](https://img.shields.io/pypi/v/gene-normalizer.svg)](https://pypi.python.org/pypi/gene-normalizer) [![image](https://img.shields.io/pypi/l/gene-normalizer.svg)](https://pypi.python.org/pypi/gene-normalizer) [![image](https://img.shields.io/pypi/pyversions/gene-normalizer.svg)](https://pypi.python.org/pypi/gene-normalizer) [![Actions status](https://github.com/cancervariants/gene-normalization/actions/workflows/checks.yaml/badge.svg)](https://github.com/cancervariants/gene-normalization/actions/workflows/checks.yaml) [![DOI](https://zenodo.org/badge/309797998.svg)](https://zenodo.org/badge/latestdoi/309797998)

## Overview
<!-- description -->
The Gene Normalizer provides tools for resolving ambiguous human gene references to consistently-structured, normalized terms. For gene concepts extracted from [NCBI Gene](https://www.ncbi.nlm.nih.gov/gene/), [Ensembl](https://useast.ensembl.org/index.html), and [HGNC](https://www.genenames.org/), it designates a [CURIE](https://en.wikipedia.org/wiki/CURIE), and provides additional metadata like current and previously-used symbols, aliases, database cross-references and associations, and coordinates.
<!-- /description -->
---

**[Live service](https://normalize.cancervariants.org/gene)**

**[Documentation](https://gene-normalizer.readthedocs.io/latest/)** · [Installation](https://gene-normalizer.readthedocs.io/latest/install.html) · [Usage](https://gene-normalizer.readthedocs.io/latest/usage.html) · [API reference](https://gene-normalizer.readthedocs.io/latest/api/index.html)

---

## Install

The Gene Normalizer is available on [PyPI](https://pypi.org/project/gene-normalizer/):

```shell
python3 -m pip install gene-normalizer
```

See [installation instruction](https://gene-normalizer.readthedocs.io/latest/install.html) in the documentation for a description of installation options and data setup requirements.

## Examples

Use the [live service](https://normalize.cancervariants.org/gene) to programmatically normalize gene terms, as in the following truncated example:

```shell
$ curl 'https://normalize.cancervariants.org/gene/normalize?q=BRAF' | python -m json.tool
{
    "query": "BRAF",
    "match_type": 100,
    "gene": {
        "conceptType": "Gene",
        "id": "normalize.gene.hgnc:1097"
        "primaryCoding": {
            "id": "hgnc:1097",
            "code": "HGNC:1097",
            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
        },
        "name": "BRAF",
        "extensions": [
            {
                "name": "aliases",
                "value": [
                    "BRAF1",
                    "B-RAF1",
                    "NS7",
                    "RAFB1",
                    "B-raf",
                    "BRAF-1"
                ]
            }
        ]
    }
    # ...
}
```

Or utilize the [Python API](https://gene-normalizer.readthedocs.io/latest/api/query_api.html) for fast access:

```python
>>> from gene.database import create_db
>>> from gene.query import QueryHandler
>>> q = QueryHandler(create_db())
>>> result = q.normalize("KRAS")
>>> result.gene.primaryCoding.id
'hgnc:6407'
```

See the [usage](https://gene-normalizer.readthedocs.io/latest/usage.html) and [normalization](https://gene-normalizer.readthedocs.io/latest/normalizing_data/normalization.html) entries in the documentation for more.

## Feedback and contributing

We welcome bug reports, feature requests, and code contributions from users and interested collaborators. The [documentation](https://gene-normalizer.readthedocs.io/latest/contributing.html) contains guidance for submitting feedback and contributing new code.
