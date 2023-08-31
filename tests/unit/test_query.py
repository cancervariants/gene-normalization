"""Module to test the query module."""
import copy

import pytest

from gene.query import QueryHandler, InvalidParameterException
from gene.schemas import BaseGene, SourceName, MatchType, GeneDescriptor


@pytest.fixture(scope='module')
def query_handler(database):
    """Build query_handler test fixture."""
    class QueryGetter:

        def __init__(self):
            self.query_handler = QueryHandler(database)

        def search(self, query_str, keyed=False, incl='', excl=''):
            return self.query_handler.search(query_str=query_str, keyed=keyed,
                                             incl=incl, excl=excl)

        def normalize(self, query_str):
            return self.query_handler.normalize(query_str)

        def normalize_unmerged(self, query_str):
            return self.query_handler.normalize_unmerged(query_str)

    return QueryGetter()


@pytest.fixture(scope='module')
def normalized_ache():
    """Return normalized Gene Descriptor for ACHE."""
    params = {
        "id": "normalize.gene:ACHE",
        "type": "GeneDescriptor",
        "gene": "hgnc:108",
        "label": "ACHE",
        "xrefs": {
            "ensembl:ENSG00000087085",
            "ncbigene:43"
        },
        "alternate_labels": [
            "3.1.1.7",
            "YT",
            "N-ACHE",
            "ARACHE",
            "ACEE"
        ],
        "extensions": [
            {
                "name": "previous_symbols",
                "value": [
                    "ACEE",
                    "YT"
                ],
                "type": "Extension"
            },
            {
                "name": "approved_name",
                "value": "acetylcholinesterase (Cartwright blood group)",
                "type": "Extension"
            },
            {
                "name": "symbol_status",
                "value": "approved",
                "type": "Extension"
            },
            {
                "name": "associated_with",
                "value": [
                    "vega:OTTHUMG00000157033",
                    "ucsc:uc003uxi.4",
                    "ccds:CCDS5710",
                    "ccds:CCDS64736",
                    "ccds:CCDS5709",
                    "uniprot:P22303",
                    "pubmed:1380483",
                    "omim:100740",
                    "merops:S09.979",
                    "iuphar:2465",
                    "refseq:NM_015831"
                ],
                "type": "Extension"
            },
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
                        "id": "ga4gh:SL.OuUQ-JYrkb92VioFp1P9JLGAbVQA1Wqs",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"
                        },
                        "start": 100889993,
                        "end": 100896994
                    }
                ],
                "type": "Extension"
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
                        "id": "ga4gh:SL.oyhehgtv3XV3iMTlul7XtMQ_5RSAvts6",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"
                        },
                        "start": 100889993,
                        "end": 100896974
                    }
                ],
                "type": "Extension"
            },
            {
                "name": "ncbi_gene_type",
                "type": "Extension",
                "value": "protein-coding"
            },
            {
                "name": "hgnc_locus_type",
                "type": "Extension",
                "value": "gene with protein product"
            },
            {
                "name": "ensembl_biotype",
                "type": "Extension",
                "value": "protein_coding"
            },
            {
                "name": "strand",
                "type": "Extension",
                "value": "-"
            }
        ]
    }
    return GeneDescriptor(**params)


