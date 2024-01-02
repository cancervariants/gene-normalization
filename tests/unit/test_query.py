"""Module to test the query module."""
import pytest
from ga4gh.core import core_models

from gene.query import QueryHandler
from gene.schemas import BaseGene, MatchType, SourceName


@pytest.fixture(scope="module")
def query_handler(database):
    """Build query_handler test fixture."""

    class QueryGetter:
        def __init__(self):
            self.query_handler = QueryHandler(database)

        def search(self, query_str, sources=None):
            return self.query_handler.search(query=query_str, sources=sources)

        def normalize(self, query_str):
            return self.query_handler.normalize(query_str)

        def normalize_unmerged(self, query_str):
            return self.query_handler.normalize_unmerged(query_str)

    return QueryGetter()


@pytest.fixture(scope="module")
def normalized_ache():
    """Return normalized core Gene object for ACHE."""
    params = {
        "type": "Gene",
        "id": "normalize.gene.hgnc:108",
        "label": "ACHE",
        "mappings": [
            {
                "coding": {"code": "ENSG00000087085", "system": "ensembl"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "43", "system": "ncbigene"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "OTTHUMG00000157033", "system": "vega"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "uc003uxi.4", "system": "ucsc"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "CCDS5710", "system": "ccds"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "CCDS64736", "system": "ccds"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "CCDS5709", "system": "ccds"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "P22303", "system": "uniprot"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "1380483", "system": "pubmed"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "100740", "system": "omim"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "S09.979", "system": "merops"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "2465", "system": "iuphar"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "NM_015831", "system": "refseq"},
                "relation": "relatedMatch",
            },
        ],
        "aliases": ["3.1.1.7", "YT", "N-ACHE", "ARACHE", "ACEE"],
        "extensions": [
            {"name": "previous_symbols", "value": ["ACEE", "YT"], "type": "Extension"},
            {
                "name": "approved_name",
                "value": "acetylcholinesterase (Cartwright blood group)",
                "type": "Extension",
            },
            {"name": "symbol_status", "value": "approved", "type": "Extension"},
            {
                "name": "ncbi_locations",
                "value": [
                    # {
                    #     "id": "ga4gh:CL.JSw-08GkF-7M-OQR-33MLLKQHSi7QJb5",
                    #     "type": "ChromosomeLocation",
                    #     "species_id": "taxonomy:9606",
                    #     "chr": "7",
                    #     "end": "q22.1",
                    #     "start": "q22.1"
                    # },
                    {
                        "id": "ga4gh:SL.U7vPSlX8eyCKdFSiROIsc9om0Y7pCm2g",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        },
                        "start": 100889993,
                        "end": 100896994,
                    }
                ],
                "type": "Extension",
            },
            # {
            #     "name": "hgnc_locations",
            #     "value": [
            #         {
            #             "id": "ga4gh:CL.JSw-08GkF-7M-OQR-33MLLKQHSi7QJb5",
            #             "type": "ChromosomeLocation",
            #             "species_id": "taxonomy:9606",
            #             "chr": "7",
            #             "start": "q22.1",
            #             "end": "q22.1"
            #         }
            #     ],
            #     "type": "Extension"
            # },
            {
                "name": "ensembl_locations",
                "value": [
                    {
                        "id": "ga4gh:SL.dnydHb2Bnv5pwXjI4MpJmrZUADf5QLe1",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        },
                        "start": 100889993,
                        "end": 100896974,
                    }
                ],
                "type": "Extension",
            },
            {"name": "ncbi_gene_type", "type": "Extension", "value": "protein-coding"},
            {
                "name": "hgnc_locus_type",
                "type": "Extension",
                "value": "gene with protein product",
            },
            {"name": "ensembl_biotype", "type": "Extension", "value": "protein_coding"},
            {"name": "strand", "type": "Extension", "value": "-"},
        ],
    }
    return core_models.Gene(**params)


