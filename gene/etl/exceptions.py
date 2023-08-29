"""Provide ETL-specific exceptions."""


class GeneNormalizerEtlError(Exception):
    """Base ETL exception."""


class GeneFileVersionError(GeneNormalizerEtlError):
    """Raise when unable to parse version number from saved data file."""


class GeneSourceFetchError(GeneNormalizerEtlError):
    """Raise during data acquisition when data fetch fails (e.g. unable to get latest
    version number, or connection failure during download)
    """
