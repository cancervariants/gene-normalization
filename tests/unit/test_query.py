"""Module to test the query module."""

import pytest
from deepdiff import DeepDiff
from ga4gh.core.models import MappableConcept

from gene.query import InvalidParameterException, QueryHandler
from gene.schemas import BaseGene, MatchType, SourceName


@pytest.fixture(scope="module")
def query_handler(database):
    """Build query_handler test fixture."""

    class QueryGetter:
        def __init__(self):
            self.query_handler = QueryHandler(database)

        def search(self, query_str, incl="", excl=""):
            return self.query_handler.search(query_str=query_str, incl=incl, excl=excl)

        def normalize(self, query_str):
            return self.query_handler.normalize(query_str)

        def normalize_unmerged(self, query_str):
            return self.query_handler.normalize_unmerged(query_str)

    return QueryGetter()


@pytest.fixture(scope="module")
def normalized_ache():
    """Return normalized core Gene object for ACHE."""
    params = {
        "conceptType": "Gene",
        "id": "normalize.gene.hgnc:108",
        "primaryCoding": {
            "id": "hgnc:108",
            "code": "HGNC:108",
            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
        },
        "name": "ACHE",
        "mappings": [
            {
                "coding": {
                    "id": "ensembl:ENSG00000087085",
                    "code": "ENSG00000087085",
                    "system": "https://www.ensembl.org/id/",
                },
                "relation": "exactMatch",
            },
            {
                "coding": {
                    "id": "ncbigene:43",
                    "code": "43",
                    "system": "https://www.ncbi.nlm.nih.gov/gene/",
                },
                "relation": "exactMatch",
            },
            {
                "coding": {
                    "id": "vega:OTTHUMG00000157033",
                    "code": "OTTHUMG00000157033",
                    "system": "https://vega.archive.ensembl.org/Homo_sapiens/Gene/Summary?g=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "ucsc:uc003uxi.4",
                    "code": "uc003uxi.4",
                    "system": "http://genome.cse.ucsc.edu/cgi-bin/hgGene?org=Human&hgg_chrom=none&hgg_type=knownGene&hgg_gene=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "uniprot:P22303",
                    "code": "P22303",
                    "system": "http://purl.uniprot.org/uniprot/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "pubmed:1380483",
                    "code": "1380483",
                    "system": "https://pubmed.ncbi.nlm.nih.gov/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "omim:100740",
                    "code": "100740",
                    "system": "https://www.omim.org/MIM:",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "merops:S09.979",
                    "code": "S09.979",
                    "system": "https://www.ebi.ac.uk/merops/cgi-bin/pepsum?id=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "iuphar:2465",
                    "code": "2465",
                    "system": "https://www.guidetopharmacology.org/GRAC/ObjectDisplayForward?objectId=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "refseq:NM_015831",
                    "code": "NM_015831",
                    "system": "https://www.ncbi.nlm.nih.gov/nuccore/",
                },
                "relation": "relatedMatch",
            },
        ],
        "extensions": [
            {"name": "aliases", "value": ["3.1.1.7", "YT", "N-ACHE", "ARACHE", "ACEE"]},
            {"name": "previous_symbols", "value": ["ACEE", "YT"]},
            {
                "name": "approved_name",
                "value": "acetylcholinesterase (Yt blood group)",
            },
            {"name": "symbol_status", "value": "approved"},
            {
                "name": "ncbi_locations",
                "value": [
                    {
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        },
                        "start": 100889993,
                        "end": 100896994,
                    }
                ],
            },
            {
                "name": "ensembl_locations",
                "value": [
                    {
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        },
                        "start": 100889993,
                        "end": 100896974,
                    }
                ],
            },
            {"name": "ncbi_gene_type", "value": "protein-coding"},
            {
                "name": "hgnc_locus_type",
                "value": "gene with protein product",
            },
            {"name": "ensembl_biotype", "value": "protein_coding"},
            {"name": "strand", "value": "-"},
        ],
    }
    return MappableConcept(**params)