@pytest.fixture(scope="module")
def normalized_braf():
    """Return normalized core Gene object for BRAF."""
    params = {
        "type": "Gene",
        "id": "normalize.gene.hgnc:1097",
        "label": "BRAF",
        "mappings": [
            {
                "coding": {"code": "673", "system": "ncbigene"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "ENSG00000157764", "system": "ensembl"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "CCDS5863", "system": "ccds"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "1943", "system": "iuphar"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "119066", "system": "orphanet"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "BRAF", "system": "cosmic"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "2284096", "system": "pubmed"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "uc003vwc.5", "system": "ucsc"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "164757", "system": "omim"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "NM_004333", "system": "refseq"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "CCDS87555", "system": "ccds"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "P15056", "system": "uniprot"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "M95712", "system": "ena.embl"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "OTTHUMG00000157457", "system": "vega"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "1565476", "system": "pubmed"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "CCDS94219", "system": "ccds"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "CCDS94218", "system": "ccds"},
                "relation": "relatedMatch",
            },
        ],
        "aliases": ["BRAF1", "BRAF-1", "RAFB1", "NS7", "B-RAF1", "B-raf"],
        "extensions": [
            {
                "name": "approved_name",
                "value": "B-Raf proto-oncogene, serine/threonine kinase",
                "type": "Extension",
            },
            # {
            #     "name": "hgnc_locations",
            #     "value": [
            #         {
            #             "id": "ga4gh:CL.ZZZYpOwuW1BLLJXc_Dm4eVZ5E0smVYCc",
            #             "type": "ChromosomeLocation",
            #             "species_id": "taxonomy:9606",
            #             "chr": "7",
            #             "end": "q34",
            #             "start": "q34",
            #         }
            #     ],
            #     "type": "Extension"
            # },
            {
                "name": "ensembl_locations",
                "value": [
                    {
                        "id": "ga4gh:SL.WJ0hsPzXuK54mQyVysTqUNV5jaCATnRf",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        },
                        "start": 140719326,
                        "end": 140924929,
                    }
                ],
                "type": "Extension",
            },
            {
                "name": "ncbi_locations",
                "value": [
                    # {
                    #     "id": "ga4gh:CL.ZZZYpOwuW1BLLJXc_Dm4eVZ5E0smVYCc",
                    #     "type": "ChromosomeLocation",
                    #     "species_id": "taxonomy:9606",
                    #     "chr": "7",
                    #     "start": "q34",
                    #     "end": "q34"
                    # },
                    {
                        "id": "ga4gh:SL.uNBZoxhjhohl24VlIut-JxPJAGfJ7EQE",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        },
                        "start": 140713327,
                        "end": 140924929,
                    }
                ],
                "type": "Extension",
            },
            {"name": "ncbi_gene_type", "type": "Extension", "value": "protein-coding"},
            {
                "name": "hgnc_locus_type",
                "type": "Extension",
                "value": "gene with protein product",
            },
            {"name": "ensembl_biotype", "type": "Extension", "value": "protein_coding"},
            {"name": "strand", "type": "Extension", "value": "-"},
            {"name": "symbol_status", "type": "Extension", "value": "approved"},
        ],
    }
    return core_models.Gene(**params)


@pytest.fixture(scope="module")
def normalized_abl1():
    """Return normalized core Gene object for ABL1."""
    params = {
        "type": "Gene",
        "id": "normalize.gene.hgnc:76",
        "label": "ABL1",
        "mappings": [
            {
                "coding": {"code": "ENSG00000097007", "system": "ensembl"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "25", "system": "ncbigene"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "OTTHUMG00000020813", "system": "vega"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "uc004bzv.4", "system": "ucsc"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "CCDS35166", "system": "ccds"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "CCDS35165", "system": "ccds"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "P00519", "system": "uniprot"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "1857987", "system": "pubmed"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "12626632", "system": "pubmed"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "ABL1", "system": "cosmic"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "189980", "system": "omim"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "117691", "system": "orphanet"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "1923", "system": "iuphar"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "M14752", "system": "ena.embl"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "NM_007313", "system": "refseq"},
                "relation": "relatedMatch",
            },
        ],
        "aliases": [
            "c-ABL",
            "JTK7",
            "p150",
            "CHDSKM",
            "BCR-ABL",
            "v-abl",
            "c-ABL1",
            "bcr/abl",
            "LOC116063",
            "LOC112779",
            "ABL",
        ],
        "extensions": [
            {
                "name": "previous_symbols",
                "value": ["LOC116063", "LOC112779", "ABL"],
                "type": "Extension",
            },
            {
                "name": "approved_name",
                "value": "ABL proto-oncogene 1, non-receptor tyrosine kinase",
                "type": "Extension",
            },
            # {
            #     "name": "hgnc_locations",
            #     "value": [
            #         {
            #             "id": "ga4gh:CL.1vsxettosueUHyFIOoTPzwIFD1DodLuT",
            #             "type": "ChromosomeLocation",
            #             "species_id": "taxonomy:9606",
            #             "chr": "9",
            #             "end": "q34.12",
            #             "start": "q34.12"
            #         }
            #     ],
            #     "type": "Extension"
            # },
            {
                "name": "ncbi_locations",
                "value": [
                    # {
                    #     "id": "ga4gh:CL.1vsxettosueUHyFIOoTPzwIFD1DodLuT",
                    #     "type": "ChromosomeLocation",
                    #     "species_id": "taxonomy:9606",
                    #     "chr": "9",
                    #     "start": "q34.12",
                    #     "end": "q34.12"
                    # },
                    {
                        "id": "ga4gh:SL.F1QUtInXQaBEjAJNR1sYHXdp0XC000Qi",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.KEO-4XBcm1cxeo_DIQ8_ofqGUkp4iZhI",
                        },
                        "start": 130713042,
                        "end": 130887675,
                    }
                ],
                "type": "Extension",
            },
            {
                "name": "ensembl_locations",
                "value": [
                    {
                        "id": "ga4gh:SL.P9Qu87GYxoWPYh1BdAQC5bTLorjvvye7",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.KEO-4XBcm1cxeo_DIQ8_ofqGUkp4iZhI",
                        },
                        "start": 130713015,
                        "end": 130887675,
                    }
                ],
                "type": "Extension",
            },
            {"name": "ncbi_gene_type", "type": "Extension", "value": "protein-coding"},
            {
                "name": "hgnc_locus_type",
                "type": "Extension",
                "value": "gene with protein product",
            },
            {"name": "ensembl_biotype", "type": "Extension", "value": "protein_coding"},
            {"name": "strand", "type": "Extension", "value": "+"},
            {"name": "symbol_status", "type": "Extension", "value": "approved"},
        ],
    }
    return core_models.Gene(**params)


