Gene Normalizer |version|
=========================

The Gene Normalizer provides tools for resolving ambiguous gene references to consistently-structured, normalized terms. For gene concepts extracted from `NCBI Gene <https://www.ncbi.nlm.nih.gov/gene/>`_, `Ensembl <https://useast.ensembl.org/index.html>`_, and `HGNC <https://www.genenames.org/>`_, it designates a `CURIE <https://en.wikipedia.org/wiki/CURIE>`_, and provides additional metadata like current and previously-used symbols, aliases, and database cross-references and associations. See the `public instance of the service <https://normalize.cancervariants.org/gene>`_ for a demonstration.

The Gene Normalizer is a library created to support the `Knowledgebase Integration Project <https://cancervariants.org/projects/integration/>`_ of the `Variant Interpretation for Cancer Consortium (VICC) <https://cancervariants.org/>`_. It is developed primarily by the `Wagner Lab <https://www.nationwidechildrens.org/specialties/institute-for-genomic-medicine/research-labs/wagner-lab>`_.

.. toctree::
   :maxdepth: 1

    Quick installation<quick_install>
    Full installation<full_install>
    Loading and updating data<loading_and_updating_data>
    DynamoDB<dynamodb>
    PostgreSQL<postgresql>
    Using the search endpoints<search_endpoints>
    Information model and concept normalization<normalization>
    Query API<query_api>
    DynamoDB Handler API<dynamodb_api>
    PostgreSQL Handler API<postgres_api>
    Source ETL API<etl_api>
    Contributing<contributing>
