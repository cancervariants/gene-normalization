.. _etl-api:

Source ETL API
==============

Base
----

.. autoclass:: gene.etl.base.Base
    :members:
    :special-members: __init__
    :undoc-members:

NCBI
----

.. autoclass:: gene.etl.ncbi.NCBI
    :members:
    :special-members: __init__
    :undoc-members:
    :show-inheritance:
    :inherited-members:

HGNC
----

.. autoclass:: gene.etl.hgnc.HGNC
    :members:
    :special-members: __init__
    :undoc-members:
    :show-inheritance:
    :inherited-members:

Ensembl
-------

.. autoclass:: gene.etl.ensembl.Ensembl
    :members:
    :special-members: __init__
    :undoc-members:
    :show-inheritance:
    :inherited-members:

Normalized Records
------------------

.. autoclass:: gene.etl.merge.Merge
    :members:
    :special-members: __init__
    :undoc-members:
    :show-inheritance:

Chromosome Location
-------------------------------

.. autoclass:: gene.etl.vrs_locations.chromosome_location.ChromosomeLocation
    :members:
    :special-members: __init__
    :undoc-members:

Sequence Location
-----------------------------

.. autoclass:: gene.etl.vrs_locations.sequence_location.SequenceLocation
    :members:
    :special-members: __init__
    :undoc-members:
