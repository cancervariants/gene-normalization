"""Add other_id reference to current other identifiers."""
import sys
from pathlib import Path
from timeit import default_timer as timer
import click

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(f"{PROJECT_ROOT}")

from gene.database import Database  # noqa: E402


def add_other_id_refs():
    """Add other_id reference for other_identifiers attribute."""
    db = Database()
    batch = db.genes.batch_writer()

    last_evaluated_key = None
    while True:
        if last_evaluated_key:
            response = db.genes.scan(ExclusiveStartKey=last_evaluated_key)
        else:
            response = db.genes.scan()
        last_evaluated_key = response.get('LastEvaluatedKey')

        records = response['Items']
        for record in records:
            if record['label_and_type'].endswith('##identity'):
                for other_id in record.get('other_identifiers', []):
                    batch.put_item(Item={
                        'label_and_type': f"{other_id.lower()}##other_id",
                        'concept_id': record['concept_id'].lower(),
                        'src_name': record['src_name']
                    })

        if not last_evaluated_key:
            break


if __name__ == '__main__':
    click.echo("Adding other_id references...")
    start = timer()
    add_other_id_refs()
    end = timer()
    click.echo(f"Finished adding other_id references in {end - start:.5f}s.")