@pytest.fixture(scope='module')
def normalized_braf():
    """Return normalized Gene Descriptor for BRAF."""
    params = {
        "id": "normalize.gene:BRAF",
        "type": "GeneDescriptor",
        "gene": "hgnc:1097",
        "label": "BRAF",
        "xrefs": {
            "ensembl:ENSG00000157764",
            "ncbigene:673"
        },
        "alternate_labels": [
            "BRAF1",
            "BRAF-1",
            "RAFB1",
            "NS7",
            "B-RAF1",
            "B-raf"
        ],
        "extensions": [
            {
                "name": "approved_name",
                "value": "B-Raf proto-oncogene, serine/threonine kinase",
                "type": "Extension"
            },
            {
                "name": "symbol_status",
                "value": "approved",
                "type": "Extension"
            },
            {
                "name": "associated_with",
                "value": [
                    "vega:OTTHUMG00000157457",
                    "ucsc:uc003vwc.5",
                    "ccds:CCDS5863",
                    "ccds:CCDS87555",
                    "ccds:CCDS94218",
                    "ccds:CCDS94219",
                    "uniprot:P15056",
                    "pubmed:2284096",
                    "pubmed:1565476",
                    "cosmic:BRAF",
                    "omim:164757",
                    "orphanet:119066",
                    "iuphar:1943",
                    "ena.embl:M95712",
                    "refseq:NM_004333"
                ],
                "type": "Extension"
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
                        "id": "ga4gh:SL.iwWw9B3tkU3TCLF3d8xu4zSQBhpDZfJ6",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"
                        },
                        "start": 140719326,
                        "end": 140924929
                    }
                ],
                "type": "Extension"
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
                        "id": "ga4gh:SL.rXzVqqlchBvUef98MNQA77FvwSJgiOf5",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"
                        },
                        "start": 140713327,
                        "end": 140924929
                    }
                ],
                "type": "Extension"
            },
            {
                "name": "ncbi_gene_type",
                "type": "Extension",
                "value": "protein-coding"
            },
            {
                "name": "hgnc_locus_type",
                "type": "Extension",
                "value": "gene with protein product"
            },
            {
                "name": "ensembl_biotype",
                "type": "Extension",
                "value": "protein_coding"
            },
            {
                "name": "strand",
                "type": "Extension",
                "value": "-"
            }
        ]
    }
    return GeneDescriptor(**params)


@pytest.fixture(scope='module')
def normalized_abl1():
    """Return normalized Gene Descriptor for ABL1."""
    params = {
        "id": "normalize.gene:ABL1",
        "type": "GeneDescriptor",
        "gene": "hgnc:76",
        "label": "ABL1",
        "xrefs": {
            "ensembl:ENSG00000097007",
            "ncbigene:25"
        },
        "alternate_labels": [
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
            "ABL"
        ],
        "extensions": [
            {
                "name": "previous_symbols",
                "value": [
                    "LOC116063",
                    "LOC112779",
                    "ABL"
                ],
                "type": "Extension"
            },
            {
                "name": "approved_name",
                "value": "ABL proto-oncogene 1, non-receptor tyrosine kinase",
                "type": "Extension"
            },
            {
                "name": "symbol_status",
                "value": "approved",
                "type": "Extension"
            },
            {
                "name": "associated_with",
                "value": [
                    "vega:OTTHUMG00000020813",
                    "ucsc:uc004bzv.4",
                    "ccds:CCDS35166",
                    "ccds:CCDS35165",
                    "uniprot:P00519",
                    "pubmed:1857987",
                    "pubmed:12626632",
                    "cosmic:ABL1",
                    "omim:189980",
                    "orphanet:117691",
                    "iuphar:1923",
                    "ena.embl:M14752",
                    "refseq:NM_007313"
                ],
                "type": "Extension"
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
                        "id": "ga4gh:SL.qwMQXDwguWeHsOb5bd7qoLC8zyfxcHzC",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.KEO-4XBcm1cxeo_DIQ8_ofqGUkp4iZhI"
                        },
                        "start": 130713042,
                        "end": 130887675
                    }
                ],
                "type": "Extension"
            },
            {
                "name": "ensembl_locations",
                "value": [
                    {
                        "id": "ga4gh:SL.mL3bBgmOG_mOb3P68os_hfhlPzbqr1MS",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.KEO-4XBcm1cxeo_DIQ8_ofqGUkp4iZhI"
                        },
                        "start": 130713015,
                        "end": 130887675
                    }
                ],
                "type": "Extension"
            },
            {
                "name": "ncbi_gene_type",
                "type": "Extension",
                "value": "protein-coding"
            },
            {
                "name": "hgnc_locus_type",
                "type": "Extension",
                "value": "gene with protein product"
            },
            {
                "name": "ensembl_biotype",
                "type": "Extension",
                "value": "protein_coding"
            },
            {
                "name": "strand",
                "type": "Extension",
                "value": "+"
            }
        ]
    }
    return GeneDescriptor(**params)


