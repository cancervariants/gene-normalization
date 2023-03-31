Using the search endpoints
==========================

Overview
--------

The Gene Normalizer provides three different search modes:

 * **/search**: for each source, find the record or records that best match the given search string.
 * **/normalize**: find the normalized concept that best matches the given search string. Return a merged record that incorporates data from all associated records from each source.
 * **/normalize_unmerged**: find the normalized concept that best matches the given search string. Return each source record associated with that normalized concept.


Match types
-----------

The **best match** for a search string is determined by which fields in a gene record that it matches against. The Gene Normalizer will first try to match a search string against known concept IDs and gene symbols, then check for matches against previous or deprecated symbols, then aliases, etc. Matches are case-insensitive but must otherwise be exact.

.. autoclass:: gene.schemas.MatchType
    :members:
    :undoc-members:
    :show-inheritance:

*Note*: The `FUZZY_MATCH` Match Type is not currently used by the Gene Normalizer.
