Normalization
=============

Overview
--------

The Gene Normalizer extracts gene descriptions and related metadata from curated knowledge sources and stores them as gene records. Once stored, it also provides a mapping from each gene record to a normalized gene concept, and produced a combined record for that concept.

Basic information model
-----------------------

Data resources, such as NCBI Gene, HGNC, and Ensembl, provide descriptions of individual genes, which we refer to as *records*. Our normalization routines construct mappings between those records and individual normalized concepts. Those concepts are abstract representations of "true" unique entities that exist on the genome. By combining the normalized concept with its associated source records to produce a *normalized record*, we are able to provide a more comprehensive description of individual genes.

.. _gene-record-object:

The gene record
---------------

The ``gene.etl`` package contains classes for extracting relevant data for each source record. The ``gene.schemas.BaseGene`` class demonstrates the kinds of information that the ETL methods attempt to acquire from each source:

.. autoclass:: gene.schemas.BaseGene
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:
   :exclude-members:  model_config, model_fields

.. _build_normalization:

Building normalized concepts and records
----------------------------------------

Once all source records have been loaded into the database, normalized concept construction proceeds by grouping source records according to cross-references. Consider the following records referring to genes OTX2P1 and OTX2P2:

* The NCBI record for OTX2P1, ``ncbigene:100033409``, references HGNC record ``hgnc:33281``
* The HGNC record for OTX2P1, ``hgnc:33281``, references Ensembl record ``ensembl:ENSG00000234644``
* The NCBI record for OTX2P2, ``ncbigene:100419816``, references both HGNC record ``hgnc:54560`` and Ensembl record ``ensembl:ENSG00000227134``
* The HGNC record for OTX2P2, ``hgnc:54560``, references Ensembl record ``ensembl:ENSG00000227134`` and NCBI record ``ncbigene:100419816``
* The Ensembl record for OTX2P2, ``ensembl:ENSG00000227134``, references HGNC record ``hgnc:54560``

From this, the Gene Normalizer is able to produce two concept groups (one for each record), which the following visual makes clear:

.. The detail text in the figure below is invisible in dark mode, because it's just in a generic <p> block. We could probably invest some time into injecting custom SCSS and assigning it the "--color-foreground-primary" value at a later date. Once we're there, it'd be nice to update the colors and background of the figure as well.

.. raw:: html
   :file: ../_static/html/normalize_example.html

In practice, gene curation by these sources is quite thorough, and most records for well-understood genes in each source contain cross-reference to the corresponding records in the other sources. However, for normalized concept generation, it is sufficient for any record to be included in a normalized concept grouping if there is at least one cross-reference, in either direction, joining it to the rest of the concept group.

After grouping is complete, a concept ID for each normalized concept is selected from the record from the highest-priority source in each group. The SourcePriority class defines this priority ranking:

.. autoclass:: gene.schemas.SourcePriority
    :members:
    :undoc-members:
    :show-inheritance:
    :noindex:

Normalized gene records are constructed by merging known data from all associated gene records. For array-like fields (e.g. aliases, cross-references to entries in other data sources), data from all sources are simply combined. For scalar-like fields (e.g. the gene's symbol), the value is selected from an individual source record according to the priority assigned to the source.

.. _normalized-gene-object:

The normalized record
---------------------

Normalized records are structured as `Genes <https://github.com/ga4gh/vrs/tree/2.0-alpha>`_ per the VRS 2.x schema. The normalized gene concept ID is given, and additional metadata such as a label, mappings, aliases, and Extensions (for more complex information such as loci and gene type) is included. For example, the normalized result for the BRAF gene may be described as follows:

.. admonition:: Example

  .. code-block:: json

   {
     "id": "normalize.gene.hgnc:1097",
     "label": "BRAF",
     "extensions": [
       {
         "name": "symbol_status",
         "value": "approved"
       },
       {
         "name": "approved_name",
         "value": "B-Raf proto-oncogene, serine/threonine kinase"
       },
       {
         "name": "strand",
         "value": "-"
       },
       {
         "name": "ensembl_locations",
         "value": [
           {
             "id": "ga4gh:SL.fUv91vYrVHBMg-B_QW7UpOQj50g_49hb",
             "digest": "fUv91vYrVHBMg-B_QW7UpOQj50g_49hb",
             "type": "SequenceLocation",
             "sequenceReference": {
               "type": "SequenceReference",
               "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"
             },
             "start": 140719326,
             "end": 140924929
           }
         ]
       },
       {
         "name": "ncbi_locations",
         "value": [
           {
             "id": "ga4gh:SL.0nPwKHYNnTmJ06G-gSmz8BEhB_NTp-0B",
             "digest": "0nPwKHYNnTmJ06G-gSmz8BEhB_NTp-0B",
             "type": "SequenceLocation",
             "sequenceReference": {
               "type": "SequenceReference",
               "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"
             },
             "start": 140713327,
             "end": 140924929
           }
         ]
       },
       {
         "name": "hgnc_locus_type",
         "value": "gene with protein product"
       },
       {
         "name": "ncbi_gene_type",
         "value": "protein-coding"
       },
       {
         "name": "ensembl_biotype",
         "value": "protein_coding"
       }
     ],
     "mappings": [
       {
         "coding": {
           "system": "ncbigene",
           "code": "673"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "ensembl",
           "code": "ENSG00000157764"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "iuphar",
           "code": "1943"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "omim",
           "code": "164757"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "ccds",
           "code": "CCDS94218"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "pubmed",
           "code": "1565476"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "vega",
           "code": "OTTHUMG00000157457"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "ucsc",
           "code": "uc003vwc.5"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "ena.embl",
           "code": "M95712"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "ccds",
           "code": "CCDS87555"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "ccds",
           "code": "CCDS5863"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "cosmic",
           "code": "BRAF"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "pubmed",
           "code": "2284096"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "orphanet",
           "code": "119066"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "refseq",
           "code": "NM_004333"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "uniprot",
           "code": "P15056"
         },
         "relation": "relatedMatch"
       },
       {
         "coding": {
           "system": "ccds",
           "code": "CCDS94219"
         },
         "relation": "relatedMatch"
       }
     ],
     "type": "Gene",
     "aliases": [
       "RAFB1",
       "B-RAF1",
       "BRAF1",
       "BRAF-1",
       "B-raf",
       "NS7"
     ]
   }