@pytest.fixture(scope="module")
def normalized_p150():
    """Return normalized core Gene object for p150."""
    params = {
        "type": "Gene",
        "id": "normalize.gene.hgnc:1910",
        "label": "CHAF1A",
        "mappings": [
            {
                "coding": {"code": "ENSG00000167670", "system": "ensembl"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "10036", "system": "ncbigene"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "601246", "system": "omim"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "CCDS32875", "system": "ccds"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "7600578", "system": "pubmed"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "OTTHUMG00000181922", "system": "vega"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "Q13111", "system": "uniprot"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "NM_005483", "system": "refseq"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "U20979", "system": "ena.embl"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "uc002mal.4", "system": "ucsc"},
                "relation": "relatedMatch",
            },
        ],
        "aliases": [
            "CAF1P150",
            "MGC71229",
            "CAF-1",
            "P150",
            "CAF1B",
            "CAF1",
            "LOC107985297",
        ],
        "extensions": [
            {
                "name": "approved_name",
                "value": "chromatin assembly factor 1 subunit A",
                "type": "Extension",
            },
            # {
            #     "name": "hgnc_locations",
            #     "value": [
            #         {
            #             "id": "ga4gh:CL.kPEG2TGUPOAsAYK6HY0ukprQ-DR_IuMZ",
            #             "type": "ChromosomeLocation",
            #             "species_id": "taxonomy:9606",
            #             "chr": "19",
            #             "end": "p13.3",
            #             "start": "p13.3"
            #         }
            #     ],
            #     "type": "Extension"
            # },
            {
                "name": "ensembl_locations",
                "value": [
                    {
                        "id": "ga4gh:SL.tLUFh2LAYq-bsMi0Vob_TIWrz-sE4HgE",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl",
                        },
                        "start": 4402639,
                        "end": 4445018,
                    }
                ],
            },
            {
                "name": "ncbi_locations",
                "value": [
                    # {
                    #     "id": "ga4gh:CL.kPEG2TGUPOAsAYK6HY0ukprQ-DR_IuMZ",
                    #     "type": "ChromosomeLocation",
                    #     "species_id": "taxonomy:9606",
                    #     "chr": "19",
                    #     "start": "p13.3",
                    #     "end": "p13.3"
                    # },
                    {
                        "id": "ga4gh:SL.-3T7UXNk6nIkMKB9YGEb0RTYxbVY2TUy",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl",
                        },
                        "start": 4402639,
                        "end": 4450830,
                    }
                ],
            },
            {"name": "ncbi_gene_type", "type": "Extension", "value": "protein-coding"},
            {
                "name": "hgnc_locus_type",
                "type": "Extension",
                "value": "gene with protein product",
            },
            {"name": "ensembl_biotype", "type": "Extension", "value": "protein_coding"},
            {
                "name": "previous_symbols",
                "type": "Extension",
                "value": ["LOC107985297"],
            },
            {"name": "strand", "type": "Extension", "value": "+"},
            {"name": "symbol_status", "type": "Extension", "value": "approved"},
        ],
    }
    return core_models.Gene(**params)


@pytest.fixture(scope="module")
def normalized_loc_653303():
    """Provide test fixture for NCBI gene LOC653303. Used to validate
    normalized results that don't merge records.
    """
    params = {
        "type": "Gene",
        "label": "LOC653303",
        "aliases": ["LOC196266", "LOC654080", "LOC731196"],
        "extensions": [
            {
                "type": "Extension",
                "name": "approved_name",
                "value": "proprotein convertase subtilisin/kexin type 7 pseudogene",
            },
            {
                "name": "ncbi_locations",
                "value": [
                    # {
                    #     "id": "ga4gh:CL.82tL1yxucvwp5U2Yo4jNYX06pru8zZYl",
                    #     "type": "ChromosomeLocation",
                    #     "species_id": "taxonomy:9606",
                    #     "chr": "11",
                    #     "start": "q23.3",
                    #     "end": "q23.3"
                    # },
                    {
                        "id": "ga4gh:SL.hgpw5EH5q6_PFX1CTcOx5od0LKUQRuDH",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.2NkFm8HK88MqeNkCgj78KidCAXgnsfV1",
                        },
                        "start": 117135528,
                        "end": 117138867,
                    }
                ],
            },
            {
                "type": "Extension",
                "name": "previous_symbols",
                "value": ["LOC196266", "LOC731196", "LOC654080"],
            },
            {"type": "Extension", "name": "ncbi_gene_type", "value": "pseudo"},
            {"name": "strand", "type": "Extension", "value": "+"},
        ],
        "id": "normalize.gene.ncbigene:653303",
    }
    return core_models.Gene(**params)


