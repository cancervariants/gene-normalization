# Gene Normalizer {{ config.extra.version }}

[![image](https://img.shields.io/pypi/v/gene-normalizer.svg)](https://pypi.python.org/pypi/gene-normalizer) [![image](https://img.shields.io/pypi/l/gene-normalizer.svg)](https://pypi.python.org/pypi/gene-normalizer) [![image](https://img.shields.io/pypi/pyversions/gene-normalizer.svg)](https://pypi.python.org/pypi/gene-normalizer) [![Actions status](https://github.com/cancervariants/gene-normalization/actions/workflows/checks.yaml/badge.svg)](https://github.com/cancervariants/gene-normalization/actions/workflows/checks.yaml) [![DOI](https://zenodo.org/badge/309797998.svg)](https://zenodo.org/badge/latestdoi/309797998)


The Gene Normalizer provides tools for resolving ambiguous human gene references to consistently-structured, normalized terms. For gene concepts extracted from [NCBI Gene](https://www.ncbi.nlm.nih.gov/gene/), [Ensembl](https://useast.ensembl.org/index.html), and [HGNC](https://www.genenames.org/), it designates a [CURIE](https://en.wikipedia.org/wiki/CURIE), and provides additional metadata like current and previously-used symbols, aliases, database cross-references and associations, and coordinates.

A [public REST instance of the service](https://normalize.cancervariants.org/gene) is available for programmatic queries:

```pycon
>>> import requests
>>> result = requests.get("https://normalize.cancervariants.org/gene/normalize?q=braf").json()
>>> result["gene"]["primaryCoding"]["id"]
'hgnc:1097'
>>> next(ext for ext in result["gene"]["extensions"] if ext["name"] == "aliases")["value"]
['B-raf', 'NS7', 'B-RAF1', 'BRAF-1', 'BRAF1', 'RAFB1']
```

The Gene Normalizer can also be installed locally as a Python package for fast access:

```pycon
>>> from gene.query import QueryHandler
>>> from gene.database import create_db
>>> q = QueryHandler(create_db())
>>> result = q.normalize("BRAF")
>>> result.gene.primaryCoding.id
'hgnc:1097'
>>> next(ext for ext in result.gene.extensions if ext.name == "aliases").value
['B-raf', 'NS7', 'B-RAF1', 'BRAF-1', 'BRAF1', 'RAFB1']
```

The Gene Normalizer was created to support the [Knowledgebase Integration Project](https://cancervariants.org/projects/integration/) of the [Variant Interpretation for Cancer Consortium (VICC)](https://cancervariants.org/). It is developed primarily by the [Wagner Lab](https://www.nationwidechildrens.org/specialties/institute-for-genomic-medicine/research-labs/wagner-lab). Full source code is available on [GitHub](https://github.com/cancervariants/gene-normalization).
