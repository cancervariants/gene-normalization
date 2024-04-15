Contributing to the Gene Normalizer
===================================

Bug reports and feature requests
--------------------------------

Bugs and new feature requests can be submitted to the Gene Normalizer `issue tracker on GitHub <https://github.com/cancervariants/gene-normalization/issues>`_. See `this StackOverflow post <https://stackoverflow.com/help/minimal-reproducible-example>`_ for tips on how to craft a helpful bug report.

Development prerequisites
-------------------------
For a development install, we recommend using Pipenv. See the `Pipenv docs <https://pipenv-fork.readthedocs.io/en/latest/#install-pipenv-today>`_ for direction on installing Pipenv in your environment.

Setup
-----
Clone the repository: ::

    git clone https://github.com/cancervariants/gene-normalization
    cd gene-normalization

Then initialize the Pipenv environment: ::

    pipenv update
    pipenv install --dev
    pipenv shell

Alternatively, use a virtual environment and install all dependency groups: ::

    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install -e ".[pg,etl,test,dev,docs]"

We use `pre-commit <https://pre-commit.com/#usage>`_ to run conformance tests before commits. This provides checks for:

* Code format and style
* Added large files
* AWS credentials
* Private keys

Before your first commit, run: ::

    pre-commit install

When running the web server, enable hot-reloading on new code changes: ::

    uvicorn gene.main:app --reload


Style
-----

Code style is managed by `Ruff <https://github.com/astral-sh/ruff>`_, and should be checked via pre-commit hook before commits. Final QC is applied with GitHub Actions to every pull request.

Tests
-----

Tests are executed with `pytest <https://docs.pytest.org/en/7.1.x/getting-started.html>`_: ::

    pytest

By default, tests will utilize an existing database, and won't load any new data. For test environments where this is unavailable (e.g. in CI), the `GENE_TEST` environment variable can be set to `'true'` to initialize the connected database instance with miniature versions of input data files before tests are executed: ::

    export GENE_TEST=true

.. warning::

    Tests executed under the GENE_TEST environment will overwrite existing data. It is recommend that a database instance separate from the main working environment is used.


Documentation
-------------

The documentation is built with Sphinx, which is included as part of the Pipenv developer dependencies, or in the ``docs`` dependency group. Navigate to the `docs/` subdirectory and use `make` to build the HTML version: ::

    pipenv shell
    cd docs
    make html

See the `Sphinx documentation <https://www.sphinx-doc.org/en/master/>`_ for more information.

Figure generation
_________________

We are experimenting with the inclusion of some static HTML figures in the documentation. For now, scripts used to generate these figures should be provided in ``docs/scripts/``, and any external dependencies should be included in the ``docs`` dependency group.