@pytest.fixture(scope="module")
def normalize_unmerged_loc_653303():
    """Provide fixture for NCBI gene LOC655303. Used to validate normalized results
    that don't merge records.
    """
    return {
        "normalized_concept_id": "ncbigene:653303",
        "source_matches": {
            "NCBI": {
                "records": [
                    {
                        "concept_id": "ncbigene:653303",
                        "symbol": "LOC653303",
                        "symbol_status": None,
                        "label": "proprotein convertase subtilisin/kexin type 7 pseudogene",  # noqa: E501
                        "strand": "+",
                        "location_annotations": [],
                        "locations": [
                            # {
                            #     "type": "ChromosomeLocation",
                            #     "id": "ga4gh:CL.82tL1yxucvwp5U2Yo4jNYX06pru8zZYl",
                            #     "species_id": "taxonomy:9606",
                            #     "chr": "11",
                            #     "start": "q23.3",
                            #     "end": "q23.3"
                            # },
                            {
                                "id": "ga4gh:SL.hgpw5EH5q6_PFX1CTcOx5od0LKUQRuDH",
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.2NkFm8HK88MqeNkCgj78KidCAXgnsfV1",  # noqa: E501
                                },
                                "start": 117135528,
                                "end": 117138867,
                            }
                        ],
                        "aliases": [],
                        "previous_symbols": ["LOC196266", "LOC731196", "LOC654080"],
                        "xrefs": [],
                        "associated_with": [],
                        "gene_type": "pseudo",
                    }
                ]
            }
        },
    }


@pytest.fixture(scope="module")
def normalize_unmerged_chaf1a():
    """Return expected results from /normalize_unmerged for CHAF1A."""
    return {
        "normalized_concept_id": "hgnc:1910",
        "source_matches": {
            "HGNC": {
                "records": [
                    {
                        "concept_id": "hgnc:1910",
                        "symbol": "CHAF1A",
                        "symbol_status": "approved",
                        "label": "chromatin assembly factor 1 subunit A",
                        "strand": None,
                        "location_annotations": [],
                        "locations": [
                            # {
                            #     "type": "ChromosomeLocation",
                            #     "id": "ga4gh:CL.kPEG2TGUPOAsAYK6HY0ukprQ-DR_IuMZ",
                            #     "species_id": "taxonomy:9606",
                            #     "chr": "19",
                            #     "start": "p13.3",
                            #     "end": "p13.3"
                            # }
                        ],
                        "aliases": [
                            "CAF1P150",
                            "P150",
                            "CAF1",
                            "CAF1B",
                            "MGC71229",
                            "CAF-1",
                        ],
                        "previous_symbols": [],
                        "xrefs": ["ensembl:ENSG00000167670", "ncbigene:10036"],
                        "associated_with": [
                            "vega:OTTHUMG00000181922",
                            "ccds:CCDS32875",
                            "ucsc:uc002mal.4",
                            "pubmed:7600578",
                            "uniprot:Q13111",
                            "omim:601246",
                            "ena.embl:U20979",
                            "refseq:NM_005483",
                        ],
                        "gene_type": "gene with protein product",
                    }
                ],
            },
            "Ensembl": {
                "records": [
                    {
                        "concept_id": "ensembl:ENSG00000167670",
                        "symbol": "CHAF1A",
                        "symbol_status": None,
                        "label": "chromatin assembly factor 1 subunit A",
                        "strand": "+",
                        "location_annotations": [],
                        "locations": [
                            {
                                "id": "ga4gh:SL.tLUFh2LAYq-bsMi0Vob_TIWrz-sE4HgE",
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl",  # noqa: E501
                                },
                                "start": 4402639,
                                "end": 4445018,
                            }
                        ],
                        "aliases": [],
                        "previous_symbols": [],
                        "xrefs": ["hgnc:1910"],
                        "associated_with": [],
                        "gene_type": "protein_coding",
                    }
                ],
            },
            "NCBI": {
                "records": [
                    {
                        "concept_id": "ncbigene:10036",
                        "symbol": "CHAF1A",
                        "symbol_status": None,
                        "label": "chromatin assembly factor 1 subunit A",
                        "strand": "+",
                        "location_annotations": [],
                        "locations": [
                            # {
                            #     "type": "ChromosomeLocation",
                            #     "id": "ga4gh:CL.kPEG2TGUPOAsAYK6HY0ukprQ-DR_IuMZ",
                            #     "species_id": "taxonomy:9606",
                            #     "chr": "19",
                            #     "start": "p13.3",
                            #     "end": "p13.3"
                            # },
                            {
                                "id": "ga4gh:SL.-3T7UXNk6nIkMKB9YGEb0RTYxbVY2TUy",
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl",  # noqa: E501
                                },
                                "start": 4402639,
                                "end": 4450830,
                            }
                        ],
                        "aliases": ["CAF1P150", "P150", "CAF1", "CAF1B", "CAF-1"],
                        "previous_symbols": ["LOC107985297"],
                        "xrefs": ["ensembl:ENSG00000167670", "hgnc:1910"],
                        "associated_with": ["omim:601246"],
                        "gene_type": "protein-coding",
                    }
                ]
            },
        },
    }


