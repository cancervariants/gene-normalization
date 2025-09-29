"""Test utils module"""

import pytest
from deepdiff import DeepDiff

from gene.database.database import AbstractDatabase
from gene.schemas import RecordType, SourceName
from gene.utils import get_term_mappings


@pytest.fixture(scope="module")
def test_db(null_database_class):
    return null_database_class(
        get_all_records={
            RecordType.IDENTITY: [
                {
                    "concept_id": "hgnc:3236",
                    "symbol_status": "approved",
                    "label": "epidermal growth factor receptor",
                    "gene_type": "gene with protein product",
                    "aliases": ["ERRP", "ERBB1"],
                    "associated_with": [
                        "orphanet:121311",
                        "uniprot:P00533",
                        "refseq:NM_005228",
                        "iuphar:1797",
                        "omim:131550",
                        "ucsc:uc003tqk.4",
                        "pubmed:1505215",
                        "cosmic:EGFR",
                        "vega:OTTHUMG00000023661",
                    ],
                    "previous_symbols": ["ERBB"],
                    "symbol": "EGFR",
                    "xrefs": ["ensembl:ENSG00000146648", "ncbigene:1956"],
                    "src_name": "HGNC",
                    "merge_ref": "hgnc:3236",
                    "item_type": "identity",
                },
                {
                    "concept_id": "ensembl:ENSG00000146648",
                    "label": "epidermal growth factor receptor",
                    "strand": "+",
                    "locations": [
                        {
                            "type": "SequenceLocation",
                            "start": 55019016,
                            "end": 55211628,
                            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        }
                    ],
                    "gene_type": "protein_coding",
                    "symbol": "EGFR",
                    "xrefs": ["hgnc:3236"],
                    "src_name": "Ensembl",
                    "merge_ref": "hgnc:3236",
                    "item_type": "identity",
                },
                {
                    "concept_id": "ncbigene:1956",
                    "label": "epidermal growth factor receptor",
                    "strand": "+",
                    "locations": [
                        {
                            "type": "SequenceLocation",
                            "start": 55019016,
                            "end": 55211628,
                            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        }
                    ],
                    "gene_type": "protein-coding",
                    "aliases": [
                        "PIG61",
                        "NISBD2",
                        "HER1",
                        "NNCIS",
                        "ERBB",
                        "ERRP",
                        "mENA",
                        "ERBB1",
                    ],
                    "associated_with": ["omim:131550"],
                    "symbol": "EGFR",
                    "xrefs": ["hgnc:3236", "ensembl:ENSG00000146648"],
                    "src_name": "NCBI",
                    "merge_ref": "hgnc:3236",
                    "item_type": "identity",
                },
                {
                    "concept_id": "ncbigene:673",
                    "label": "B-Raf proto-oncogene, serine/threonine kinase",
                    "strand": "-",
                    "locations": [
                        {
                            "type": "SequenceLocation",
                            "start": 140713327,
                            "end": 140924929,
                            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        }
                    ],
                    "gene_type": "protein-coding",
                    "aliases": ["B-RAF1", "BRAF-1", "B-raf", "RAFB1", "NS7", "BRAF1"],
                    "associated_with": ["omim:164757"],
                    "symbol": "BRAF",
                    "xrefs": ["hgnc:1097", "ensembl:ENSG00000157764"],
                    "src_name": "NCBI",
                    "merge_ref": "hgnc:1097",
                    "item_type": "identity",
                },
                {
                    "concept_id": "ensembl:ENSG00000157764",
                    "label": "B-Raf proto-oncogene, serine/threonine kinase",
                    "strand": "-",
                    "locations": [
                        {
                            "type": "SequenceLocation",
                            "start": 140719326,
                            "end": 140924929,
                            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        }
                    ],
                    "gene_type": "protein_coding",
                    "symbol": "BRAF",
                    "xrefs": ["hgnc:1097"],
                    "src_name": "Ensembl",
                    "merge_ref": "hgnc:1097",
                    "item_type": "identity",
                },
                {
                    "concept_id": "hgnc:1097",
                    "symbol_status": "approved",
                    "label": "B-Raf proto-oncogene, serine/threonine kinase",
                    "gene_type": "gene with protein product",
                    "aliases": ["BRAF1", "BRAF-1"],
                    "associated_with": [
                        "iuphar:1943",
                        "pubmed:1565476",
                        "cosmic:BRAF",
                        "orphanet:119066",
                        "vega:OTTHUMG00000157457",
                        "pubmed:2284096",
                        "refseq:NM_004333",
                        "omim:164757",
                        "ena.embl:M95712",
                        "uniprot:P15056",
                        "ucsc:uc003vwc.5",
                    ],
                    "symbol": "BRAF",
                    "xrefs": ["ensembl:ENSG00000157764", "ncbigene:673"],
                    "src_name": "HGNC",
                    "merge_ref": "hgnc:1097",
                    "item_type": "identity",
                },
                {
                    "concept_id": "ensembl:ENSG00000231995",
                    "label": "ribosomal protein L7a pseudogene 76",
                    "strand": "+",
                    "locations": [
                        {
                            "type": "SequenceLocation",
                            "start": 62266318,
                            "end": 62266919,
                            "sequence_id": "ga4gh:SQ.KEO-4XBcm1cxeo_DIQ8_ofqGUkp4iZhI",
                        }
                    ],
                    "gene_type": "transcribed_processed_pseudogene",
                    "symbol": "RPL7AP76",
                    "xrefs": ["hgnc:55899"],
                    "src_name": "Ensembl",
                    "merge_ref": "hgnc:55899",
                    "item_type": "identity",
                },
            ],
            RecordType.MERGER: [
                {
                    "concept_id": "hgnc:1097",
                    "symbol": "BRAF",
                    "symbol_status": "approved",
                    "label": "B-Raf proto-oncogene, serine/threonine kinase",
                    "strand": "-",
                    "ensembl_locations": [
                        {
                            "type": "SequenceLocation",
                            "start": 140719326,
                            "end": 140924929,
                            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        }
                    ],
                    "ncbi_locations": [
                        {
                            "type": "SequenceLocation",
                            "start": 140713327,
                            "end": 140924929,
                            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        }
                    ],
                    "ensembl_biotype": ["protein_coding"],
                    "hgnc_locus_type": ["gene with protein product"],
                    "ncbi_gene_type": ["protein-coding"],
                    "aliases": ["B-RAF1", "BRAF-1", "B-raf", "RAFB1", "NS7", "BRAF1"],
                    "associated_with": [
                        "iuphar:1943",
                        "pubmed:1565476",
                        "cosmic:BRAF",
                        "orphanet:119066",
                        "vega:OTTHUMG00000157457",
                        "pubmed:2284096",
                        "refseq:NM_004333",
                        "omim:164757",
                        "ena.embl:M95712",
                        "uniprot:P15056",
                        "ucsc:uc003vwc.5",
                    ],
                    "xrefs": ["ensembl:ENSG00000157764", "ncbigene:673"],
                    "item_type": "merger",
                },
                {
                    "concept_id": "hgnc:3236",
                    "symbol": "EGFR",
                    "symbol_status": "approved",
                    "previous_symbols": ["ERBB"],
                    "label": "epidermal growth factor receptor",
                    "strand": "+",
                    "ensembl_locations": [
                        {
                            "type": "SequenceLocation",
                            "start": 55019016,
                            "end": 55211628,
                            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        }
                    ],
                    "ncbi_locations": [
                        {
                            "type": "SequenceLocation",
                            "start": 55019016,
                            "end": 55211628,
                            "sequence_id": "ga4gh:SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        }
                    ],
                    "ensembl_biotype": ["protein_coding"],
                    "hgnc_locus_type": ["gene with protein product"],
                    "ncbi_gene_type": ["protein-coding"],
                    "aliases": [
                        "PIG61",
                        "NISBD2",
                        "HER1",
                        "NNCIS",
                        "ERBB",
                        "ERRP",
                        "mENA",
                        "ERBB1",
                    ],
                    "associated_with": [
                        "orphanet:121311",
                        "uniprot:P00533",
                        "refseq:NM_005228",
                        "iuphar:1797",
                        "omim:131550",
                        "ucsc:uc003tqk.4",
                        "cosmic:EGFR",
                        "pubmed:1505215",
                        "vega:OTTHUMG00000023661",
                    ],
                    "xrefs": ["ncbigene:1956", "ensembl:ENSG00000146648"],
                    "item_type": "merger",
                },
                {
                    "concept_id": "ncbigene:3378",
                    "label": "inflammatory bowel disease 2",
                    "gene_type": "unknown",
                    "associated_with": ["omim:601458"],
                    "symbol": "IBD2",
                    "src_name": "NCBI",
                    "item_type": "identity",
                },
            ],
        }
    )


def test_get_term_mappings_hgnc(test_db: AbstractDatabase):
    results = list(get_term_mappings(test_db, SourceName.HGNC))

    mappings_fixture = [
        {
            "concept_id": "hgnc:3236",
            "symbol": "EGFR",
            "label": "epidermal growth factor receptor",
            "aliases": ["ERRP", "ERBB1"],
            "xrefs": [
                "ensembl:ENSG00000146648",
                "ncbigene:1956",
                "orphanet:121311",
                "uniprot:P00533",
                "refseq:NM_005228",
                "iuphar:1797",
                "omim:131550",
                "ucsc:uc003tqk.4",
                "pubmed:1505215",
                "cosmic:EGFR",
                "vega:OTTHUMG00000023661",
            ],
            "previous_symbols": ["ERBB"],
        },
        {
            "concept_id": "hgnc:1097",
            "symbol": "BRAF",
            "label": "B-Raf proto-oncogene, serine/threonine kinase",
            "aliases": ["BRAF1", "BRAF-1"],
            "previous_symbols": [],
            "xrefs": [
                "iuphar:1943",
                "pubmed:1565476",
                "cosmic:BRAF",
                "orphanet:119066",
                "vega:OTTHUMG00000157457",
                "pubmed:2284096",
                "refseq:NM_004333",
                "omim:164757",
                "ena.embl:M95712",
                "uniprot:P15056",
                "ucsc:uc003vwc.5",
                "ensembl:ENSG00000157764",
                "ncbigene:673",
            ],
        },
    ]
    diff = DeepDiff(mappings_fixture, results, ignore_order=True)
    assert diff == {}


def test_get_term_mappings_merger(test_db: AbstractDatabase):
    results = list(get_term_mappings(test_db, scope=RecordType.MERGER))

    fixture = [
        {
            "concept_id": "hgnc:1097",
            "symbol": "BRAF",
            "label": "B-Raf proto-oncogene, serine/threonine kinase",
            "aliases": ["B-RAF1", "BRAF-1", "B-raf", "RAFB1", "NS7", "BRAF1"],
            "xrefs": [
                "iuphar:1943",
                "pubmed:1565476",
                "cosmic:BRAF",
                "orphanet:119066",
                "vega:OTTHUMG00000157457",
                "pubmed:2284096",
                "refseq:NM_004333",
                "omim:164757",
                "ena.embl:M95712",
                "uniprot:P15056",
                "ucsc:uc003vwc.5",
                "ensembl:ENSG00000157764",
                "ncbigene:673",
            ],
            "previous_symbols": [],
        },
        {
            "concept_id": "hgnc:3236",
            "symbol": "EGFR",
            "previous_symbols": ["ERBB"],
            "label": "epidermal growth factor receptor",
            "aliases": [
                "PIG61",
                "NISBD2",
                "HER1",
                "NNCIS",
                "ERBB",
                "ERRP",
                "mENA",
                "ERBB1",
            ],
            "xrefs": [
                "orphanet:121311",
                "uniprot:P00533",
                "refseq:NM_005228",
                "iuphar:1797",
                "omim:131550",
                "ucsc:uc003tqk.4",
                "cosmic:EGFR",
                "pubmed:1505215",
                "vega:OTTHUMG00000023661",
                "ncbigene:1956",
                "ensembl:ENSG00000146648",
            ],
        },
        {
            "aliases": [],
            "concept_id": "ncbigene:3378",
            "label": "inflammatory bowel disease 2",
            "previous_symbols": [],
            "symbol": "IBD2",
            "xrefs": [
                "omim:601458",
            ],
        },
    ]
    diff = DeepDiff(fixture, results, ignore_order=True)
    assert diff == {}


def test_get_term_mappings_protein_coding_only(test_db: AbstractDatabase):
    results = list(
        get_term_mappings(test_db, scope=RecordType.IDENTITY, protein_coding_only=True)
    )
    assert len(results) == 6
    assert "ensembl:ENSG00000231995" not in [r["concept_id"] for r in results]

    results = list(
        get_term_mappings(test_db, scope=RecordType.MERGER, protein_coding_only=True)
    )
    assert len(results) == 2
    assert "ncbigene:3378" not in [r["concept_id"] for r in results]
