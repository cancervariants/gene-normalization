# A simple container for gene-service.
# Runs service on port 80.
# Healthchecks service up every 5m.

FROM python:3.7
RUN pip install pipenv uvicorn[standard]
COPY . /app
WORKDIR /app
RUN if [ ! -f "Pipfile.lock" ] ; then pipenv lock ; else echo Pipfile.lock exists ; fi
RUN pipenv sync
EXPOSE 80
RUN apt update ; apt install -y rsync
HEALTHCHECK --interval=5m --timeout=3s \
    CMD curl -f http://localhost/gene || exit 1

CMD pipenv run uvicorn gene.main:app --port 80 --host 0.0.0.0
