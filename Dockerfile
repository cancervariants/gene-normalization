# A simple container for gene-normalizer service.
# Runs service on port 80.
# Health checks service up every 5m.

FROM python:3.12-slim

WORKDIR /app

ARG IS_DEV_ENV="false"

ARG VERSION

ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_GENE_NORMALIZER=$VERSION

RUN if [ $IS_DEV_ENV = "true" ]; then \
    apt update ; apt install -y rsync ; \
  fi

COPY src/ ./src/
COPY pyproject.toml gene-norm-update.sh ./

RUN pip install --upgrade pip setuptools setuptools_scm
RUN if [ $IS_DEV_ENV = "true" ]; then \
    pip install --no-cache-dir '.[etl]'; \
  else \
    pip install --no-cache-dir '.'; \
  fi

EXPOSE 80
HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost/gene || exit 1

CMD ["uvicorn", "gene.main:app", "--port", "80", "--host", "0.0.0.0"]