@pytest.fixture(scope="module")
def normalized_braf():
    """Return normalized core Gene object for BRAF."""
    params = {
        "conceptType": "Gene",
        "id": "normalize.gene.hgnc:1097",
        "primaryCoding": {
            "id": "hgnc:1097",
            "code": "HGNC:1097",
            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
        },
        "name": "BRAF",
        "mappings": [
            {
                "coding": {
                    "id": "ncbigene:673",
                    "code": "673",
                    "system": "https://www.ncbi.nlm.nih.gov/gene/",
                },
                "relation": "exactMatch",
            },
            {
                "coding": {
                    "id": "ensembl:ENSG00000157764",
                    "code": "ENSG00000157764",
                    "system": "https://www.ensembl.org/id/",
                },
                "relation": "exactMatch",
            },
            {
                "coding": {
                    "id": "iuphar:1943",
                    "code": "1943",
                    "system": "https://www.guidetopharmacology.org/GRAC/ObjectDisplayForward?objectId=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "orphanet:119066",
                    "code": "119066",
                    "system": "http://www.orpha.net/consor/cgi-bin/OC_Exp.php?Lng=EN&Expert=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "cosmic:BRAF",
                    "code": "BRAF",
                    "system": "http://cancer.sanger.ac.uk/cosmic/gene/overview?ln=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "pubmed:2284096",
                    "code": "2284096",
                    "system": "https://pubmed.ncbi.nlm.nih.gov/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "ucsc:uc003vwc.5",
                    "code": "uc003vwc.5",
                    "system": "http://genome.cse.ucsc.edu/cgi-bin/hgGene?org=Human&hgg_chrom=none&hgg_type=knownGene&hgg_gene=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "omim:164757",
                    "code": "164757",
                    "system": "https://www.omim.org/MIM:",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "refseq:NM_004333",
                    "code": "NM_004333",
                    "system": "https://www.ncbi.nlm.nih.gov/nuccore/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "uniprot:P15056",
                    "code": "P15056",
                    "system": "http://purl.uniprot.org/uniprot/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "ena.embl:M95712",
                    "code": "M95712",
                    "system": "https://www.ebi.ac.uk/ena/browser/view/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "vega:OTTHUMG00000157457",
                    "code": "OTTHUMG00000157457",
                    "system": "https://vega.archive.ensembl.org/Homo_sapiens/Gene/Summary?g=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "pubmed:1565476",
                    "code": "1565476",
                    "system": "https://pubmed.ncbi.nlm.nih.gov/",
                },
                "relation": "relatedMatch",
            },
        ],
        "extensions": [
            {
                "name": "aliases",
                "value": ["BRAF1", "BRAF-1", "RAFB1", "NS7", "B-RAF1", "B-raf"],
            },
            {
                "name": "approved_name",
                "value": "B-Raf proto-oncogene, serine/threonine kinase",
            },
            {
                "name": "ensembl_locations",
                "value": [
                    {
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        },
                        "start": 140719326,
                        "end": 140924929,
                    }
                ],
            },
            {
                "name": "ncbi_locations",
                "value": [
                    {
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
                        },
                        "start": 140713327,
                        "end": 140924929,
                    }
                ],
            },
            {"name": "ncbi_gene_type", "value": "protein-coding"},
            {
                "name": "hgnc_locus_type",
                "value": "gene with protein product",
            },
            {"name": "ensembl_biotype", "value": "protein_coding"},
            {"name": "strand", "value": "-"},
            {"name": "symbol_status", "value": "approved"},
        ],
    }
    return MappableConcept(**params)


