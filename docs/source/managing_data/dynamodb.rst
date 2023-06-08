.. _dynamodb:

DynamoDB
========

The Gene Normalizer can store and retrieve gene records from a `local DynamoDB <https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html>`_ database instance.

.. note::

    See the :ref:`DynamoDB handler API reference<dynamodb_api>` for information on programmatic access.

Local setup
-----------

See the `instructions for deploying and running DynamoDB local <https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html>`_ in the AWS docs for server setup instructions.

By default, the Gene Normalizer expects to find a DynamoDB instance running at ``http://localhost:8000``. The ``GENE_NORM_DB_URL`` environment variable can be used to designate an alternate location: ::

    export GENE_NORM_DB_URL=http://localhost:8001

.. warning::

    By default, DynamoDB Local serves to port 8000, which is also the port at which Uvicorn serves by default. This means that when running Gene Normalizer REST service with DynamoDB, you may have to use a different port for one of those processes. To do so with DynamoDB, use the ``-port`` option: ::

        java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -port 8001
        # then, in the Gene Normalizer's environment:
        export GENE_NORM_DB_URL=http://localhost:8001


Managing persistent DynamoDB data
--------------------------------------------

DynamoDB Local will store all data in a file named ``shared-local-instance.db`` when called with the ``sharedDb`` flag. This file persists after the database process ends and can be shared with other users. An alternate directory can be provided with the ``dbPath`` option if the DB file is stored in a different directory, e.g.: ::

    java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb -dbPath ../other_directory/

If the ``sharedDb`` flag is not provided, then data will not persist after the DynamoDB process ends.