@pytest.fixture(scope='module')
def normalized_p150():
    """Return normalized Gene Descriptor for p150."""
    params = {
        "id": "normalize.gene:P150",
        "type": "GeneDescriptor",
        "gene": "hgnc:1910",
        "label": "CHAF1A",
        "xrefs": {
            "ensembl:ENSG00000167670",
            "ncbigene:10036"
        },
        "alternate_labels": [
            "CAF1P150",
            "MGC71229",
            "CAF-1",
            "P150",
            "CAF1B",
            "CAF1",
            "LOC107985297"
        ],
        "extensions": [
            {
                "name": "approved_name",
                "value": "chromatin assembly factor 1 subunit A",
                "type": "Extension"
            },
            {
                "name": "symbol_status",
                "value": "approved",
                "type": "Extension"
            },
            {
                "name": "associated_with",
                "value": [
                    "omim:601246",
                    "ccds:CCDS32875",
                    "pubmed:7600578",
                    "vega:OTTHUMG00000181922",
                    "uniprot:Q13111",
                    "refseq:NM_005483",
                    "ena.embl:U20979",
                    "ucsc:uc002mal.4"
                ],
                "type": "Extension"
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
                        "id": "ga4gh:SL.4RCVIbLVXLWPxvhd3IkRA-yI4o99Uwuq",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl"
                        },
                        "start": 4402639,
                        "end": 4445018
                    }
                ]
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
                        "id": "ga4gh:SL.-EYdfD5JkE4lqRwkCR_NNzaaT0uTYBg2",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl"
                        },
                        "start": 4402639,
                        "end": 4450830
                    }
                ]
            },
            {
                "name": "ncbi_gene_type",
                "type": "Extension",
                "value": "protein-coding"
            },
            {
                "name": "hgnc_locus_type",
                "type": "Extension",
                "value": "gene with protein product"
            },
            {
                "name": "ensembl_biotype",
                "type": "Extension",
                "value": "protein_coding"
            },
            {
                "name": "previous_symbols",
                "type": "Extension",
                "value": ["LOC107985297"]
            },
            {
                "name": "strand",
                "type": "Extension",
                "value": "+"
            }
        ]
    }
    return GeneDescriptor(**params)


@pytest.fixture(scope="module")
def normalized_loc_653303():
    """Provide test fixture for NCBI gene LOC653303. Used to validate
    normalized results that don't merge records.
    """
    params = {
        "id": "normalize.gene:LOC653303",
        "type": "GeneDescriptor",
        "label": "LOC653303",
        "alternate_labels": [
            "LOC196266",
            "LOC654080",
            "LOC731196"
        ],
        "extensions": [
            {
                "type": "Extension",
                "name": "approved_name",
                "value": "proprotein convertase subtilisin/kexin type 7 pseudogene"
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
                        "id": "ga4gh:SL.Iumme4GSaXUPAo0ifaq85LLlA1nT7l5o",
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.2NkFm8HK88MqeNkCgj78KidCAXgnsfV1"
                        },
                        "start": 117135528,
                        "end": 117138867
                    }
                ]
            },
            {
                "type": "Extension",
                "name": "previous_symbols",
                "value": [
                    "LOC196266",
                    "LOC731196",
                    "LOC654080"
                ]
            },
            {
                "type": "Extension",
                "name": "ncbi_gene_type",
                "value": "pseudo"
            },
            {
                "name": "strand",
                "type": "Extension",
                "value": "+"
            }
        ],
        "gene": "ncbigene:653303"
    }
    return GeneDescriptor(**params)


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
                                "id": "ga4gh:SL.Iumme4GSaXUPAo0ifaq85LLlA1nT7l5o",
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.2NkFm8HK88MqeNkCgj78KidCAXgnsfV1"  # noqa: E501
                                },
                                "start": 117135528,
                                "end": 117138867
                            }
                        ],
                        "aliases": [],
                        "previous_symbols": [
                            "LOC196266",
                            "LOC731196",
                            "LOC654080"
                        ],
                        "xrefs": [],
                        "associated_with": [],
                        "gene_type": "pseudo",
                    }
                ]
            }
        }
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
                            "CAF-1"
                        ],
                        "previous_symbols": [],
                        "xrefs": [
                            "ensembl:ENSG00000167670",
                            "ncbigene:10036"
                        ],
                        "associated_with": [
                            "vega:OTTHUMG00000181922",
                            "ccds:CCDS32875",
                            "ucsc:uc002mal.4",
                            "pubmed:7600578",
                            "uniprot:Q13111",
                            "omim:601246",
                            "ena.embl:U20979",
                            "refseq:NM_005483"
                        ],
                        "gene_type": "gene with protein product"
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
                                "id": "ga4gh:SL.4RCVIbLVXLWPxvhd3IkRA-yI4o99Uwuq",
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl"  # noqa: E501
                                },
                                "start": 4402639,
                                "end": 4445018
                            }
                        ],
                        "aliases": [],
                        "previous_symbols": [],
                        "xrefs": [
                            "hgnc:1910"
                        ],
                        "associated_with": [],
                        "gene_type": "protein_coding"
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
                                "id": "ga4gh:SL.-EYdfD5JkE4lqRwkCR_NNzaaT0uTYBg2",
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl"  # noqa: E501
                                },
                                "start": 4402639,
                                "end": 4450830
                            }
                        ],
                        "aliases": [
                            "CAF1P150",
                            "P150",
                            "CAF1",
                            "CAF1B",
                            "CAF-1"
                        ],
                        "previous_symbols": ["LOC107985297"],
                        "xrefs": [
                            "ensembl:ENSG00000167670",
                            "hgnc:1910"
                        ],
                        "associated_with": [
                            "omim:601246"
                        ],
                        "gene_type": "protein-coding"
                    }
                ]
            }
        }
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
                                "id": "ga4gh:SL.OuUQ-JYrkb92VioFp1P9JLGAbVQA1Wqs",
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"  # noqa: E501
                                },
                                "start": 100889993,
                                "end": 100896994
                            }
                        ],
                        "aliases": [
                            "YT",
                            "ARACHE",
                            "ACEE",
                            "N-ACHE"
                        ],
                        "previous_symbols": [
                            "ACEE"
                        ],
                        "xrefs": [
                            "hgnc:108",
                            "ensembl:ENSG00000087085"
                        ],
                        "associated_with": [
                            "omim:100740"
                        ],
                        "gene_type": "protein-coding"
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
                                "id": "ga4gh:SL.oyhehgtv3XV3iMTlul7XtMQ_5RSAvts6",
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul"  # noqa: E501
                                },
                                "start": 100889993,
                                "end": 100896974
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
                        "aliases": [
                            "3.1.1.7"
                        ],
                        "previous_symbols": [
                            "YT"
                        ],
                        "xrefs": [
                            "ncbigene:43",
                            "ensembl:ENSG00000087085"
                        ],
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
                            "ccds:CCDS64736"
                        ],
                        "gene_type": "gene with protein product",
                    }
                ]
            }
        }
    }


