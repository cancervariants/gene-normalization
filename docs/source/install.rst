Installation
============

The Gene Normalizer can be installed from `PyPI <https://pypi.org/project/gene-normalizer/>`_. Users who have access to a PostgreSQL database and don't need to regenerate the Gene Normalizer database can use the :ref:`quick installation instructions <quick-install>`. To use a DynamoDB instance, or to enable local data updates, use the :ref:`full installation instructions <full-install>`.

.. _dependency-groups:

.. note::

    The Gene Normalizer defines five optional dependency groups in total:

    * ``etl`` provides dependencies for regenerating data from sources. It's necessary for users who don't intend to rely on existing database dumps.
    * ``pg`` provides dependencies for connecting to a PostgreSQL database. It's not necessary for users who are using a DynamoDB backend.
    * ``dev`` provides development dependencies, such as static code analysis. It's required for contributing to the Gene Normalizer, but otherwise unnecessary.
    * ``test`` provides dependencies for running tests. As with ``dev``, it's mostly relevant for contributors.
    * ``docs`` provides dependencies for documentation generation. It's only relevant for contributors.

.. _quick-install:

Quick Installation
------------------

Requirements
++++++++++++

* A UNIX-like environment (e.g. MacOS, WSL, Ubuntu)
* Python 3.8+
* A recent version of PostgreSQL (ideally at least 11+)

Package installation
++++++++++++++++++++

Install the Gene Normalizer, and the ``pg`` :ref:`dependency group <dependency-groups>`, via PyPI::

    pip install "gene-normalizer[pg]"

Database setup
++++++++++++++

Create a new PostgreSQL database. For example, using the `psql createdb <https://www.postgresql.org/docs/current/app-createdb.html>`_ utility, and assuming that ``postgres`` is a valid user: ::

    createdb -h localhost -p 5432 -U postgres gene_normalizer

Set the environment variable ``GENE_NORM_DB_URL`` to a connection description for that database. See the PostgreSQL `connection string documentation <https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING>`_ for more information: ::

   export GENE_NORM_DB_URL=postgres://postgres@localhost:5432/gene_normalizer

Load data
+++++++++

Use the ``gene_norm_update_remote`` shell command to load data from the most recent remotely-stored data dump: ::

    gene_norm_update_remote

Start service
+++++++++++++

Finally, start an instance of the gene normalizer API on port 5000: ::

    uvicorn gene.main:app --port=5000

Point your browser to http://localhost:5000/gene/. You should see the SwaggerUI page demonstrating available REST endpoints.

The beginning of the response to a GET request to http://localhost:5000/gene/normalize?q=braf should look something like this:

.. code-block::

    {
      "query": "braf",
      "warnings": [],
      "match_type": 100,
      "service_meta_": {
        "version": "0.1.33",
        "response_datetime": "2023-03-29 15:10:58.579675",
        "name": "gene-normalizer",
        "url": "https://github.com/cancervariants/gene-normalization"
      },
      "gene_descriptor": {
        "id": "normalize.gene:braf",
        "type": "GeneDescriptor",
        "label": "BRAF",

        ...
      }
    }


.. _full-install:

Full Installation
-----------------

Requirements
++++++++++++

* A UNIX-like environment (e.g. MacOS, WSL, Ubuntu) with superuser permissions
* Python 3.8+
* A recent version of PostgreSQL (ideally at least 11+), if using PostgreSQL as the database backend
* An available Java runtime (version 8.x or newer), or Docker Desktop, if using DynamoDB as the database backend

Package installation
++++++++++++++++++++

First, install the Gene Normalizer from PyPI: ::

    pip install "gene-normalizer[etl]"

The ``[etl]`` option installs dependencies necessary for using the ``gene.etl`` package, which performs data loading operations.

Users intending to utilize PostgreSQL to store source data should also include the ``pg`` :ref:`dependency group <dependency-groups>`: ::

    pip install "gene-normalizer[etl,pg]"

SeqRepo
+++++++

Next, acquire `SeqRepo <https://github.com/biocommons/biocommons.seqrepo>`_ sequence and alias data. ::

    sudo mkdir /usr/local/share/seqrepo
    sudo chown $USER /usr/local/share/seqrepo
    seqrepo pull -i 2021-01-29  # Replace with latest version using `seqrepo list-remote-instances` if outdated

If you encounter an error like the following: ::

    PermissionError: [Error 13] Permission denied: '/usr/local/share/seqrepo/2021-01-29._fkuefgd' -> '/usr/local/share/seqrepo/2021-01-29'

You may need to manually finish moving sequence files (replace the `XXXXXX` characters in the path below with the temporary name created by your instance): ::

    sudo mv /usr/local/share/seqrepo/2021-01-29.XXXXXXX /usr/local/share/seqrepo/2021-01-29

By default, the Gene Normalizer expects seqrepo data to be located at ``/usr/local/share/seqrepo/latest``. To designate an alternate location, set the ``SEQREPO_ROOT_DIR`` environment variable.


Database setup
++++++++++++++

The Gene Normalizer requires a separate database process for data storage and retrieval. See the instructions on database setup and population for the available database options:

* :ref:`dynamodb`
* :ref:`postgres`

By default, the Gene Normalizer will attempt to connect to a DynamoDB instance listening at ``http://localhost:8000``.

Load data
+++++++++

To load all source data, and then generate normalized records, use the following shell command: ::

    gene_norm_update --update_all --update_merged

This will download the latest available versions of all source data files, extract and transform recognized gene concepts, load them into the database, and construct normalized concept groups. For more specific update commands, see :ref:`Loading and updating data <loading_and_updating_data>`.

.. _starting-service:

Start service
+++++++++++++

Start an instance of the gene normalizer API: ::

    uvicorn gene.main:app --port=5000

Point your browser to http://localhost:5000/gene/. You should see the SwaggerUI page demonstrating available REST endpoints.
