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

Normalized records are structured as `Genes <https://github.com/ga4gh/vrs/tree/2.0-alpha>`_ per the VRS 2.x schema. The normalized gene concept ID is given, and additional metadata such as a name, mappings, aliases, and Extensions (for more complex information such as loci and gene type) is included. For example, the normalized result for the BRAF gene may be described as follows:

.. admonition:: Example

  .. code-block:: json

    {
      "conceptType": "Gene",
      "id": "normalize.gene.hgnc:1097",
      "primaryCoding": {
            "id": "hgnc:1097",
            "code": "HGNC:1097",
            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
        },
      "name": "BRAF",
      "mappings": [
          {
              "coding": {
                  "id": "ncbigene:673",
                  "code": "673",
                  "system": "https://www.ncbi.nlm.nih.gov/gene/",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "ensembl:ENSG00000157764",
                  "code": "ENSG00000157764",
                  "system": "https://www.ensembl.org/id/",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "iuphar:1943",
                  "code": "1943",
                  "system": "https://www.guidetopharmacology.org/GRAC/ObjectDisplayForward?objectId=",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "orphanet:119066",
                  "code": "119066",
                  "system": "http://www.orpha.net/consor/cgi-bin/OC_Exp.php?Lng=EN&Expert=",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "cosmic:BRAF",
                  "code": "BRAF",
                  "system": "http://cancer.sanger.ac.uk/cosmic/gene/overview?ln=",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "pubmed:2284096",
                  "code": "2284096",
                  "system": "https://pubmed.ncbi.nlm.nih.gov/",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "ucsc:uc003vwc.5",
                  "code": "uc003vwc.5",
                  "system": "http://genome.cse.ucsc.edu/cgi-bin/hgGene?org=Human&hgg_chrom=none&hgg_type=knownGene&hgg_gene=",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "omim:164757",
                  "code": "164757",
                  "system": "https://www.omim.org/MIM:",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "refseq:NM_004333",
                  "code": "NM_004333",
                  "system": "https://www.ncbi.nlm.nih.gov/nuccore/",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "uniprot:P15056",
                  "code": "P15056",
                  "system": "http://purl.uniprot.org/uniprot/",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "ena.embl:M95712",
                  "code": "M95712",
                  "system": "https://www.ebi.ac.uk/ena/browser/view/",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "vega:OTTHUMG00000157457",
                  "code": "OTTHUMG00000157457",
                  "system": "https://vega.archive.ensembl.org/Homo_sapiens/Gene/Summary?g=",
              },
              "relation": "relatedMatch",
          },
          {
              "coding": {
                  "id": "pubmed:1565476",
                  "code": "1565476",
                  "system": "https://pubmed.ncbi.nlm.nih.gov/",
              },
              "relation": "relatedMatch",
          },
      ],
      "extensions": [
        {
          "name": "aliases",
          "value": [
            "BRAF1",
            "BRAF-1",
            "RAFB1",
            "NS7",
            "B-RAF1",
            "B-raf"
          ]
        },
        {
          "name": "approved_name",
          "value": "B-Raf proto-oncogene, serine/threonine kinase"
        },
        {
          "name": "ensembl_locations",
          "value": [
            {
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
          "name": "ncbi_gene_type",
          "value": "protein-coding"
        },
        {
          "name": "hgnc_locus_type",
          "value": "gene with protein product"
        },
        {
          "name": "ensembl_biotype",
          "value": "protein_coding"
        },
        {
          "name": "strand",
          "value": "-"
        },
        {
          "name": "symbol_status",
          "value": "approved"
        }
      ]
    }
