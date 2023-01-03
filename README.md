[![DOI](https://zenodo.org/badge/309797998.svg)](https://zenodo.org/badge/latestdoi/309797998)

# Gene Normalization
Services and guidelines for normalizing gene terms

Installing with pip:

```commandline
pip install gene[dev]
```

The `[dev]` argument tells pip to install packages to fulfill the dependencies of the `gene.etl` package.

## Developer instructions
Following are sections include instructions specifically for developers.

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
exit
```

### Deploying DynamoDB Locally

We use Amazon DynamoDB for our database. To deploy locally, follow [these instructions](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.DownloadingAndRunning.html).

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

By default, tests will employ an existing DynamoDB database. For test environments where this is unavailable (e.g. in CI), the `GENE_TEST` environment variable can be set to initialize a local DynamoDB instance with miniature versions of input data files before tests are executed.

```commandline
export GENE_TEST=true
```

Running unit tests is as easy as pytest.

```commandline
pipenv run pytest
```

### Updating the gene normalization database

Before you use the CLI to update the database, run the following in a separate terminal to start a local DynamoDB service on `port 8000`:

```
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb
```

To change the port, simply add `-port value`.

#### Update source(s)
The sources we currently use are: HGNC, Ensembl, and NCBI.

To update one source, simply set `--normalizer` to the source you wish to update.

From the project root, run the following to update the HGNC source:

```commandline
python3 -m gene.cli --normalizer="hgnc"
```

To update multiple sources, you can use the `--normalizer` flag with the source names separated by spaces.

#### Update all sources

To update all sources, use the `--update_all` flag.

From the project root, run the following to update all sources:

```commandline
python3 -m gene.cli --update_all
```

#### Specifying the database URL endpoint
The default URL endpoint is `http://localhost:8000`.
There are two different ways to specify the database URL endpoint.

The first way is to set the `--db_url` flag to the URL endpoint.
```commandline
python3 -m gene.cli --update_all --db_url="http://localhost:8001"
```

The second way is to set the `GENE_NORM_DB_URL` to the URL endpoint.
```commandline
export GENE_NORM_DB_URL="http://localhost:8001"
python3 -m gene.cli --update_all
```

### Starting the gene normalization service
From the project root, run the following:
```commandline
 uvicorn gene.main:app --reload
```

Next, view the OpenAPI docs on your local machine:

http://127.0.0.1:8000/gene
