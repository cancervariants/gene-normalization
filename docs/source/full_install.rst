.. _full_install:

Full Installation
=================

Requirements
------------

* A UNIX-like environment (e.g. MacOS, WSL, Ubuntu) with superuser permissions
* Python 3.8+
* A recent version of PostgreSQL (ideally at least 11+), if using PostgreSQL as the database backend
* An available Java runtime (version 8.x or newer), or Docker Desktop, if using DynamoDB as the database backend

Package installation
--------------------

First, install the Gene Normalizer from PyPI: ::

    pip install gene-normalizer[dev]

The ``[dev]`` option installs dependencies necessary for using the ``gene.etl`` package, which performs data loading operations.


SeqRepo
-------

Next, acquire `SeqRepo <https://github.com/biocommons/biocommons.seqrepo>`_ sequence and alias data. ::

    sudo mkdir /usr/local/share/seqrepo
    sudo chown $USER /usr/local/share/seqrepo
    seqrepo pull -i 2021-01-29  # Replace with latest version using `seqrepo list-remote-instances` if outdated

If you encounter an error like the following: ::

    PermissionError: [Error 13] Permission denied: '/usr/local/share/seqrepo/2021-01-29._fkuefgd' -> '/usr/local/share/seqrepo/2021-01-29'

You may need to manually finish moving sequence files (replace the `XXXXXX` characters in the path below with the temporary name created by your instance): ::

    sudo mv /usr/local/share/seqrepo/2021-01-29.XXXXXXX /usr/local/share/seqrepo/2021-01-29


Database setup
--------------

The Gene Normalizer requires a separate database process for data storage and retrieval. See the instructions on database setup and initialization for the available database options:

* :ref:`dynamodb`
* :ref:`postgres`


Loading data
------------

To load all source data, and then generate normalized records, use the following shell command: ::

    gene_norm_update --update_all --update_merged

This will download the latest available versions of all source data files, extract and transform recognized gene concepts, load them into the database, and construct normalized concept groups. For more specific update commands, see the TODO SECTION ON THAT REF OUT

.. _starting-service:

Starting service
----------------

Start an instance of the gene normalizer API: ::

    uvicorn gene.main:app --port=5000

Point your browser to http://localhost:5000/gene/. You should see the SwaggerUI page demonstrating available REST endpoints.
