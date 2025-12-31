"""Make package version accessible from docs"""

import importlib.metadata


def on_config(config, **kwargs):
    config["extra"]["version"] = importlib.metadata.version("gene-normalizer")
    return config