@pytest.fixture(scope="module")
def normalize_unmerged_ache():
    """Provide ACHE fixture for unmerged normalize endpoint."""
    return {
        "normalized_concept_id": "hgnc:108",
        "source_matches": {
            "NCBI": {
                "records": [
                    {
                        "concept_id": "ncbigene:43",
                        "symbol": "ACHE",
                        "symbol_status": None,
                        "label": "acetylcholinesterase (Cartwright blood group)",
                        "strand": "-",
                        "location_annotations": [],
                        "locations": [
                            # {
                            #     "type": "ChromosomeLocation",
                            #     "id": "ga4gh:CL.JSw-08GkF-7M-OQR-33MLLKQHSi7QJb5",
                            #     "species_id": "taxonomy:9606",
                            #     "chr": "7",
                            #     "start": "q22.1",
                            #     "end": "q22.1"
                            # },
                            {
                                "id": "ga4gh:SL.U7vPSlX8eyCKdFSiROIsc9om0Y7pCm2g",
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",  # noqa: E501
                                },
                                "start": 100889993,
                                "end": 100896994,
                            }
                        ],
                        "aliases": ["YT", "ARACHE", "ACEE", "N-ACHE"],
                        "previous_symbols": ["ACEE"],
                        "xrefs": ["hgnc:108", "ensembl:ENSG00000087085"],
                        "associated_with": ["omim:100740"],
                        "gene_type": "protein-coding",
                    }
                ],
            },
            "Ensembl": {
                "records": [
                    {
                        "concept_id": "ensembl:ENSG00000087085",
                        "symbol": "ACHE",
                        "symbol_status": None,
                        "label": "acetylcholinesterase (Cartwright blood group)",
                        "strand": "-",
                        "location_annotations": [],
                        "locations": [
                            {
                                "id": "ga4gh:SL.dnydHb2Bnv5pwXjI4MpJmrZUADf5QLe1",
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",  # noqa: E501
                                },
                                "start": 100889993,
                                "end": 100896974,
                            }
                        ],
                        "aliases": [],
                        "previous_symbols": [],
                        "xrefs": ["hgnc:108"],
                        "associated_with": [],
                        "gene_type": "protein_coding",
                    }
                ]
            },
            "HGNC": {
                "records": [
                    {
                        "concept_id": "hgnc:108",
                        "symbol": "ACHE",
                        "symbol_status": "approved",
                        "label": "acetylcholinesterase (Cartwright blood group)",
                        "strand": None,
                        "location_annotations": [],
                        "locations": [
                            # {
                            #     "type": "ChromosomeLocation",
                            #     "id": "ga4gh:CL.JSw-08GkF-7M-OQR-33MLLKQHSi7QJb5",
                            #     "species_id": "taxonomy:9606",
                            #     "chr": "7",
                            #     "start": "q22.1",
                            #     "end": "q22.1"
                            # }
                        ],
                        "aliases": ["3.1.1.7"],
                        "previous_symbols": ["YT"],
                        "xrefs": ["ncbigene:43", "ensembl:ENSG00000087085"],
                        "associated_with": [
                            "ucsc:uc003uxi.4",
                            "vega:OTTHUMG00000157033",
                            "merops:S09.979",
                            "ccds:CCDS5710",
                            "omim:100740",
                            "iuphar:2465",
                            "ccds:CCDS5709",
                            "refseq:NM_015831",
                            "pubmed:1380483",
                            "uniprot:P22303",
                            "ccds:CCDS64736",
                        ],
                        "gene_type": "gene with protein product",
                    }
                ]
            },
        },
    }


@pytest.fixture(scope="module")
def normalized_ifnr():
    """Return normalized core Gene object for IFNR."""
    params = {
        "type": "Gene",
        "id": "normalize.gene.hgnc:5447",
        "label": "IFNR",
        "mappings": [
            {
                "coding": {"code": "3466", "system": "ncbigene"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "1906174", "system": "pubmed"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "147573", "system": "omim"},
                "relation": "relatedMatch",
            },
            {
                "coding": {"code": "1193239", "system": "pubmed"},
                "relation": "relatedMatch",
            },
        ],
        "aliases": ["IFNGM", "IFNGM2"],
        "extensions": [
            {
                "name": "approved_name",
                "value": "interferon production regulator",
                "type": "Extension",
            },
            {"name": "symbol_status", "value": "approved", "type": "Extension"},
            {"name": "symbol_status", "value": "approved", "type": "Extension"},
            {"name": "ncbi_gene_type", "type": "Extension", "value": "unknown"},
            {"name": "hgnc_locus_type", "type": "Extension", "value": "unknown"},
            {"name": "location_annotations", "type": "Extension", "value": ["16"]},
        ],
    }
    return core_models.Gene(**params)


@pytest.fixture(scope="module")
def num_sources():
    """Get the number of sources."""
    return len({s for s in SourceName})


@pytest.fixture(scope="module")
def source_meta():
    """Create test fixture for source meta"""
    return [SourceName.HGNC, SourceName.ENSEMBL, SourceName.NCBI]


