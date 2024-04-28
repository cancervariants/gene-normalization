.. _loading_and_updating_data:

Loading and updating data
=========================

The Gene Normalizer defines a command line tool for data management. It includes functions for refreshing data, checking database status, and for the PostgreSQL data backend, dumping to a local file and updating from a remote backup.

.. note::

    See the :ref:`data updates API documentation <data_updates_api>` for information on programmatic access to the data loader classes.


.. click:: gene.cli:cli
   :prog: gene-normalizer
   :nested: full