@pytest.fixture(scope="module")
def normalized_ifnr():
    """Return normalized Gene Descriptor for IFNR."""
    params = {
        "id": "normalize.gene:IFNR",
        "type": "GeneDescriptor",
        "gene": "hgnc:5447",
        "label": "IFNR",
        "xrefs": {
            "ncbigene:3466"
        },
        "alternate_labels": [
            "IFNGM",
            "IFNGM2"
        ],
        "extensions": [
            {
                "name": "approved_name",
                "value": "interferon production regulator",
                "type": "Extension"
            },
            {
                "name": "symbol_status",
                "value": "approved",
                "type": "Extension"
            },
            {
                "name": "associated_with",
                "value": [
                    "pubmed:1906174",
                    "omim:147573",
                    "pubmed:1193239"
                ],
                "type": "Extension"
            },
            {
                "name": "ncbi_gene_type",
                "type": "Extension",
                "value": "unknown"
            },
            {
                "name": "hgnc_locus_type",
                "type": "Extension",
                "value": "unknown"
            },
            {
                "name": "location_annotations",
                "type": "Extension",
                "value": ["16"]
            }
        ]
    }
    return GeneDescriptor(**params)


@pytest.fixture(scope='module')
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


def compare_normalize_resp(resp, expected_query, expected_match_type,
                           expected_gene_descriptor, expected_warnings=None,
                           expected_source_meta=None):
    """Check that normalize response is correct"""
    assert resp.query == expected_query
    compare_warnings(resp.warnings, expected_warnings)
    assert resp.match_type == expected_match_type
    compare_gene_descriptor(expected_gene_descriptor, resp.gene_descriptor)
    if not expected_source_meta:
        assert resp.source_meta_ == {}
    else:
        resp_source_meta_keys = resp.source_meta_.keys()
        assert len(resp_source_meta_keys) == len(expected_source_meta), "source_meta_keys"  # noqa: E501
        for src in expected_source_meta:
            assert src in resp_source_meta_keys
    compare_service_meta(resp.service_meta_)