def compare_warnings(actual_warnings, expected_warnings):
    """Compare response warnings against expected results."""
    if expected_warnings:
        assert len(actual_warnings) == len(expected_warnings), "warnings len"
        for e_warnings in expected_warnings:
            for r_warnings in actual_warnings:
                for e_key, e_val in e_warnings.items():
                    for r_val in r_warnings.values():
                        if e_key == r_val:
                            if isinstance(e_val, list):
                                assert set(r_val) == set(e_val), "warnings val"
                            else:
                                assert r_val == e_val, "warnings val"
    else:
        assert actual_warnings == [], "warnings != []"


def compare_normalize_resp(
    resp,
    expected_query,
    expected_match_type,
    expected_gene,
    expected_warnings=None,
    expected_source_meta=None,
):
    """Check that normalize response is correct"""
    assert resp.query == expected_query
    compare_warnings(resp.warnings, expected_warnings)
    assert resp.match_type == expected_match_type
    assert resp.normalized_id == expected_gene.id.split("normalize.gene.")[-1]
    compare_gene(expected_gene, resp.gene)
    if not expected_source_meta:
        assert resp.source_meta_ == {}
    else:
        resp_source_meta_keys = resp.source_meta_.keys()
        assert len(resp_source_meta_keys) == len(
            expected_source_meta
        ), "source_meta_keys"  # noqa: E501
        for src in expected_source_meta:
            assert src in resp_source_meta_keys
    compare_service_meta(resp.service_meta_)


def compare_unmerged_record(gene, test_gene):
    """Check that gene and test_gene are the same."""
    assert gene.label == test_gene.label
    assert gene.concept_id == test_gene.concept_id
    assert set(gene.aliases) == set(test_gene.aliases)
    assert set(gene.xrefs) == set(test_gene.xrefs)
    assert gene.symbol_status == test_gene.symbol_status
    assert set(gene.previous_symbols) == set(test_gene.previous_symbols)
    assert set(gene.associated_with) == set(test_gene.associated_with)
    assert gene.symbol == test_gene.symbol
    assert len(gene.locations) == len(test_gene.locations)
    for loc in gene.locations:
        assert loc in test_gene.locations
    assert set(gene.location_annotations) == set(test_gene.location_annotations)
    assert gene.strand == test_gene.strand
    assert gene.gene_type == test_gene.gene_type


def compare_unmerged_response(actual, query, warnings, match_type, fixture):
    """Compare response from normalize unmerged endpoint to fixture."""
    assert actual.query == query
    compare_warnings(actual.warnings, warnings)
    assert actual.match_type == match_type
    assert actual.normalized_concept_id == fixture["normalized_concept_id"]

    for source, match in actual.source_matches.items():
        assert match.source_meta_  # check that it's there
        for record in match.records:
            concept_id = record.concept_id
            fixture_gene = None
            # get corresponding fixture record
            for gene in fixture["source_matches"][source.value]["records"]:
                if gene["concept_id"] == concept_id:
                    fixture_gene = BaseGene(**gene)
                    break
            assert fixture_gene, f"Unable to find fixture for {concept_id}"
            compare_unmerged_record(record, fixture_gene)


def compare_service_meta(service_meta):
    """Check that service metadata is correct."""
    assert service_meta.name == "gene-normalizer"
    assert service_meta.version >= "0.1.0"
    assert isinstance(service_meta.response_datetime, str)
    assert service_meta.url == "https://github.com/cancervariants/gene-normalization"


def compare_gene(test, actual):
    """Test that actual and expected core gene objects match."""
    assert actual.id == test.id
    assert actual.type == test.type
    assert actual.label == test.label

    assert bool(actual.mappings) == bool(test.mappings)
    if actual.mappings:
        no_matches = []
        for actual_mapping in actual.mappings:
            match = None
            for fixture_mapping in test.mappings:
                if actual_mapping == fixture_mapping:
                    match = actual_mapping
                    break
            if not match:
                no_matches.append(actual_mapping)
        assert no_matches == [], no_matches
        assert len(actual.mappings) == len(test.mappings)

    assert set(actual.aliases) == set(test.aliases), "aliases"
    extensions_present = "extensions" in test.model_fields.keys()
    assert ("extensions" in actual.model_fields.keys()) == extensions_present
    if extensions_present:
        actual_ext_names = sorted([ext.name for ext in actual.extensions])
        unique_actual_ext_names = sorted(set(actual_ext_names))
        assert actual_ext_names == unique_actual_ext_names, "duplicate extension names"
        test_ext_names = {ext.name for ext in test.extensions}
        assert set(actual_ext_names) == test_ext_names, "extension names dont match"
        n_ext_correct = 0
        for test_ext in test.extensions:
            for actual_ext in actual.extensions:
                if actual_ext.name == test_ext.name:
                    assert isinstance(actual_ext.value, type(test_ext.value))
                    if isinstance(test_ext.value, list):
                        if test_ext.value:
                            if isinstance(test_ext.value[0], dict):
                                assert actual_ext.value == test_ext.value
                            else:
                                assert set(actual_ext.value) == set(
                                    test_ext.value
                                ), f"{test_ext.value} value"
                        else:
                            assert actual_ext.value == test_ext.value
                    else:
                        assert actual_ext.value == test_ext.value
                    assert actual_ext.type == test_ext.type
                    n_ext_correct += 1
        assert n_ext_correct == len(test.extensions), "number of correct extensions"


