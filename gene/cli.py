"""This module provides a CLI util to make updates to normalizer database."""
import click
from botocore.exceptions import ClientError
from gene.etl import HGNC, Ensembl, NCBI
from gene.schemas import SourceName
from timeit import default_timer as timer
from gene.database import Database
from boto3.dynamodb.conditions import Key
from os import environ


class CLI:
    """Class for updating the normalizer database via Click"""

    @staticmethod
    @click.command()
    @click.option(
        '--normalizer',
        help="The normalizer(s) you wish to update separated by spaces."
    )
    @click.option(
        '--prod',
        is_flag=True,
        help="Working in production environment."
    )
    @click.option(
        '--db_url',
        help="URL endpoint for the application database."
    )
    @click.option(
        '--update_all',
        is_flag=True,
        help='Update all normalizer sources.'
    )
    def update_normalizer_db(normalizer, prod, db_url, update_all):
        """Update selected normalizer source(s) in the gene database."""
        sources = {
            'hgnc': HGNC,
            'ensembl': Ensembl,
            'ncbi': NCBI
        }
        if prod:
            environ['GENE_NORM_PROD'] = "TRUE"
            db: Database = Database()
        else:
            if db_url:
                endpoint_url = db_url
            elif 'GENE_NORM_DB_URL' in environ.keys():
                endpoint_url = environ['GENE_NORM_DB_URL']
            else:
                endpoint_url = 'http://localhost:8000'
            db: Database = Database(db_url=endpoint_url)

        if update_all:
            normalizers = [src for src in sources]
            CLI()._update_normalizers(normalizers, sources, db)
        elif not normalizer:
            CLI()._help_msg()
        else:
            normalizers = normalizer.lower().split()

            if len(normalizers) == 0:
                raise Exception("Must enter a normalizer")

            non_sources = set(normalizers) - {src for src in sources}

            if len(non_sources) != 0:
                raise Exception(f"Not valid source(s): {non_sources}")

            CLI()._update_normalizers(normalizers, sources, db)

    @staticmethod
    def _help_msg():
        """Display help message."""
        ctx = click.get_current_context()
        click.echo(
            "Must either enter 1 or more sources, or use `--update_all` parameter")  # noqa: E501
        click.echo(ctx.get_help())
        ctx.exit()

    @staticmethod
    def _update_normalizers(normalizers, sources, db):
        """Update selected normalizer sources."""
        for n in normalizers:
            click.echo(f"\nDeleting {n}...")
            start_delete = timer()
            CLI()._delete_data(n, db)
            end_delete = timer()
            delete_time = end_delete - start_delete
            click.echo(f"Deleted {n} in "
                       f"{delete_time:.5f} seconds.\n")
            click.echo(f"Loading {n}...")
            start_load = timer()
            sources[n](database=db)
            end_load = timer()
            load_time = end_load - start_load
            click.echo(f"Loaded {n} in {load_time:.5f} seconds.")
            click.echo(f"Total time for {n}: "
                       f"{(delete_time + load_time):.5f} seconds.")

    @staticmethod
    def _delete_data(source, database):
        # Delete source's metadata
        try:
            metadata = database.metadata.query(
                KeyConditionExpression=Key(
                    'src_name').eq(SourceName[f"{source.upper()}"].value)
            )
            if metadata['Items']:
                database.metadata.delete_item(
                    Key={'src_name': metadata['Items'][0]['src_name']},
                    ConditionExpression="src_name = :src",
                    ExpressionAttributeValues={
                        ':src': SourceName[f"{source.upper()}"].value}
                )
        except ClientError as e:
            click.echo(e.response['Error']['Message'])

        # Delete source's data from genes table
        try:
            while True:
                response = database.genes.query(
                    IndexName='src_index',
                    KeyConditionExpression=Key('src_name').eq(
                        SourceName[f"{source.upper()}"].value)
                )

                records = response['Items']
                if not records:
                    break

                with database.genes.batch_writer(
                        overwrite_by_pkeys=['label_and_type', 'concept_id']) \
                        as batch:

                    for record in records:
                        batch.delete_item(
                            Key={
                                'label_and_type': record['label_and_type'],
                                'concept_id': record['concept_id']
                            }
                        )
        except ClientError as e:
            click.echo(e.response['Error']['Message'])


if __name__ == '__main__':
    CLI().update_normalizer_db()
