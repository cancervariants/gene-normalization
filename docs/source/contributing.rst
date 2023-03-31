Contributing to the Gene Normalizer
===================================

Prerequisites
-------------
For a development install, we recommend using Pipenv. See the `pipenv docs <https://pipenv-fork.readthedocs.io/en/latest/#install-pipenv-today>`_ for direction on installing Pipenv in your environment.

Setup
-----
Clone the repository: ::

    git clone https://github.com/cancervariants/gene-normalization
    cd gene-normalization

Then initialize the Pipenv environment: ::

    pipenv update
    pipenv install --dev
    pipenv shell

We use `pre-commit <https://pre-commit.com/#usage>`_ to run conformance tests before commits. This provides checks for:

* Code style
* Added large files
* AWS credentials
* Private keys

Before your first commit, run: ::

    pre-commit install

When running the web server, enable hot-reloading on new code changes: ::

    uvicorn gene.main:app --reload


Style
-----

Code style is managed by `flake8 <https://github.com/PyCQA/flake8>`_ and should be checked via pre-commit hook before commits. Final QC is applied with GitHub Actions to every pull request.


Tests
-----

Tests are executed with `pytest <https://docs.pytest.org/en/7.1.x/getting-started.html>`_: ::

    pytest

By default, tests will utilize an existing database, and won't load any new data. For test environments where this is unavailable (e.g. in CI), the `GENE_TEST` environment variable can be set to initialize the connected database instance with miniature versions of input data files before tests are executed: ::

    export GENE_TEST=true

This does overwrite existing data, so be sure to use a separate database instance from your main working environment.
