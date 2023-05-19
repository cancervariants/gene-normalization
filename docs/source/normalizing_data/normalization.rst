Normalization
=============

Overview
--------

The Gene Normalizer extracts gene descriptions and related metadata from curated knowledge sources and stores them as gene records. Once stored, it also provides a mapping from each gene record to a normalized gene concept, and produced a combined record for that concept.

Basic information model
-----------------------

Data resources, such as NCBI Gene, HGNC, and Ensembl, provide descriptions of individual genes, which we refer to as *records*. Our normalization routines construct mappings between those records and individual normalized concepts. Those concepts are abstract representations of "true" unique entities that exist on the genome. By combining the normalized concept with its associated source records to produce a *normalized record*, we are able to provide a more comprehensive description of individual genes.

The gene record
---------------

The `gene.etl` package contains classes for extracting relevant data for each source record. The `gene.schemas.BaseGene` class demonstrates the kinds of information that the ETL methods attempt to acquire:

.. autoclass:: gene.schemas.BaseGene
   :members:
   :undoc-members:
   :show-inheritance:

.. _build_normalization:

Building normalized concepts and records
----------------------------------------

Once all source records have been loaded into the database, normalized concept construction proceeds by grouping source records according to cross-references. For example, HGNC identifies Orthodenticle Homeobox 2 Pseudogene 1, or OTX2P1, as ``hgnc:33281``. The HGNC record also contains cross-references to ``ncbigene:100033409`` and ``ensembl:ENSG000000234644``. From this, the Gene Normalizer is able to produce a concept group containing each of these records:

.. raw:: html
   :file: ../_static/html/normalize_otx2p1.html

In practice, gene curation by these sources is rich and thorough, and most gene records in each source contain cross-reference to the corresponding records in the other sources. However, for normalized concept generation, it is sufficient for any record to be included in a normalized concept grouping if there is at least one cross-reference, in either direction, joining it to the rest of the concept group.

After grouping is complete, a concept ID for each normalized concept is selected from the record from the highest-priority source in each group. The SourcePriority class defines this priority ranking:

.. autoclass:: gene.schemas.SourcePriority
    :members:
    :undoc-members:
    :show-inheritance:

Normalized gene records are constructed by merging known data from all associated gene records. For array-like fields (e.g. aliases, cross-references to entries in other data sources), data from all sources are simply combined. For scalar-like fields (e.g. the gene's symbol), the value is selected from an individual source record according to the priority assigned to the source.

Normalized records are structured as `Gene Descriptors <https://vrsatile.readthedocs.io/en/latest/>`_ in conformance with the `GA4GH VRSATILE Standard <https://vrsatile.readthedocs.io/en/latest/>`_. The normalized gene concept is provided as a value object, and additional metadata is deposited as a label, xrefs, alternate labels, as well as Extensions for more complex information (such as loci and gene type).