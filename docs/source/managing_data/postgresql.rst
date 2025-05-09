.. _postgres:

PostgreSQL
==========

The Gene Normalizer can store and retrieve gene records from a `PostgreSQL <https://www.postgresql.org/>`_ database. See the `"Getting Started" section of the PostgreSQL documentation <https://www.postgresql.org/docs/current/tutorial-start.html>`_ for basic installation instructions.

.. note::

    See the :py:mod:`PostgreSQL handler API reference<gene.database.postgresql>` for information on programmatic access.

Local setup
--------------

To populate the Gene Normalizer, a connection must be established to an existing PostgreSQL database, so one must be created manually when performing Gene Normalizer setup. Most PostgreSQL distributions include the `createdb <https://www.postgresql.org/docs/current/app-createdb.html>`_ utility for this purpose. For example, to create a database named ``gene_normalizer`` in a local database listening on port 5432 using the PostgreSQL user named ``postgres``, run the following shell command: ::

    createdb -h localhost -p 5432 -U postgres gene_normalizer

Once created, set the environment variable ``GENE_NORM_DB_URL`` to a connection description for that database. The following command provides a connection to a database named ``gene_normalizer`` in a local PostgreSQL instance, using port 5432, under the username ``postgres`` with no required password. See the PostgreSQL `connection string documentation <https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING>`_ for more information. ::

   export GENE_NORM_DB_URL=postgres://postgres@localhost:5432/gene_normalizer


Load from remote source
--------------------------------

The Gene Normalizer's PostgreSQL class provides the ``gene-normalizer update-from-remote`` shell command to refresh its data directly from a remotely-stored SQL dump, instead of acquiring, transforming, and loading source data. This enables data loading on the order of seconds rather than hours. See the command description at ``gene-normalizer update-from-remote --help`` for more information.

By default, this command will fetch the `latest data dump <https://vicc-normalizers.s3.us-east-2.amazonaws.com/gene_normalization/postgresql/gene_norm_latest.sql.tar.gz>`_ provided by the VICC. Alternative URLs can be set with the ``--data_url`` option: ::

    gene-normalizer update-from-remote --data_url=https://vicc-normalizers.s3.us-east-2.amazonaws.com/gene_normalization/postgresql/gene_norm_20230322163523.sql.tar.gz


Create SQL dump from database
-----------------------------

The Gene Normalizer's PostgreSQL class also provides the ``gene-normalizer dump-database`` shell command to create a SQL dump of current data into a file. This command will create a file named ``gene_norm_YYYYMMDDHHmmss.sql`` in the current directory; the ``-o`` option can be used to specify an alternate location, like so: ::

    gene-normalizer dump-database -o ~/.gene_data/

See ``gene-normalizer dump-database --help`` for more information.
