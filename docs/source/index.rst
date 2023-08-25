Gene Normalizer |version|
=========================

.. image:: https://img.shields.io/pypi/pyversions/gene-normalizer?color=gr
   :alt: PyPI - Python Version

.. image:: https://github.com/cancervariants/gene-normalization/actions/workflows/github-actions.yml/badge.svg
     :alt: tests status
     :target: https://github.com/cancervariants/gene-normalization/actions/workflows/github-actions.yml

.. image:: https://zenodo.org/badge/309797998.svg
     :alt: citation
     :target: https://zenodo.org/badge/latestdoi/309797998

The Gene Normalizer provides tools for resolving ambiguous human gene references to consistently-structured, normalized terms. For gene concepts extracted from `NCBI Gene <https://www.ncbi.nlm.nih.gov/gene/>`_, `Ensembl <https://useast.ensembl.org/index.html>`_, and `HGNC <https://www.genenames.org/>`_, it designates a `CURIE <https://en.wikipedia.org/wiki/CURIE>`_, and provides additional metadata like current and previously-used symbols, aliases, database cross-references and associations, and coordinates.

A `public REST instance of the service <https://normalize.cancervariants.org/gene>`_ is available for programmatic queries:

.. code-block:: pycon

   >>> import requests
   >>> result = requests.get("https://normalize.cancervariants.org/gene/normalize?q=braf")
   >>> gene = result.json()['gene_descriptor']
   >>> print((gene['gene_id']))
   "hgnc:1097"
   >>> print(gene['alternate_labels'])
   ['B-raf', 'NS7', 'B-RAF1', 'BRAF-1', 'BRAF1', 'RAFB1']

The Gene Normalizer can also be installed locally as a Python package for fast access:

.. code-block:: pycon

    >>> from gene.query import QueryHandler
    >>> from gene.database import create_db
    >>> q = QueryHandler(create_db())
    >>> result = q.normalize("BRAF")
    >>> result.gene_descriptor.gene_id
    "hgnc:1097"
    >>> result.gene_descriptor.alternate_labels
    ['NS7', 'RAFB1', 'B-raf', 'BRAF-1', 'BRAF1', 'B-RAF1']

The Gene Normalizer was created to support the `Knowledgebase Integration Project <https://cancervariants.org/projects/integration/>`_ of the `Variant Interpretation for Cancer Consortium (VICC) <https://cancervariants.org/>`_. It is developed primarily by the `Wagner Lab <https://www.nationwidechildrens.org/specialties/institute-for-genomic-medicine/research-labs/wagner-lab>`_. Full source code is available on `GitHub <https://github.com/cancervariants/gene-normalization>`_.

.. toctree::
   :hidden:
   :maxdepth: 2

    Installation<install>
    Usage<usage>
    Normalizing data<normalizing_data/index>
    Managing data<managing_data/index>
    API<api/api>
    Contributing<contributing>
    License<license>