@pytest.fixture(scope="module")
def normalized_abl1():
    """Return normalized core Gene object for ABL1."""
    params = {
        "conceptType": "Gene",
        "id": "normalize.gene.hgnc:76",
        "primaryCoding": {
            "id": "hgnc:76",
            "code": "HGNC:76",
            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
        },
        "name": "ABL1",
        "mappings": [
            {
                "coding": {
                    "id": "ensembl:ENSG00000097007",
                    "code": "ENSG00000097007",
                    "system": "https://www.ensembl.org/id/",
                },
                "relation": "exactMatch",
            },
            {
                "coding": {
                    "id": "ncbigene:25",
                    "code": "25",
                    "system": "https://www.ncbi.nlm.nih.gov/gene/",
                },
                "relation": "exactMatch",
            },
            {
                "coding": {
                    "id": "vega:OTTHUMG00000020813",
                    "code": "OTTHUMG00000020813",
                    "system": "https://vega.archive.ensembl.org/Homo_sapiens/Gene/Summary?g=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "ucsc:uc004bzv.4",
                    "code": "uc004bzv.4",
                    "system": "http://genome.cse.ucsc.edu/cgi-bin/hgGene?org=Human&hgg_chrom=none&hgg_type=knownGene&hgg_gene=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "uniprot:P00519",
                    "code": "P00519",
                    "system": "http://purl.uniprot.org/uniprot/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "pubmed:1857987",
                    "code": "1857987",
                    "system": "https://pubmed.ncbi.nlm.nih.gov/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "pubmed:12626632",
                    "code": "12626632",
                    "system": "https://pubmed.ncbi.nlm.nih.gov/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "cosmic:ABL1",
                    "code": "ABL1",
                    "system": "http://cancer.sanger.ac.uk/cosmic/gene/overview?ln=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "omim:189980",
                    "code": "189980",
                    "system": "https://www.omim.org/MIM:",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "orphanet:117691",
                    "code": "117691",
                    "system": "http://www.orpha.net/consor/cgi-bin/OC_Exp.php?Lng=EN&Expert=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "iuphar:1923",
                    "code": "1923",
                    "system": "https://www.guidetopharmacology.org/GRAC/ObjectDisplayForward?objectId=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "ena.embl:M14752",
                    "code": "M14752",
                    "system": "https://www.ebi.ac.uk/ena/browser/view/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "refseq:NM_007313",
                    "code": "NM_007313",
                    "system": "https://www.ncbi.nlm.nih.gov/nuccore/",
                },
                "relation": "relatedMatch",
            },
        ],
        "extensions": [
            {
                "name": "aliases",
                "value": [
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
            },
            {
                "name": "previous_symbols",
                "value": ["LOC116063", "LOC112779", "ABL"],
            },
            {
                "name": "approved_name",
                "value": "ABL proto-oncogene 1, non-receptor tyrosine kinase",
            },
            {
                "name": "ncbi_locations",
                "value": [
                    {
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.KEO-4XBcm1cxeo_DIQ8_ofqGUkp4iZhI",
                        },
                        "start": 130713042,
                        "end": 130887675,
                    }
                ],
            },
            {
                "name": "ensembl_locations",
                "value": [
                    {
                        "type": "SequenceLocation",
                        "sequenceReference": {
                            "type": "SequenceReference",
                            "refgetAccession": "SQ.KEO-4XBcm1cxeo_DIQ8_ofqGUkp4iZhI",
                        },
                        "start": 130713042,
                        "end": 130887675,
                    }
                ],
            },
            {"name": "ncbi_gene_type", "value": "protein-coding"},
            {
                "name": "hgnc_locus_type",
                "value": "gene with protein product",
            },
            {"name": "ensembl_biotype", "value": "protein_coding"},
            {"name": "strand", "value": "+"},
            {"name": "symbol_status", "value": "approved"},
        ],
    }
    return MappableConcept(**params)


