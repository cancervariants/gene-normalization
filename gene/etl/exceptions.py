"""Provide ETL-specific exceptions."""


class NormalizerEtlError(Exception):
    """Base ETL exception."""


class FileVersionError(NormalizerEtlError):
    """Raise when unable to parse version number from saved data file."""


class SourceFormatError(NormalizerEtlError):
    """Raise when source data formatting is incompatible with the source transformation
    methods: for example, if columns in a CSV file have changed.
    """


class SourceFetchError(NormalizerEtlError):
    """Raise during data acquisition when data fetch fails (e.g. unable to get latest
    version number, or connection failure during download)
    """
