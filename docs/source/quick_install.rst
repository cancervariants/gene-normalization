Quick Installation
==================

These instructions describe installation of a static (i.e., non-updateable) version of the Gene Normalizer using a PostgreSQL database. To use another database backend, or to enable data updates, see the :ref:`full_install` instructions.

Requirements
------------

* A UNIX-like environment (e.g. MacOS, WSL, Ubuntu)
* Python 3.8+
* A recent version of PostgreSQL (ideally at least 11+)

Installation Steps
------------------

Install the Gene Normalizer via PyPI (see the :ref:`note on dependency groups <Dependency groups>` for more info): ::

    pip install "gene-normalizer[pg]"

Create a new PostgreSQL database. For example, using the `psql createdb <https://www.postgresql.org/docs/current/app-createdb.html>`_ utility, and assuming that ``postgres`` is a valid user: ::

    createdb -h localhost -p 5432 -U postgres gene_normalizer

Set the environment variable ``GENE_NORM_DB_URL`` to a connection description for that database. See the PostgreSQL `connection string documentation <https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING>`_ for more information: ::

   export GENE_NORM_DB_URL=postgres://postgres@localhost:5432/gene_normalizer

Use the ``gene_norm_update_remote`` shell command to load data from the most recent remotely-stored data dump: ::

    gene_norm_update_remote

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
