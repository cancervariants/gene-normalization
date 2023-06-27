.. _loading_and_updating_data:

Loading and updating data
=========================

.. note::

    See the :ref:`ETL API documentation<etl-api>` for information on programmatic access to the data loader classes.

Full load/reload
----------------

Calling the Gene Normalizer update command with the ``--update_all`` and ``--update_merged`` flags will delete all existing data, fetch new source data if available, and then perform a complete reload of the database (including merged records):

.. code-block:: shell

    gene_norm_update --update_all --update_merged


Reload individual source
------------------------

To update specific sources, call the ``--sources`` option with one or more source name(s) quoted and separated by spaces. While it is possible to update individual source data without also updating the normalized record data, that may affect the proper function of the normalized query endpoints, so it is recommended to include the ``--update_merged`` flag as well.

.. code-block:: shell

    gene_norm_update --sources="HGNC NCBI" --update_merged


Check DB health
---------------

The shell command ``gene_norm_check_db`` performs a basic check on the database status. It first confirms that the database's schema exists, and then identifies whether metadata is available for each source, and whether gene record and normalized concept tables are non-empty. Check the process's exit code for the result (per the UNIX standard, ``0`` means success, and any other return code means failure).

.. code-block:: console

    $ gene_norm_check_db
    $ echo $?
    1  # indicates failure
