Loading and updating data
=========================

See the :ref:`ETL API documentation<etl-api>` for information on programmatic access.

Full load/reload
----------------

Calling the Gene Normalizer update command with the ``--update_all`` and ``--update_merged`` flags will delete all existing data, fetch new source data if available, and then perform a complete reload of the database: ::

    gene_norm_update --update_all --update_merged


Reload individual source
------------------------

To update specific sources, use the ``--normalizer`` option along with source name(s), quoted and separated by spaces. While it is possible to update individual source data without updating the normalized record data with ``--update_merged``, the normalization query endpoints may not function properly until normalized data is refreshed again. ::

    gene_norm_update --normalizer="HGNC NCBI" --update_merged

