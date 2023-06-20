.. _sources:

Sources
=======

Normalized records are constructed by aggregating data from established resources in the genomics community. This section details those data sources and provides a high-level overview of data capture routines and the kinds of information extracted from each source.

.. note::

   Per the `GA4GH Variation Representation Specification (VRS) <https://vrs.ga4gh.org/en/stable/>`_, Genomic and cytogenic locations are stored and represented as `VRS locations <https://vrs.ga4gh.org/en/stable/terms_and_model.html#location>`_.

HGNC
----

`The HUGO Gene Nomenclature Committee database <https://www.genenames.org/>`_ provides records (referred to as *Symbol Reports*) for protein-coding genes, pseudogenes, and non-coding RNA genes as designated by the HGNC. :footcite:p:`Hgnc2023` Symbol reports contain approved symbols, previously-used symbols, full names, and other relevant information for each approved gene. The Gene Normalizer extracts nomenclature, aliases, cross-references, locus types, and VRS Chromosome Locations for all HGNC gene records. Data is extracted from the latest HGNC JSON release (``hgnc_complete_set.json``) provided on the `HGNC archive page <https://www.genenames.org/download/archive/>`_. `Computed identifiers <https://vrs.ga4gh.org/en/stable/impl-guide/computed_identifiers.html>`_ are used to identify source accessions.

.. admonition:: Example

  .. code-block:: json

    {
      "concept_id": "hgnc:1097",
      "symbol": "BRAF",
      "symbol_status": "approved",
      "label": "B-Raf proto-oncogene, serine/threonine kinase",
      "strand": null,
      "location_annotations": [],
      "locations": [
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
      ],
      "aliases": [
        "BRAF-1",
        "BRAF1"
      ],
      "previous_symbols": [],
      "xrefs": [
        "ensembl:ENSG00000157764",
        "ncbigene:673"
      ],
      "associated_with": [
        "uniprot:P15056",
        "ena.embl:M95712",
        "pubmed:2284096",
        "ucsc:uc003vwc.5",
        "ccds:CCDS5863",
        "omim:164757",
        "cosmic:BRAF",
        "vega:OTTHUMG00000157457",
        "pubmed:1565476",
        "orphanet:119066",
        "iuphar:1943",
        "ccds:CCDS87555",
        "refseq:NM_004333"
      ],
      "gene_type": "gene with protein product",
      "match_type": 100
    }

Ensembl
-------

`Ensembl <https://ensembl.org>`_ is an online genome browser provided by EMBL-EBI to support research in vertebrates and model organisms. :footcite:p:`Ensembl2023` The Gene Normalizer extracts human gene identifiers, names, symbols, cross-references, Ensembl biotypes, and genomic locations for each Ensembl gene record. Data is pulled from the latest Ensembl release listed on the `EBI FTP server <https://ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.109.gff3.gz>`_.

.. admonition:: Example

  .. code-block:: json

    {
      "concept_id": "ensembl:ENSG00000157764",
      "symbol": "BRAF",
      "symbol_status": null,
      "label": "B-Raf proto-oncogene, serine/threonine kinase",
      "strand": "-",
      "location_annotations": [],
      "locations": [
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
      ],
      "aliases": [],
      "previous_symbols": [],
      "xrefs": [
        "hgnc:1097"
      ],
      "associated_with": [],
      "gene_type": "protein_coding",
      "match_type": 100
    }

NCBI Gene
---------

The `NCBI Gene Database <https://www.ncbi.nlm.nih.gov/gene/>`_ is a service provided under the NCBI Database mantle, relaying gene nomenclature, reference sequences, pathways, and cross-references to other genomic resources. :footcite:p:`Ncbi2022` The Gene Normalizer selects all records for *homo sapiens* and gathers names, aliases, cross-references, gene types, and cytogenic and genomic loci. Data is sourced from the latest Homo Sapiens release provided on the `NCBI FTP server <https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/>`_.

.. admonition:: Example

  .. code-block:: json

    {
      "concept_id": "ncbigene:673",
      "symbol": "BRAF",
      "symbol_status": null,
      "label": "B-Raf proto-oncogene, serine/threonine kinase",
      "strand": "-",
      "location_annotations": [],
      "locations": [
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
      ],
      "aliases": [
        "RAFB1",
        "BRAF-1",
        "BRAF1",
        "NS7",
        "B-RAF1",
        "B-raf"
      ],
      "previous_symbols": [],
      "xrefs": [
        "ensembl:ENSG00000157764",
        "hgnc:1097"
      ],
      "associated_with": [
        "omim:164757"
      ],
      "gene_type": "protein-coding",
      "match_type": 100
    }

References
__________

.. footbibliography::
