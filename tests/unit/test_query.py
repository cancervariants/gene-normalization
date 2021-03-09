"""Module to test the query module."""
from gene.query import QueryHandler, InvalidParameterException
from gene.schemas import SourceName, MatchType
import pytest


@pytest.fixture(scope='module')
def query_handler():
    """Build query_handler test fixture."""
    class QueryGetter:

        def __init__(self):
            self.query_handler = QueryHandler()

        def search(self, query_str, keyed=False, incl='', excl=''):
            resp = self.query_handler.search_sources(query_str=query_str,
                                                     keyed=keyed,
                                                     incl=incl, excl=excl)
            return resp
    return QueryGetter()


@pytest.fixture(scope='module')
def num_sources():
    """Get the number of sources."""
    return len({s for s in SourceName})


def test_query(query_handler, num_sources):
    """Test that query returns properly-structured response."""
    resp = query_handler.search(' BRAF ')
    assert resp['query'] == 'BRAF'
    matches = resp['source_matches']
    assert isinstance(matches, list)
    assert len(matches) == num_sources


def test_query_keyed(query_handler, num_sources):
    """Test that query returns properly-structured response."""
    resp = query_handler.search(' BRAF ', keyed=True)
    assert resp['query'] == 'BRAF'
    matches = resp['source_matches']
    assert isinstance(matches, dict)
    assert len(matches) == num_sources


def test_query_inc_exc(query_handler, num_sources):
    """Test that query incl and excl work correctly."""
    sources = "hgnc, ensembl, ncbi"
    resp = query_handler.search('BRAF', excl=sources)
    matches = resp['source_matches']
    assert len(matches) == num_sources - len(sources.split())

    sources = 'Hgnc, NCBi'
    resp = query_handler.search('BRAF', keyed=True, incl=sources)
    matches = resp['source_matches']
    assert len(matches) == len(sources.split())
    assert 'HGNC' in matches
    assert 'NCBI' in matches

    sources = 'HGnC'
    resp = query_handler.search('BRAF', keyed=True, excl=sources)
    matches = resp['source_matches']
    assert len(matches) == num_sources - len(sources.split())
    assert 'Ensembl' in matches
    assert 'NCBI' in matches


def test_invalid_parameter_exception(query_handler):
    """Test that Invalid parameter exception works correctly."""
    with pytest.raises(InvalidParameterException):
        resp = query_handler.search('BRAF', keyed=True, incl='hgn')  # noqa: F841, E501

    with pytest.raises(InvalidParameterException):
        resp = query_handler.search('BRAF', incl='hgnc', excl='hgnc')  # noqa: F841, E501


def test_ncbi_43_query(query_handler, num_sources):
    """Test that ACHE concept_id shows a match for each source."""
    resp = query_handler.search('ncbigene:43', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.OTHER_ID
    assert matches['Ensembl']['match_type'] == MatchType.OTHER_ID
    assert matches['NCBI']['match_type'] == MatchType.CONCEPT_ID

    resp = query_handler.search('hgnc:108', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.CONCEPT_ID
    assert matches['Ensembl']['match_type'] == MatchType.OTHER_ID
    assert matches['NCBI']['match_type'] == MatchType.OTHER_ID

    resp = query_handler.search('ensembl:ENSG00000087085', keyed=True)
    matches = resp['source_matches']
    assert len(matches) == num_sources
    assert matches['HGNC']['match_type'] == MatchType.OTHER_ID
    assert matches['Ensembl']['match_type'] == MatchType.CONCEPT_ID
    assert matches['NCBI']['match_type'] == MatchType.NO_MATCH