def test_search_query(query_handler, num_sources):
    """Test that query returns properly-structured response."""
    resp = query_handler.search(" BRAF ")
    assert resp.query == "BRAF"
    matches = resp.source_matches
    assert isinstance(matches, dict)
    assert len(matches) == num_sources


def test_search_query_source_filters(query_handler):
    """Test query source filtering."""
    sources = [SourceName.HGNC, SourceName.NCBI]
    resp = query_handler.search("BRAF", sources=sources)
    matches = resp.source_matches
    assert len(matches) == len(sources)
    assert SourceName.HGNC in matches
    assert SourceName.NCBI in matches

    sources = [SourceName.HGNC, SourceName.NCBI, SourceName.ENSEMBL]
    resp = query_handler.search("BRAF", sources=sources)
    matches = resp.source_matches
    assert len(matches) == len(sources)
    assert SourceName.ENSEMBL in matches
    assert SourceName.NCBI in matches
    assert SourceName.HGNC in matches


def test_ache_query(query_handler, num_sources, normalized_ache, source_meta):
    """Test that ACHE concept_id shows xref matches."""
    # Search
    resp = query_handler.search("ncbigene:43")
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert len(matches[SourceName.ENSEMBL].records) == 0
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.CONCEPT_ID

    resp = query_handler.search("hgnc:108")
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.CONCEPT_ID
    assert matches[SourceName.ENSEMBL].records[0].match_type == MatchType.XREF
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    resp = query_handler.search("ensembl:ENSG00000087085")
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert matches[SourceName.ENSEMBL].records[0].match_type == MatchType.CONCEPT_ID
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    # Normalize
    q = "ACHE"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.SYMBOL, normalized_ache, expected_source_meta=source_meta
    )

    q = "ache"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.SYMBOL, normalized_ache, expected_source_meta=source_meta
    )

    q = "hgnc:108"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.CONCEPT_ID, normalized_ache, expected_source_meta=source_meta
    )

    q = "ensembl:ENSG00000087085"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.CONCEPT_ID, normalized_ache, expected_source_meta=source_meta
    )

    q = "ncbigene:43"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.CONCEPT_ID, normalized_ache, expected_source_meta=source_meta
    )

    q = "3.1.1.7"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.ALIAS, normalized_ache, expected_source_meta=source_meta
    )

    q = "ARACHE"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.ALIAS, normalized_ache, expected_source_meta=source_meta
    )

    q = "YT"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp,
        q,
        MatchType.PREV_SYMBOL,
        normalized_ache,
        expected_source_meta=source_meta,
    )

    q = "ACEE"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp,
        q,
        MatchType.PREV_SYMBOL,
        normalized_ache,
        expected_source_meta=source_meta,
    )

    q = "omim:100740"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp,
        q,
        MatchType.ASSOCIATED_WITH,
        normalized_ache,
        expected_source_meta=source_meta,
    )


def test_braf_query(query_handler, num_sources, normalized_braf, source_meta):
    """Test that BRAF concept_id shows xref matches."""
    # Search
    resp = query_handler.search("ncbigene:673")
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert len(matches[SourceName.ENSEMBL].records) == 0
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.CONCEPT_ID

    resp = query_handler.search("hgnc:1097")
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.CONCEPT_ID
    assert matches[SourceName.ENSEMBL].records[0].match_type == MatchType.XREF
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    resp = query_handler.search("ensembl:ENSG00000157764")
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert matches[SourceName.ENSEMBL].records[0].match_type == MatchType.CONCEPT_ID
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    # Normalize
    q = "BRAF"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.SYMBOL, normalized_braf, expected_source_meta=source_meta
    )

    q = "braf"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.SYMBOL, normalized_braf, expected_source_meta=source_meta
    )

    q = "hgnc:1097"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.CONCEPT_ID, normalized_braf, expected_source_meta=source_meta
    )

    q = "ensembl:ENSG00000157764"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.CONCEPT_ID, normalized_braf, expected_source_meta=source_meta
    )

    q = "ncbigene:673"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.CONCEPT_ID, normalized_braf, expected_source_meta=source_meta
    )

    q = "NS7"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.ALIAS, normalized_braf, expected_source_meta=source_meta
    )

    q = "b-raf"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.ALIAS, normalized_braf, expected_source_meta=source_meta
    )

    q = "omim:164757"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp,
        q,
        MatchType.ASSOCIATED_WITH,
        normalized_braf,
        expected_source_meta=source_meta,
    )


