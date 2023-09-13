# Gene Normalizer

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gene-normalizer?color=gr) [![tests](https://github.com/cancervariants/gene-normalization/actions/workflows/github-actions.yml/badge.svg)](https://github.com/cancervariants/gene-normalization/actions/workflows/github-actions.yml) [![DOI](https://zenodo.org/badge/309797998.svg)](https://zenodo.org/badge/latestdoi/309797998)

Services and guidelines for normalizing gene terms

## Basic usage

Create a database instance and pass it to the `QueryHandler` constructor:

```
>>> from gene.query import QueryHandler
>>> from gene.database import create_db
>>> q = QueryHandler(create_db())
```

Call the `normalize()` method with a gene term. If available, a rich description of the normalized concept is returned.

```
>>> result = q.normalize("BRAF")
>>> result.gene.id
"hgnc:1097"
>>> result.gene.aliases
['NS7', 'RAFB1', 'B-raf', 'BRAF-1', 'BRAF1', 'B-RAF1']
```

See the [documentation](https://gene-normalizer.readthedocs.io/en/latest/) for more information, or check out the [public REST instance](https://normalize.cancervariants.org/gene) for a live demonstration.

## Installation

The Normalizer is available via PyPI:

```commandline
pip install gene-normalizer[etl,pg]
```

The `[etl,pg]` argument tells pip to install packages to fulfill the dependencies of the `gene.etl` package and the PostgreSQL data storage implementation.

### External requirements

Gene Normalization relies on [SeqRepo](https://github.com/biocommons/biocommons.seqrepo) data, which you must download yourself.

From the _root_ directory:
```
pip install seqrepo
sudo mkdir /usr/local/share/seqrepo
sudo chown $USER /usr/local/share/seqrepo
seqrepo pull -i 2021-01-29  # Replace with latest version using `seqrepo list-remote-instances` if outdated
```

If you get an error similar to the one below:
```
PermissionError: [Error 13] Permission denied: '/usr/local/share/seqrepo/2021-01-29._fkuefgd' -> '/usr/local/share/seqrepo/2021-01-29'
```

You will want to do the following:\
(*Might not be ._fkuefgd, so replace with your error message path*)

```console
sudo mv /usr/local/share/seqrepo/2021-01-29._fkuefgd /usr/local/share/seqrepo/2021-01-29
```

Use the `SEQREPO_ROOT_DIR` environment variable to set the path of an already existing SeqRepo directory. The default is `/usr/local/share/seqrepo/latest`.

### Database Initialization

The Normalizer supports two data storage options:

* [DynamoDB](https://aws.amazon.com/dynamodb), a NoSQL service provided by AWS. This is our preferred storage solution. In addition to cloud deployment, Amazon also provides a tool for local service, which can be installed [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html). Once downloaded, you can start service by running `java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb` in a terminal (add a `-port <VALUE>` option to use a different port)
* [PostgreSQL](https://www.postgresql.org/), a well-known relational database technology. Once starting the Postgres server process, [ensure that a database is created](https://www.postgresql.org/docs/current/sql-createdatabase.html) (we typically name ours `gene_normalizer`).

By default, the Gene Normalizer expects to find a DynamoDB instance listening at `http://localhost:8000`. Alternative locations can be specified in two ways:

The first way is to set the `--db_url` option to the URL endpoint.

```commandline
gene_update --update_all --db_url="http://localhost:8001"
```

The second way is to set the `GENE_NORM_DB_URL` environment variable to the URL endpoint.
```commandline
export GENE_NORM_DB_URL="http://localhost:8001"
```

To use a PostgreSQL instance instead of DynamoDB, provide a PostgreSQL connection URL instead, e.g.

```commandline
export GENE_NORM_DB_URL="postgresql://postgres@localhost:5432/gene_normalizer"
```

### Adding and refreshing data

Use the `gene_update` command in a shell to update the database.

#### Update source(s)

The normalizer currently pulls data from [HGNC](https://www.genenames.org/), [Ensembl](https://useast.ensembl.org/index.html), and [NCBI](https://www.ncbi.nlm.nih.gov/gene/).

To update one source, simply set `--sources` to the source you wish to update. The normalizer will check to see if local source data is up-to-date, acquire the most recent data if not, and use it to populate the database.

For example, run the following to acquire the latest HGNC data if necessary, and update the HGNC gene records in the normalizer database:

```commandline
gene_update --sources="hgnc"
```

To update multiple sources, you can use the `--sources` option with the source names separated by spaces.

#### Update all sources

To update all sources, use the `--update_all` flag:

```commandline
gene_update --update_all
```

### Starting the gene normalization service

Once the Gene Normalizer database has been loaded, from the project root, run the following:

```commandline
uvicorn gene.main:app --reload
```

Next, view the OpenAPI docs on your local machine:

http://127.0.0.1:8000/gene

## Developer instructions
The following sections include instructions specifically for developers.

### Installation
For a development install, we recommend using Pipenv. See the
[pipenv docs](https://pipenv-fork.readthedocs.io/en/latest/#install-pipenv-today)
for direction on installing pipenv in your compute environment.

Once installed, clone the repo and initialize the environment:

```commandline
git clone https://github.com/cancervariants/gene-normalization
cd gene-normalization
pipenv shell
pipenv update
pipenv install --dev
```

Alternatively, install the `pg`, `etl`, `dev`, and `test` dependency groups in a virtual environment:

```commandline
git clone https://github.com/cancervariants/gene-normalization
cd gene-normalization
python3 -m virtualenv venv
source venv/bin/activate
pip install -e ".[pg,etl,dev,test]"
```

### Init coding style tests

Code style is managed by [flake8](https://github.com/PyCQA/flake8) and checked prior to commit.

We use [pre-commit](https://pre-commit.com/#usage) to run conformance tests.

This ensures:

* Check code style
* Check for added large files
* Detect AWS Credentials
* Detect Private Key

Before first commit run:

```commandline
pre-commit install
```

### Running unit tests

By default, tests will employ an existing database. For test environments where this is unavailable (e.g. in CI), the `GENE_TEST` environment variable can be set to initialize a local DynamoDB instance with miniature versions of input data files before tests are executed.

```commandline
export GENE_TEST=true
```

Running unit tests is as easy as pytest.

```commandline
pipenv run pytest
```