def compare_unmerged_record(gene, test_gene):
    """Check that gene and test_gene are the same."""
    assert gene.label == test_gene.label
    assert gene.concept_id == test_gene.concept_id
    assert set(gene.aliases) == set(test_gene.aliases)
    set_actual_xrefs = {xref.root for xref in gene.xrefs}
    set_test_xrefs = {xref.root for xref in test_gene.xrefs}
    assert set_actual_xrefs == set_test_xrefs
    assert gene.symbol_status == test_gene.symbol_status
    assert set(gene.previous_symbols) == set(test_gene.previous_symbols)
    set_actual_aw = {aw.root for aw in gene.associated_with}
    set_test_aw = {aw.root for aw in test_gene.associated_with}
    assert set_actual_aw == set_test_aw
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
                if gene["concept_id"] == concept_id.root:
                    fixture_gene = BaseGene(**gene)
                    break
            assert fixture_gene, f"Unable to find fixture for {concept_id}"
            compare_unmerged_record(record, fixture_gene)


def compare_service_meta(service_meta):
    """Check that service metadata is correct."""
    assert service_meta.name == "gene-normalizer"
    assert service_meta.version >= "0.1.0"
    assert isinstance(service_meta.response_datetime, str)
    assert service_meta.url == 'https://github.com/cancervariants/gene-normalization'


def compare_gene_descriptor(test, actual):
    """Test that actual and expected gene descriptors match."""
    assert actual.id == test.id
    assert actual.type == test.type
    assert actual.gene.root == test.gene.root
    assert actual.label == test.label
    if actual.xrefs or test.xrefs:
        set_actual_xrefs = {xref.root for xref in actual.xrefs}
        set_test_xrefs = {xref.root for xref in test.xrefs}
        assert set_actual_xrefs == set_test_xrefs, "xrefs"
    assert set(actual.alternate_labels) == set(test.alternate_labels), "alt labels"
    extensions_present = "extensions" in test.model_fields.keys()
    assert ("extensions" in actual.model_fields.keys()) == extensions_present
    if extensions_present:
        assert len(actual.extensions) == len(test.extensions), "len of extensions"
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
                                assert set(actual_ext.value) == \
                                    set(test_ext.value), f"{test_ext.value} value"
                        else:
                            assert actual_ext.value == test_ext.value
                    else:
                        assert actual_ext.value == test_ext.value
                    assert actual_ext.type == test_ext.type
                    n_ext_correct += 1
        assert n_ext_correct == len(test.extensions), "number of correct extensions"


def test_search_query(query_handler, num_sources):
    """Test that query returns properly-structured response."""
    resp = query_handler.search(' BRAF ')
    assert resp.query == 'BRAF'
    matches = resp.source_matches
    assert isinstance(matches, list)
    assert len(matches) == num_sources


def test_search_query_keyed(query_handler, num_sources):
    """Test that query returns properly-structured response."""
    resp = query_handler.search(' BRAF ', keyed=True)
    assert resp.query == 'BRAF'
    matches = resp.source_matches
    assert isinstance(matches, dict)
    assert len(matches) == num_sources


def test_search_query_inc_exc(query_handler, num_sources):
    """Test that query incl and excl work correctly."""
    sources = "hgnc, ensembl, ncbi"
    resp = query_handler.search('BRAF', excl=sources)
    matches = resp.source_matches
    assert len(matches) == num_sources - len(sources.split())

    sources = 'Hgnc, NCBi'
    resp = query_handler.search('BRAF', keyed=True, incl=sources)
    matches = resp.source_matches
    assert len(matches) == len(sources.split())
    assert SourceName.HGNC in matches
    assert SourceName.NCBI in matches

    sources = 'HGnC'
    resp = query_handler.search('BRAF', keyed=True, excl=sources)
    matches = resp.source_matches
    assert len(matches) == num_sources - len(sources.split())
    assert SourceName.ENSEMBL in matches
    assert SourceName.NCBI in matches


def test_search_invalid_parameter_exception(query_handler):
    """Test that Invalid parameter exception works correctly."""
    with pytest.raises(InvalidParameterException):
        resp = query_handler.search('BRAF', keyed=True, incl='hgn')  # noqa: F841

    with pytest.raises(InvalidParameterException):
        resp = query_handler.search('BRAF', incl='hgnc', excl='hgnc')  # noqa: F841


