Searching genes
===============

Overview
--------

The Gene Normalizer provides three different search modes:

 * **search**: for each source, find the record or records that best match the given search string.
 * **normalize**: find the normalized concept that best matches the given search string. Return a merged record that incorporates data from all associated records from each source. See :ref:`build_normalization` for more information.
 * **normalize_unmerged**: find the normalized concept that best matches the given search string. Return each source record associated with that normalized concept.

REST endpoints
--------------

Once :ref:`HTTP service is activated<starting-service>`, OpenAPI documentation for the REST endpoints is available at the ``/genes`` subdirectory (e.g., with default service parameters, at ``http://localhost:8000/genes``). This documentation describes endpoint parameters and response objects, and provides some minimal example queries.

The individual endpoints are:

* ``/genes/search``
* ``/genes/normalize``
* ``/genes/normalize_unmerged``

Internal Python API
-------------------

Each search mode can be accessed directly within Python using the :ref:`query API<query-api>`:

::

    >>> from gene.database import create_db
    >>> from gene.query import QueryHandler
    >>> q = QueryHandler(create_db())
    >>> normalized_response = q.normalize('HER2')
    >>> normalized_response
    >>> normalized_response.match_type
    <MatchType.ALIAS: 60>
    >>> normalized_response.gene_descriptor.label
    'ERBB2'



Match types
-----------

The **best match** for a search string is determined by which fields in a gene record that it matches against. The Gene Normalizer will first try to match a search string against known concept IDs and gene symbols, then check for matches against previous or deprecated symbols, then aliases, etc. Matches are case-insensitive but must otherwise be exact.

.. autoclass:: gene.schemas.MatchType
    :members:
    :undoc-members:
    :show-inheritance:

.. note::

    The `FUZZY_MATCH` Match Type is not currently used by the Gene Normalizer.
