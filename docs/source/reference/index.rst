.. _api_reference:

API Reference
=============

Core Modules
--------------

.. autosummary::
   :nosignatures:
   :toctree: api/
   :template: module_summary.rst

   gene.query
   gene.schemas

Database Modules
--------------------

.. autosummary::
   :nosignatures:
   :toctree: api/database
   :template: module_summary.rst

   gene.database.database
   gene.database.dynamodb
   gene.database.postgresql

.. _etl-api:

ETL Modules
-----------

.. autosummary::
   :nosignatures:
   :toctree: api/etl
   :template: module_summary_inherited.rst

   gene.etl.base
   gene.etl.ensembl
   gene.etl.hgnc
   gene.etl.ncbi
   gene.etl.update
   gene.etl.exceptions
   gene.etl.merge