def test_ache_query(query_handler, num_sources, normalized_ache, source_meta):
    """Test that ACHE concept_id shows xref matches."""
    # Search
    resp = query_handler.search('ncbigene:43', keyed=True)
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert len(matches[SourceName.ENSEMBL].records) == 0
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.CONCEPT_ID

    resp = query_handler.search('hgnc:108', keyed=True)
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.CONCEPT_ID
    assert matches[SourceName.ENSEMBL].records[0].match_type == MatchType.XREF
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    resp = query_handler.search('ensembl:ENSG00000087085', keyed=True)
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert matches[SourceName.ENSEMBL].records[0].match_type == \
           MatchType.CONCEPT_ID
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    # Normalize
    q = "ACHE"
    resp = query_handler.normalize(q)
    compare_normalize_resp(resp, q, MatchType.SYMBOL, normalized_ache,
                           expected_source_meta=source_meta)

    q = "ache"
    resp = query_handler.normalize(q)
    cpy_normalized_ache = copy.deepcopy(normalized_ache)
    cpy_normalized_ache.id = "normalize.gene:ache"
    compare_normalize_resp(resp, q, MatchType.SYMBOL, cpy_normalized_ache,
                           expected_source_meta=source_meta)

    q = "hgnc:108"
    resp = query_handler.normalize(q)
    cpy_normalized_ache.id = "normalize.gene:hgnc%3A108"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_ache,
                           expected_source_meta=source_meta)

    q = "ensembl:ENSG00000087085"
    resp = query_handler.normalize(q)
    cpy_normalized_ache.id = "normalize.gene:ensembl%3AENSG00000087085"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_ache,
                           expected_source_meta=source_meta)

    q = "ncbigene:43"
    resp = query_handler.normalize(q)
    cpy_normalized_ache.id = "normalize.gene:ncbigene%3A43"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_ache,
                           expected_source_meta=source_meta)

    q = "3.1.1.7"
    resp = query_handler.normalize(q)
    cpy_normalized_ache.id = "normalize.gene:3.1.1.7"
    compare_normalize_resp(resp, q, MatchType.ALIAS, cpy_normalized_ache,
                           expected_source_meta=source_meta)

    q = "ARACHE"
    resp = query_handler.normalize(q)
    cpy_normalized_ache.id = "normalize.gene:ARACHE"
    compare_normalize_resp(resp, q, MatchType.ALIAS, cpy_normalized_ache,
                           expected_source_meta=source_meta)

    q = "YT"
    resp = query_handler.normalize(q)
    cpy_normalized_ache.id = "normalize.gene:YT"
    compare_normalize_resp(resp, q, MatchType.PREV_SYMBOL, cpy_normalized_ache,
                           expected_source_meta=source_meta)

    q = "ACEE"
    resp = query_handler.normalize(q)
    cpy_normalized_ache.id = "normalize.gene:ACEE"
    compare_normalize_resp(resp, q, MatchType.PREV_SYMBOL, cpy_normalized_ache,
                           expected_source_meta=source_meta)

    q = "omim:100740"
    resp = query_handler.normalize(q)
    cpy_normalized_ache.id = "normalize.gene:omim%3A100740"
    compare_normalize_resp(resp, q, MatchType.ASSOCIATED_WITH,
                           cpy_normalized_ache,
                           expected_source_meta=source_meta)