@pytest.fixture(scope="module")
def normalized_p150():
    """Return normalized core Gene object for p150."""
    params = {
        "conceptType": "Gene",
        "id": "normalize.gene.hgnc:1910",
        "primaryCoding": {
            "id": "hgnc:1910",
            "code": "HGNC:1910",
            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
        },
        "name": "CHAF1A",
        "mappings": [
            {
                "coding": {
                    "id": "ensembl:ENSG00000167670",
                    "code": "ENSG00000167670",
                    "system": "https://www.ensembl.org/id/",
                },
                "relation": "exactMatch",
            },
            {
                "coding": {
                    "id": "ncbigene:10036",
                    "code": "10036",
                    "system": "https://www.ncbi.nlm.nih.gov/gene/",
                },
                "relation": "exactMatch",
            },
            {
                "coding": {
                    "id": "omim:601246",
                    "code": "601246",
                    "system": "https://www.omim.org/MIM:",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "ccds:CCDS32875",
                    "code": "CCDS32875",
                    "system": "http://www.ncbi.nlm.nih.gov/CCDS/CcdsBrowse.cgi?REQUEST=CCDS&DATA=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "pubmed:7600578",
                    "code": "7600578",
                    "system": "https://pubmed.ncbi.nlm.nih.gov/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "vega:OTTHUMG00000181922",
                    "code": "OTTHUMG00000181922",
                    "system": "https://vega.archive.ensembl.org/Homo_sapiens/Gene/Summary?g=",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "uniprot:Q13111",
                    "code": "Q13111",
                    "system": "http://purl.uniprot.org/uniprot/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "refseq:NM_005483",
                    "code": "NM_005483",
                    "system": "https://www.ncbi.nlm.nih.gov/nuccore/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "ena.embl:U20979",
                    "code": "U20979",
                    "system": "https://www.ebi.ac.uk/ena/browser/view/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "ucsc:uc002mal.4",
                    "code": "uc002mal.4",
                    "system": "http://genome.cse.ucsc.edu/cgi-bin/hgGene?org=Human&hgg_chrom=none&hgg_type=knownGene&hgg_gene=",
                },
                "relation": "relatedMatch",
            },
        ],
        "extensions": [
            {
                "name": "aliases",
                "value": [
                    "CAF1P150",
                    "MGC71229",
                    "CAF-1",
                    "P150",
                    "CAF1B",
                    "CAF1",
                    "LOC107985297",
                ],
            },
            {
                "name": "approved_name",
                "value": "chromatin assembly factor 1 subunit A",
            },
            {
                "name": "ensembl_locations",
                "value": [
                    {
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
                    {
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
            {"name": "ncbi_gene_type", "value": "protein-coding"},
            {
                "name": "hgnc_locus_type",
                "value": "gene with protein product",
            },
            {"name": "ensembl_biotype", "value": "protein_coding"},
            {
                "name": "previous_symbols",
                "value": ["LOC107985297"],
            },
            {"name": "strand", "value": "+"},
            {"name": "symbol_status", "value": "approved"},
        ],
    }
    return MappableConcept(**params)


@pytest.fixture(scope="module")
def normalized_loc_653303():
    """Provide test fixture for NCBI gene LOC653303. Used to validate
    normalized results that don't merge records.
    """
    params = {
        "conceptType": "Gene",
        "name": "LOC653303",
        "primaryCoding": {
            "id": "ncbigene:653303",
            "code": "653303",
            "system": "https://www.ncbi.nlm.nih.gov/gene/",
        },
        "mappings": [],
        "extensions": [
            {
                "name": "aliases",
                "value": ["LOC196266", "LOC654080", "LOC731196"],
            },
            {
                "name": "approved_name",
                "value": "proprotein convertase subtilisin/kexin type 7 pseudogene",
            },
            {
                "name": "ncbi_locations",
                "value": [
                    {
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
                "name": "previous_symbols",
                "value": ["LOC196266", "LOC731196", "LOC654080"],
            },
            {"name": "ncbi_gene_type", "value": "pseudo"},
            {"name": "strand", "value": "+"},
        ],
        "id": "normalize.gene.ncbigene:653303",
    }
    return MappableConcept(**params)


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
                        "label": "proprotein convertase subtilisin/kexin type 7 pseudogene",
                        "strand": "+",
                        "location_annotations": [],
                        "locations": [
                            {
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.2NkFm8HK88MqeNkCgj78KidCAXgnsfV1",
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
                        "locations": [],
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
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl",
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
                            {
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl",
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
                        "label": "acetylcholinesterase (Yt blood group)",
                        "strand": "-",
                        "location_annotations": [],
                        "locations": [
                            {
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
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
                        "label": "acetylcholinesterase (Yt blood group)",
                        "strand": "-",
                        "location_annotations": [],
                        "locations": [
                            {
                                "type": "SequenceLocation",
                                "sequenceReference": {
                                    "type": "SequenceReference",
                                    "refgetAccession": "SQ.F-LrLMe1SRpfUZHkQmvkVKFEGaoDeHul",
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
                        "label": "acetylcholinesterase (Yt blood group)",
                        "strand": None,
                        "location_annotations": [],
                        "locations": [],
                        "aliases": ["3.1.1.7"],
                        "previous_symbols": ["YT"],
                        "xrefs": ["ncbigene:43", "ensembl:ENSG00000087085"],
                        "associated_with": [
                            "ucsc:uc003uxi.4",
                            "vega:OTTHUMG00000157033",
                            "merops:S09.979",
                            "omim:100740",
                            "iuphar:2465",
                            "refseq:NM_015831",
                            "pubmed:1380483",
                            "uniprot:P22303",
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
        "conceptType": "Gene",
        "id": "normalize.gene.hgnc:5447",
        "primaryCoding": {
            "id": "hgnc:5447",
            "code": "HGNC:5447",
            "system": "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/",
        },
        "name": "IFNR",
        "mappings": [
            {
                "coding": {
                    "id": "ncbigene:3466",
                    "code": "3466",
                    "system": "https://www.ncbi.nlm.nih.gov/gene/",
                },
                "relation": "exactMatch",
            },
            {
                "coding": {
                    "id": "pubmed:1906174",
                    "code": "1906174",
                    "system": "https://pubmed.ncbi.nlm.nih.gov/",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "omim:147573",
                    "code": "147573",
                    "system": "https://www.omim.org/MIM:",
                },
                "relation": "relatedMatch",
            },
            {
                "coding": {
                    "id": "pubmed:1193239",
                    "code": "1193239",
                    "system": "https://pubmed.ncbi.nlm.nih.gov/",
                },
                "relation": "relatedMatch",
            },
        ],
        "extensions": [
            {
                "name": "aliases",
                "value": ["IFNGM", "IFNGM2"],
            },
            {
                "name": "approved_name",
                "value": "interferon production regulator",
            },
            {"name": "symbol_status", "value": "approved"},
            {"name": "symbol_status", "value": "approved"},
            {"name": "ncbi_gene_type", "value": "unknown"},
            {"name": "hgnc_locus_type", "value": "unknown"},
            {"name": "location_annotations", "value": ["16"]},
        ],
    }
    return MappableConcept(**params)


@pytest.fixture(scope="module")
def num_sources():
    """Get the number of sources."""
    return len(set(SourceName))


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
    assert resp.gene.primaryCoding.id == expected_gene.id.split("normalize.gene.")[-1]
    compare_gene(expected_gene, resp.gene)
    if not expected_source_meta:
        assert resp.source_meta_ == {}
    else:
        resp_source_meta_keys = resp.source_meta_.keys()
        assert len(resp_source_meta_keys) == len(expected_source_meta), (
            "source_meta_keys"
        )
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
        assert loc.id.split("ga4gh:SL.")[-1] == loc.digest
        loc.id = None
        loc.digest = None
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
    for ext in actual.extensions:
        if ext.name.endswith("_locations"):
            for loc in ext.value:
                loc_id = loc.pop("id")
                loc_digest = loc.pop("digest")
                assert loc_id.split("ga4gh:SL.")[-1] == loc_digest
    diff = DeepDiff(test, actual, ignore_order=True)
    assert diff == {}, test.id


def test_search_query(query_handler, num_sources):
    """Test that query returns properly-structured response."""
    resp = query_handler.search(" BRAF ")
    assert resp.query == "BRAF"
    matches = resp.source_matches
    assert isinstance(matches, dict)
    assert len(matches) == num_sources


def test_search_query_inc_exc(query_handler, num_sources):
    """Test that query incl and excl work correctly."""
    sources = "hgnc, ensembl, ncbi"
    resp = query_handler.search("BRAF", excl=sources)
    matches = resp.source_matches
    assert len(matches) == num_sources - len(sources.split())

    sources = "Hgnc, NCBi"
    resp = query_handler.search("BRAF", incl=sources)
    matches = resp.source_matches
    assert len(matches) == len(sources.split())
    assert SourceName.HGNC in matches
    assert SourceName.NCBI in matches

    sources = "HGnC"
    resp = query_handler.search("BRAF", excl=sources)
    matches = resp.source_matches
    assert len(matches) == num_sources - len(sources.split())
    assert SourceName.ENSEMBL in matches
    assert SourceName.NCBI in matches


def test_search_invalid_parameter_exception(query_handler):
    """Test that Invalid parameter exception works correctly."""
    with pytest.raises(InvalidParameterException):
        _ = query_handler.search("BRAF", incl="hgn")

    with pytest.raises(InvalidParameterException):
        resp = query_handler.search("BRAF", incl="hgnc", excl="hgnc")  # noqa: F841


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
