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

.. _build_normalization:

Building normalized concepts and records
----------------------------------------

Once all source records have been loaded into the database, normalized concept construction proceeds by grouping source records according to cross-references. For example, HGNC identifies Orthodenticle Homeobox 2 Pseudogene 1, or OTX2P1, as ``hgnc:33281``. The HGNC record also contains cross-references to ``ncbigene:100033409`` and ``ensembl:ENSG000000234644``. From this, the Gene Normalizer is able to produce a concept group containing each of these records:

.. The detail text in the figure below is invisible in dark mode, because it's just in a generic <p> block. We could probably invest some time into injecting custom SCSS and assigning it the "--color-foreground-primary" value at a later date. Once we're there, it'd be nice to update the colors and background of the figure as well.

.. raw:: html
   :file: ../_static/html/normalize_otx2p1.html

In practice, gene curation by these sources is quite thorough, and most records for well-understood genes in each source contain cross-reference to the corresponding records in the other sources. However, for normalized concept generation, it is sufficient for any record to be included in a normalized concept grouping if there is at least one cross-reference, in either direction, joining it to the rest of the concept group.

After grouping is complete, a concept ID for each normalized concept is selected from the record from the highest-priority source in each group. The SourcePriority class defines this priority ranking:

.. autoclass:: gene.schemas.SourcePriority
    :members:
    :undoc-members:
    :show-inheritance:

Normalized gene records are constructed by merging known data from all associated gene records. For array-like fields (e.g. aliases, cross-references to entries in other data sources), data from all sources are simply combined. For scalar-like fields (e.g. the gene's symbol), the value is selected from an individual source record according to the priority assigned to the source.

.. _normalized-gene-object:

The normalized record
---------------------

Normalized records are structured as `Gene Descriptors <https://vrsatile.readthedocs.io/en/latest/>`_ in conformance with the `GA4GH VRSATILE project <https://vrsatile.readthedocs.io/en/latest/>`_. The normalized gene concept is provided as a value object, and additional metadata is deposited as a label, xrefs, alternate labels, as well as Extensions for more complex information (such as loci and gene type). The following demonstrates this model for the BRAF gene:

.. admonition:: Example

  .. code-block:: json

    {
      "id": "normalize.gene:braf",
      "type": "GeneDescriptor",
      "label": "BRAF",
      "description": null,
      "xrefs": [
        "ensembl:ENSG00000157764",
        "ncbigene:673"
      ],
      "alternate_labels": [
        "NS7",
        "B-RAF1",
        "BRAF-1",
        "B-raf",
        "RAFB1",
        "BRAF1"
      ],
      "extensions": [
        {
          "type": "Extension",
          "name": "symbol_status",
          "value": "approved"
        },
        {
          "type": "Extension",
          "name": "approved_name",
          "value": "B-Raf proto-oncogene, serine/threonine kinase"
        },
        {
          "type": "Extension",
          "name": "associated_with",
          "value": [
            "cosmic:BRAF",
            "ena.embl:M95712",
            "omim:164757",
            "iuphar:1943",
            "ucsc:uc003vwc.5",
            "vega:OTTHUMG00000157457",
            "ccds:CCDS87555",
            "uniprot:P15056",
            "refseq:NM_004333",
            "pubmed:1565476",
            "orphanet:119066",
            "pubmed:2284096",
            "ccds:CCDS5863"
          ]
        },
        {
          "type": "Extension",
          "name": "hgnc_locations",
          "value": [
            {
              "_id": "ga4gh:VCL.O6yCQ1cnThOrTfK9YUgMlTfM6HTqbrKw",
              "type": "ChromosomeLocation",
              "species_id": "taxonomy:9606",
              "chr": "7",
              "interval": {
                "type": "CytobandInterval",
                "start": "q34",
                "end": "q34"
              }
            }
          ]
        },
        {
          "type": "Extension",
          "name": "strand",
          "value": "-"
        },
        {
          "type": "Extension",
          "name": "ensembl_locations",
          "value": [
            {
              "_id": "ga4gh:VSL.amNWL6i7F2nbSZAf2QLTRTujxuDrd0pR",
              "type": "SequenceLocation",
              "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
              "interval": {
                "type": "SequenceInterval",
                "start": {
                  "type": "Number",
                  "value": 140719326
                },
                "end": {
                  "type": "Number",
                  "value": 140924929
                }
              }
            }
          ]
        },
        {
          "type": "Extension",
          "name": "ncbi_locations",
          "value": [
            {
              "_id": "ga4gh:VCL.O6yCQ1cnThOrTfK9YUgMlTfM6HTqbrKw",
              "type": "ChromosomeLocation",
              "species_id": "taxonomy:9606",
              "chr": "7",
              "interval": {
                "type": "CytobandInterval",
                "start": "q34",
                "end": "q34"
              }
            },
            {
              "_id": "ga4gh:VSL.xZU3kL8F6t2ca6WH_26CWKfNW9-owhR4",
              "type": "SequenceLocation",
              "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
              "interval": {
                "type": "SequenceInterval",
                "start": {
                  "type": "Number",
                  "value": 140713327
                },
                "end": {
                  "type": "Number",
                  "value": 140924929
                }
              }
            }
          ]
        },
        {
          "type": "Extension",
          "name": "strand",
          "value": "-"
        },
        {
          "type": "Extension",
          "name": "hgnc_locus_type",
          "value": "gene with protein product"
        },
        {
          "type": "Extension",
          "name": "ncbi_gene_type",
          "value": "protein-coding"
        },
        {
          "type": "Extension",
          "name": "ensembl_biotype",
          "value": "protein_coding"
        }
      ],
      "gene_id": "hgnc:1097",
      "gene": null
    }
