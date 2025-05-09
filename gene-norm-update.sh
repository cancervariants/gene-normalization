#!/bin/sh

gene-normalizer check-db
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "Data already exists. Skipping ETL."
else
  echo "Database status check failed. Running ETL..."
  gene-normalizer update --all --normalize
  echo "ETL completed."
fi

exec uvicorn gene.main:app  --port 80 --host 0.0.0.0