def test_braf_query(query_handler, num_sources, normalized_braf, source_meta):
    """Test that BRAF concept_id shows xref matches."""
    # Search
    resp = query_handler.search('ncbigene:673', keyed=True)
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert len(matches[SourceName.ENSEMBL].records) == 0
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.CONCEPT_ID

    resp = query_handler.search('hgnc:1097', keyed=True)
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.CONCEPT_ID
    assert matches[SourceName.ENSEMBL].records[0].match_type == MatchType.XREF
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    resp = query_handler.search('ensembl:ENSG00000157764', keyed=True)
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert matches[SourceName.ENSEMBL].records[0].match_type == \
           MatchType.CONCEPT_ID
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    # Normalize
    q = "BRAF"
    resp = query_handler.normalize(q)
    compare_normalize_resp(resp, q, MatchType.SYMBOL, normalized_braf,
                           expected_source_meta=source_meta)

    q = "braf"
    resp = query_handler.normalize(q)
    cpy_normalized_braf = copy.deepcopy(normalized_braf)
    cpy_normalized_braf.id = "normalize.gene:braf"
    compare_normalize_resp(resp, q, MatchType.SYMBOL, cpy_normalized_braf,
                           expected_source_meta=source_meta)

    q = "hgnc:1097"
    resp = query_handler.normalize(q)
    cpy_normalized_braf.id = "normalize.gene:hgnc%3A1097"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_braf,
                           expected_source_meta=source_meta)

    q = "ensembl:ENSG00000157764"
    resp = query_handler.normalize(q)
    cpy_normalized_braf.id = "normalize.gene:ensembl%3AENSG00000157764"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_braf,
                           expected_source_meta=source_meta)

    q = "ncbigene:673"
    resp = query_handler.normalize(q)
    cpy_normalized_braf.id = "normalize.gene:ncbigene%3A673"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_braf,
                           expected_source_meta=source_meta)

    q = "NS7"
    resp = query_handler.normalize(q)
    cpy_normalized_braf.id = "normalize.gene:NS7"
    compare_normalize_resp(resp, q, MatchType.ALIAS, cpy_normalized_braf,
                           expected_source_meta=source_meta)

    q = "b-raf"
    resp = query_handler.normalize(q)
    cpy_normalized_braf.id = "normalize.gene:b-raf"
    compare_normalize_resp(resp, q, MatchType.ALIAS, cpy_normalized_braf,
                           expected_source_meta=source_meta)

    q = "omim:164757"
    resp = query_handler.normalize(q)
    cpy_normalized_braf.id = "normalize.gene:omim%3A164757"
    compare_normalize_resp(resp, q, MatchType.ASSOCIATED_WITH,
                           cpy_normalized_braf,
                           expected_source_meta=source_meta)


def test_abl1_query(query_handler, num_sources, normalized_abl1, source_meta):
    """Test that ABL1 concept_id shows xref matches."""
    # Search
    resp = query_handler.search('ncbigene:25', keyed=True)
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert len(matches[SourceName.ENSEMBL].records) == 0
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.CONCEPT_ID

    resp = query_handler.search('hgnc:76', keyed=True)
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.CONCEPT_ID
    assert matches[SourceName.ENSEMBL].records[0].match_type == MatchType.XREF
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    resp = query_handler.search('ensembl:ENSG00000097007', keyed=True)
    matches = resp.source_matches
    assert len(matches) == num_sources
    assert matches[SourceName.HGNC].records[0].match_type == MatchType.XREF
    assert matches[SourceName.ENSEMBL].records[0].match_type == \
           MatchType.CONCEPT_ID
    assert matches[SourceName.NCBI].records[0].match_type == MatchType.XREF

    # Normalize
    q = "ABL1"
    resp = query_handler.normalize(q)
    compare_normalize_resp(resp, q, MatchType.SYMBOL, normalized_abl1,
                           expected_source_meta=source_meta)

    q = "abl1"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1 = copy.deepcopy(normalized_abl1)
    cpy_normalized_abl1.id = "normalize.gene:abl1"
    compare_normalize_resp(resp, q, MatchType.SYMBOL, cpy_normalized_abl1,
                           expected_source_meta=source_meta)

    q = "hgnc:76"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1.id = "normalize.gene:hgnc%3A76"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_abl1,
                           expected_source_meta=source_meta)

    q = "ensembl:ENSG00000097007"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1.id = "normalize.gene:ensembl%3AENSG00000097007"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_abl1,
                           expected_source_meta=source_meta)

    q = "ncbigene:25"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1.id = "normalize.gene:ncbigene%3A25"
    compare_normalize_resp(resp, q, MatchType.CONCEPT_ID, cpy_normalized_abl1,
                           expected_source_meta=source_meta)

    q = "v-abl"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1.id = "normalize.gene:v-abl"
    compare_normalize_resp(resp, q, MatchType.ALIAS, cpy_normalized_abl1,
                           expected_source_meta=source_meta)

    q = "LOC116063"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1.id = "normalize.gene:LOC116063"
    compare_normalize_resp(resp, q, MatchType.PREV_SYMBOL, cpy_normalized_abl1,
                           expected_source_meta=source_meta)

    q = "LOC112779"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1.id = "normalize.gene:LOC112779"
    compare_normalize_resp(resp, q, MatchType.PREV_SYMBOL, cpy_normalized_abl1,
                           expected_source_meta=source_meta)

    q = "ABL"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1.id = "normalize.gene:ABL"
    compare_normalize_resp(resp, q, MatchType.PREV_SYMBOL, cpy_normalized_abl1,
                           expected_source_meta=source_meta)

    q = "refseq:NM_007313"
    resp = query_handler.normalize(q)
    cpy_normalized_abl1.id = "normalize.gene:refseq%3ANM_007313"
    compare_normalize_resp(resp, q, MatchType.ASSOCIATED_WITH,
                           cpy_normalized_abl1,
                           expected_source_meta=source_meta)


