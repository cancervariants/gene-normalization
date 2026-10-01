"""boop beep boop normalize genes"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gene-normalizer")
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError
