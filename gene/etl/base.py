"""A base class for extraction, transformation, and loading of data."""
from abc import ABC, abstractmethod
from typing import Optional

from gene.database import Database
from gene import PREFIX_LOOKUP
from pathlib import Path
from ftplib import FTP
import gzip
import shutil
from os import remove
from dateutil import parser
import datetime


class Base(ABC):
    """The ETL base class."""

    def __init__(self, database: Database, *args, **kwargs) -> None:
        """Extract from sources."""
        self.database = database

    @abstractmethod
    def _extract_data(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def _transform_data(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def _add_meta(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def _load_meta(self, db, metadata, source_name) -> None:
        """Load source metadata into database.

        :param Database db: DynamoDB Database
        :param SourceMeta metadata: Source's metadata
        :param str source_name: Source to load metadata for
        """
        db.metadata.put_item(Item={
            'src_name': source_name,
            'data_license': metadata.data_license,
            'data_license_url': metadata.data_license_url,
            'version': metadata.version,
            'data_url': metadata.data_url,
            'rdp_url': metadata.rdp_url,
            'data_license_attributes': metadata.data_license_attributes,
            'genome_assemblies': metadata.genome_assemblies
        })

    def _load_gene(self, gene, batch) -> None:
        """Load a gene record into database.

        :param dict gene: Gene record
        :param BatchWriter batch: Object to write data to DynamoDB
        """
        concept_id = gene['concept_id'].lower()
        gene['label_and_type'] = f"{concept_id}##identity"
        gene['src_name'] = \
            PREFIX_LOOKUP[gene['concept_id'].split(':')[0].lower()]
        gene['item_type'] = 'identity'

        attrs = [
            ('symbol', 'symbol'), ('aliases', 'alias'),
            ('previous_symbols', 'prev_symbol'), ('xrefs', 'xref'),
            ('associated_with', 'associated_with')
        ]

        for attr_type, item_type in attrs:
            if attr_type in gene:
                if gene[attr_type] is not None and gene[attr_type] != []:
                    if isinstance(gene[attr_type], str):
                        items = [gene[attr_type].lower()]
                    else:
                        gene[attr_type] = list(set(gene[attr_type]))
                        items = {item.lower() for item in gene[attr_type]}
                    for item in items:
                        batch.put_item(Item={
                            'label_and_type': f"{item}##{item_type}",
                            'concept_id': concept_id,
                            'src_name': gene['src_name'],
                            'item_type': item_type
                        })
                else:
                    del gene[attr_type]
        batch.put_item(Item=gene)

    def _ftp_download(self, host: str, data_dir: str, fn: str,
                      source_dir: Path,
                      data_fn: str) -> Optional[str]:
        """Download data file from FTP site.

        :param str host: Source's FTP host name
        :param str data_dir: Data directory located on FTP site
        :param str fn: Filename for downloaded file
        :param Path source_dir: Source's data directory
        :param str data_fn: Filename on FTP site to be downloaded
        :return: Time file was last updated
        """
        with FTP(host) as ftp:
            ftp.login()
            timestamp = ftp.voidcmd(f'MDTM {data_dir}{data_fn}')[4:].strip()
            date = str(parser.parse(timestamp)).split()[0]
            version = \
                datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')
            ftp.cwd(data_dir)
            if data_fn.endswith('.gz'):
                filepath = source_dir / f'{fn}.gz'
            else:
                filepath = source_dir / fn
            with open(filepath, 'wb') as fp:
                ftp.retrbinary(f'RETR {data_fn}', fp.write)
            if data_fn.endswith('.gz'):
                with gzip.open(filepath, 'rb') as f_in:
                    with open(source_dir / fn, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                remove(filepath)
        return version
