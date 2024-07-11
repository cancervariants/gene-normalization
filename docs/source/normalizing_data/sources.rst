.. _sources:

Sources
=======

Normalized records are constructed by aggregating data from established resources in the genomics community. This section details those data sources and provides a high-level overview of data capture routines and the kinds of information extracted from each source.

.. note::

   Per the `GA4GH Variation Representation Specification (VRS) <https://vrs.ga4gh.org/en/stable/>`_, Genomic and cytogenic locations are stored and represented as `VRS locations <https://vrs.ga4gh.org/en/stable/terms_and_model.html#location>`_.

HGNC
----

`The HUGO Gene Nomenclature Committee database <https://www.genenames.org/>`_ provides records (referred to as *Symbol Reports*) for protein-coding genes, pseudogenes, and non-coding RNA genes as designated by the HGNC. Symbol reports contain approved symbols, previously-used symbols, full names, and other relevant information for each approved gene. The Gene Normalizer extracts nomenclature, aliases, cross-references, and locus types for all HGNC gene records. Data is extracted from the latest HGNC JSON release (``hgnc_complete_set.json``) provided on the `HGNC archive page <https://www.genenames.org/download/archive/>`_.

.. admonition:: Example

  .. code-block:: json

   {
     "concept_id": "hgnc:1097",
     "symbol": "BRAF",
     "symbol_status": "approved",
     "label": "B-Raf proto-oncogene, serine/threonine kinase",
     "strand": null,
     "location_annotations": [],
     "locations": [],
     "aliases": [
       "BRAF1",
       "BRAF-1"
     ],
     "previous_symbols": [],
     "xrefs": [
       "ensembl:ENSG00000157764",
       "ncbigene:673"
     ],
     "associated_with": [
       "uniprot:P15056",
       "pubmed:2284096",
       "omim:164757",
       "pubmed:1565476",
       "ccds:CCDS5863",
       "cosmic:BRAF",
       "ucsc:uc003vwc.5",
       "ccds:CCDS87555",
       "orphanet:119066",
       "ena.embl:M95712",
       "vega:OTTHUMG00000157457",
       "ccds:CCDS94218",
       "ccds:CCDS94219",
       "refseq:NM_004333",
       "iuphar:1943"
     ],
     "gene_type": "gene with protein product",
     "match_type": 100
   }

Ensembl
-------

`Ensembl <https://ensembl.org>`_ is an online genome browser provided by EMBL-EBI to support research in vertebrates and model organisms. The Gene Normalizer extracts human gene identifiers, names, symbols, cross-references, Ensembl biotypes, and genomic locations for each Ensembl gene record. Data is pulled from the latest Ensembl release listed on the `EBI FTP server <https://ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.109.gff3.gz>`_.

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
         "id": "ga4gh:SL.fUv91vYrVHBMg-B_QW7UpOQj50g_49hb",
         "digest": "fUv91vYrVHBMg-B_QW7UpOQj50g_49hb",
         "label": null,
         "description": null,
         "extensions": null,
         "digest": null,
         "type": "SequenceLocation",
         "sequenceReference": {
           "id": null,
           "label": null,
           "description": null,
           "extensions": null,
           "digest": null,
           "type": "SequenceReference",
           "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
           "residueAlphabet": null
         },
         "start": 140719326,
         "end": 140924929
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

The `NCBI Gene Database <https://www.ncbi.nlm.nih.gov/gene/>`_ is a service provided under the NCBI Database mantle, relaying gene nomenclature, reference sequences, pathways, and cross-references to other genomic resources. The Gene Normalizer selects all records for *homo sapiens* and gathers names, aliases, cross-references, gene types, and cytogenic and genomic loci. Data is sourced from the latest Homo Sapiens release provided on the `NCBI FTP server <https://ftp.ncbi.nlm.nih.gov/gene/DATA/GENE_INFO/Mammalia/>`_.

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

Source metadata
---------------

Query responses also include metadata objects describing important data attributes:

* ``data_license``, ``data_license_attributes``, ``data_license_url``: the name (if available) and boolean attributes of the source's licensing agreement, along with a link to that license. Attributes should be interpreted as whether or not something is required; for example, ``"non_commercial": false`` means that there is no restriction on commercial usage of that data. These values are curated by us, and users should consult directly with the sources and are solely responsible for understanding and complying with any constraints that they may impose.
* ``rdp_url``: link to the relevant entry on the `Reusable Data Project <https://reusabledata.org/>`_, if available. The RDP provides more extensive analysis of data licenses, particularly when sources employ custom licensing schemes.
* ``version``: the data release version.
* ``data_url``: the location of the materials used to generate source data in the Gene Normalizer. Where possible, a direct link is supplied.
* ``genome_assemblies``: The assembly, or assemblies, used for reported sequence location data.

.. admonition:: Example

  .. code-block:: json

   {
     "data_license": "custom",
     "data_license_url": "https://www.ncbi.nlm.nih.gov/home/about/policies/",
     "version": "20230929",
     "data_url": {
       "info_file": "ftp.ncbi.nlm.nih.govgene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz",
       "history_file": "ftp.ncbi.nlm.nih.govgene/DATA/gene_history.gz",
       "assembly_file": "ftp.ncbi.nlm.nih.govgenomes/refseq/vertebrate_mammalian/Homo_sapiens/latest_assembly_versions/"
     },
     "rdp_url": "https://reusabledata.org/ncbi-gene.html",
     "data_license_attributes": {
       "non_commercial": false,
       "attribution": false,
       "share_alike": false
     },
     "genome_assemblies": [
       "GRCh38.p14"
     ]
   }
