[![DOI](https://zenodo.org/badge/309797998.svg)](https://zenodo.org/badge/latestdoi/309797998)

# Gene Normalizer
Services and guidelines for normalizing gene terms

## Installation

The Normalizer is available via PyPI:

```commandline
pip install gene[dev]
```

The `[dev]` argument tells pip to install packages to fulfill the dependencies of the `gene.etl` package.

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

To update one source, simply set `--normalizer` to the source you wish to update. The normalizer will check to see if local source data is up-to-date, acquire the most recent data if not, and use it to populate the database.

For example, run the following to acquire the latest HGNC data if necessary, and update the HGNC gene records in the normalizer database:

```commandline
gene_update --normalizer="hgnc"
```

To update multiple sources, you can use the `--normalizer` option with the source names separated by spaces.

#### Update all sources

To update all sources, use the `--update_all` flag:

```commandline
gene_update --update_all
```

### Starting the gene normalization service

From the project root, run the following:

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

Once installed, from the project root dir, just run:

```commandline
pipenv shell
pipenv lock && pipenv sync
pipenv install --dev
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
