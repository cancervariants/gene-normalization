Loading and updating data
=========================

See the :ref:`ETL API documentation<etl-api>` for information on programmatic access.

Full load/reload
----------------

Calling the Gene Normalizer update command with the ``--update_all`` and ``--update_merged`` flags will delete all existing data, fetch new source data if available, and then perform a complete reload of the database: ::

    gene_norm_update --update_all --update_merged


Reload individual source
------------------------

To update specific sources, use the ``--source`` option along with source name(s), quoted and separated by spaces. While it is possible to update individual source data without updating the normalized record data with ``--update_merged``, the normalization query endpoints may not function properly until normalized data is refreshed again. ::

    gene_norm_update --source="HGNC NCBI" --update_merged


Check DB health
---------------

The shell command `gene_norm_check_db` performs a basic check on the database status. It first confirms that the database's schema exists, and then identifies whether metadata is available for each source, and whether gene record and normalized concept tables are non-empty. Check the process's exit code for the result. ::

    % gene_norm_check_db
    % echo $?
    1  # indicates failure