def test_abl1_query(query_handler, num_sources, normalized_abl1, source_meta):
    """Test that ABL1 concept_id shows xref matches."""
    # Search
    resp = query_handler.search("ncbigene:25")
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert len(matches[SourceName.ENSEMBL].records) == 0
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.CONCEPT_ID

    resp = query_handler.search("hgnc:76")
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.CONCEPT_ID
    assert matches[SourceName.ENSEMBL].records[0].match_type == MatchType.XREF
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    resp = query_handler.search("ensembl:ENSG00000097007")
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert matches[SourceName.ENSEMBL].records[0].match_type == MatchType.CONCEPT_ID
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    # Normalize
    q = "ABL1"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.SYMBOL, normalized_abl1, expected_source_meta=source_meta
    )

    q = "abl1"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.SYMBOL, normalized_abl1, expected_source_meta=source_meta
    )

    q = "hgnc:76"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.CONCEPT_ID, normalized_abl1, expected_source_meta=source_meta
    )

    q = "ensembl:ENSG00000097007"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.CONCEPT_ID, normalized_abl1, expected_source_meta=source_meta
    )

    q = "ncbigene:25"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.CONCEPT_ID, normalized_abl1, expected_source_meta=source_meta
    )

    q = "v-abl"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.ALIAS, normalized_abl1, expected_source_meta=source_meta
    )

    q = "LOC116063"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp,
        q,
        MatchType.PREV_SYMBOL,
        normalized_abl1,
        expected_source_meta=source_meta,
    )

    q = "LOC112779"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp,
        q,
        MatchType.PREV_SYMBOL,
        normalized_abl1,
        expected_source_meta=source_meta,
    )

    q = "ABL"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp,
        q,
        MatchType.PREV_SYMBOL,
        normalized_abl1,
        expected_source_meta=source_meta,
    )

    q = "refseq:NM_007313"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp,
        q,
        MatchType.ASSOCIATED_WITH,
        normalized_abl1,
        expected_source_meta=source_meta,
    )


def test_multiple_norm_concepts(query_handler, normalized_p150, source_meta):
    """Tests where more than one normalized concept is found."""
    q = "P150"
    resp = query_handler.normalize(q)
    expected_warnings = [
        {
            "multiple_normalized_concepts_found": [
                "hgnc:16850",
                "hgnc:76",
                "hgnc:17168",
                "hgnc:500",
                "hgnc:8982",
            ]
        }
    ]
    compare_normalize_resp(
        resp,
        q,
        MatchType.ALIAS,
        normalized_p150,
        expected_source_meta=source_meta,
        expected_warnings=expected_warnings,
    )


def test_normalize_single_entry(query_handler, normalized_loc_653303):
    """Test that the normalized endpoint correctly shapes unmerged identity
    records into core gene objects.
    """
    q = "LOC653303"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp,
        q,
        MatchType.SYMBOL,
        normalized_loc_653303,
        expected_source_meta=[SourceName.NCBI],
    )


def test_normalize_no_locations(query_handler, normalized_ifnr):
    """Test that the normalized endpoint correcly shapes merged entity with no
    locations
    """
    q = "IFNR"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp,
        q,
        MatchType.SYMBOL,
        normalized_ifnr,
        expected_source_meta=[SourceName.HGNC, SourceName.NCBI],
    )


def test_normalize_unmerged(
    query_handler,
    normalize_unmerged_loc_653303,
    normalize_unmerged_chaf1a,
    normalize_unmerged_ache,
):
    """Test that unmerged normalization produces correct results."""
    # concept ID
    q = "ncbigene:653303"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(
        resp, q, [], MatchType.CONCEPT_ID, normalize_unmerged_loc_653303
    )

    q = "hgnc:1910"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(
        resp, q, [], MatchType.CONCEPT_ID, normalize_unmerged_chaf1a
    )

    q = "HGNC:108"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(
        resp, q, [], MatchType.CONCEPT_ID, normalize_unmerged_ache
    )

    # symbol
    q = "LOC653303"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(
        resp, q, [], MatchType.SYMBOL, normalize_unmerged_loc_653303
    )

    # prev symbol
    q = "ACEE"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(
        resp, q, [], MatchType.PREV_SYMBOL, normalize_unmerged_ache
    )

    q = "LOC196266"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(
        resp, q, [], MatchType.PREV_SYMBOL, normalize_unmerged_loc_653303
    )

    # alias
    q = "P150"
    resp = query_handler.normalize_unmerged(q)
    expected_warnings = [
        {
            "multiple_normalized_concepts_found": [
                "hgnc:500",
                "hgnc:8982",
                "hgnc:17168",
                "hgnc:16850",
                "hgnc:76",
            ]
        }
    ]
    compare_unmerged_response(
        resp, q, expected_warnings, MatchType.ALIAS, normalize_unmerged_chaf1a
    )

    q = "ARACHE"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.ALIAS, normalize_unmerged_ache)

    q = "MGC71229"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.ALIAS, normalize_unmerged_chaf1a)

    # assoc with
    q = "omim:100740"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(
        resp, q, [], MatchType.ASSOCIATED_WITH, normalize_unmerged_ache
    )

    q = "uniprot:Q13111"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(
        resp, q, [], MatchType.ASSOCIATED_WITH, normalize_unmerged_chaf1a
    )


def test_invalid_queries(query_handler):
    """Test invalid queries"""
    resp = query_handler.normalize("B R A F")
    assert resp.match_type is MatchType.NO_MATCH

    with pytest.raises(TypeError):
        resp["match_type"]

    resp = query_handler.search("B R A F")
    records = [r for matches in resp.source_matches.values() for r in matches.records]
    assert len(records) == 0


def test_service_meta(query_handler):
    """Test service meta info in response."""
    resp = query_handler.search("pheno")
    compare_service_meta(resp.service_meta_)
