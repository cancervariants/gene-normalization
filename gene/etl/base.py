"""A base class for extraction, transformation, and loading of data."""
from abc import ABC, abstractmethod
from gene.database import Database
from gene import PREFIX_LOOKUP


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
