Usage
=====

Overview
--------

The Gene Normalizer provides three different search modes:

* **search**: for each :ref:`source <sources>`, find the record or records that best match the given search string. Returns :ref:`gene records <gene-record-object>`.
* **normalize**: find the normalized concept that best matches the given search string. Return a merged record that incorporates data from all associated records from each source. Returns :ref:`a normalized gene object <normalized-gene-object>`. See :ref:`build_normalization` for more information.
* **normalize_unmerged**: return each source record associated with the normalized concept that best matches the given search string. Returns :ref:`gene records <gene-record-object>`.

REST endpoints
--------------

Once :ref:`HTTP service is activated<starting-service>`, OpenAPI documentation for the REST endpoints is available under the ``/genes`` path (e.g., with default service parameters, at ``http://localhost:8000/genes``), describing endpoint parameters and response objects, and providing some minimal example queries. A live instance is available at `https://normalize.cancervariants.org/gene <https://normalize.cancervariants.org/gene>`_.

The individual endpoints are:

* ``/genes/search``
* ``/genes/normalize``
* ``/genes/normalize_unmerged``

Internal Python API
-------------------

Each search mode can be accessed directly within Python using the :py:mod:`query API<gene.query>`:

.. code-block:: pycon

    >>> from gene.database import create_db
    >>> from gene.query import QueryHandler
    >>> q = QueryHandler(create_db())
    >>> normalized_response = q.normalize('HER2')
    >>> normalized_response
    >>> normalized_response.match_type
    <MatchType.ALIAS: 60>
    >>> normalized_response.gene.name
    'ERBB2'

Critically, the ``QueryHandler`` class must receive a database interface instance as its first argument. The most straightforward way to construct a database instance, as demonstrated above, is with the :py:meth:`create_db() <gene.database.database.create_db>` method. This method tries to build a database connection based on a number of conditions, which are resolved in the following order:

1) if environment variable ``GENE_NORM_ENV`` is set to a value, or if the ``aws_instance`` method argument is True, try to create a cloud DynamoDB connection
2) if the ``db_url`` method argument is given a non-None value, try to create a DB connection to that address (if it looks like a PostgreSQL URL, create a PostgreSQL connection, but otherwise try DynamoDB)
3) if the ``GENE_NORM_DB_URL`` environment variable is set, try to create a DB connection to that address (if it looks like a PostgreSQL URL, create a PostgreSQL connection, but otherwise try DynamoDB)
4) otherwise, attempt a DynamoDB connection to the default URL, ``http://localhost:8000``

Users hoping for a more explicit connection declaration may instead call a database class directly, e.g.:

.. code-block:: python

    from gene.database.postgresql import PostgresDatabase
    from gene.query import QueryHandler
    pg_db = PostgresDatabase(
        user="postgres",
        password="matthew_cannon2",
        db_name="gene_normalizer"
    )
    q = QueryHandler(pg_db)

See the API documentation for the :py:mod:`database <gene.database.database>`, :py:mod:`DynamoDB <gene.database.dynamodb>`, and :py:mod:`PostgreSQL <gene.database.postgresql>` modules for more details.

Inputs
------

Gene symbols and aliases often contain only a handful of characters, raising a non-zero risk that search terms can be ambiguous or conflicting (see :download:`our lab's research on this topic <_static/documents/cgc_2023_poster.pdf>`). As described below, the Gene Normalizer will return the "best available" match where multiple are available, but users are advised to use concept identifiers or current, approved HGNC symbols where available.

Match types
-----------

The **best match** for a search string is determined by which fields in a gene record that it matches against. The Gene Normalizer will first try to match a search string against known concept IDs and gene symbols, then check for matches against previous or deprecated symbols, then aliases, etc. Matches are case-insensitive but must otherwise be exact.

.. autoclass:: gene.schemas.MatchType
    :members:
    :undoc-members:
    :show-inheritance:
    :noindex:

.. note::

    The `FUZZY_MATCH` Match Type is not currently used by the Gene Normalizer.