def test_multiple_norm_concepts(query_handler, normalized_p150, source_meta):
    """Tests where more than one normalized concept is found."""
    q = "P150"
    resp = query_handler.normalize(q)
    expected_warnings = [{
        "multiple_normalized_concepts_found":
            ['hgnc:16850', 'hgnc:76', 'hgnc:17168', 'hgnc:500', 'hgnc:8982']
    }]
    compare_normalize_resp(resp, q, MatchType.ALIAS, normalized_p150,
                           expected_source_meta=source_meta,
                           expected_warnings=expected_warnings)


def test_normalize_single_entry(query_handler, normalized_loc_653303):
    """Test that the normalized endpoint correctly shapes unmerged identity
    records into gene descriptors.
    """
    q = "LOC653303"
    resp = query_handler.normalize(q)
    compare_normalize_resp(resp, q, MatchType.SYMBOL, normalized_loc_653303,
                           expected_source_meta=[SourceName.NCBI])


def test_normalize_no_locations(query_handler, normalized_ifnr):
    """Test that the normalized endpoint correcly shapes merged entity with no
    locations
    """
    q = "IFNR"
    resp = query_handler.normalize(q)
    compare_normalize_resp(
        resp, q, MatchType.SYMBOL, normalized_ifnr,
        expected_source_meta=[SourceName.HGNC, SourceName.NCBI])


def test_normalize_unmerged(query_handler, normalize_unmerged_loc_653303,
                            normalize_unmerged_chaf1a, normalize_unmerged_ache):
    """Test that unmerged normalization produces correct results."""
    # concept ID
    q = "ncbigene:653303"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.CONCEPT_ID,
                              normalize_unmerged_loc_653303)

    q = "hgnc:1910"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.CONCEPT_ID,
                              normalize_unmerged_chaf1a)

    q = "HGNC:108"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.CONCEPT_ID,
                              normalize_unmerged_ache)

    # symbol
    q = "LOC653303"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.SYMBOL,
                              normalize_unmerged_loc_653303)

    # prev symbol
    q = "ACEE"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.PREV_SYMBOL,
                              normalize_unmerged_ache)

    q = "LOC196266"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.PREV_SYMBOL,
                              normalize_unmerged_loc_653303)

    # alias
    q = "P150"
    resp = query_handler.normalize_unmerged(q)
    expected_warnings = [{
        "multiple_normalized_concepts_found":
            ['hgnc:500', 'hgnc:8982', 'hgnc:17168', 'hgnc:16850', 'hgnc:76']
    }]
    compare_unmerged_response(resp, q, expected_warnings, MatchType.ALIAS,
                              normalize_unmerged_chaf1a)

    q = "ARACHE"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.ALIAS, normalize_unmerged_ache)

    q = "MGC71229"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.ALIAS, normalize_unmerged_chaf1a)

    # assoc with
    q = "omim:100740"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.ASSOCIATED_WITH,
                              normalize_unmerged_ache)

    q = "uniprot:Q13111"
    resp = query_handler.normalize_unmerged(q)
    compare_unmerged_response(resp, q, [], MatchType.ASSOCIATED_WITH,
                              normalize_unmerged_chaf1a)


def test_invalid_queries(query_handler):
    """Test invalid queries"""
    resp = query_handler.normalize("B R A F")
    assert resp.match_type is MatchType.NO_MATCH

    with pytest.raises(TypeError):
        resp["match_type"]

    resp = query_handler.search("B R A F")
    assert len(resp.source_matches[0].records) == 0

    with pytest.raises(TypeError):
        resp.source_matches[0].records["match_type"]


def test_service_meta(query_handler):
    """Test service meta info in response."""
    resp = query_handler.search("pheno")
    compare_service_meta(resp.service_meta_)
