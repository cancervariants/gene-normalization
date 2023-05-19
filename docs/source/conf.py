# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Gene Normalizer'
copyright = '2023, VICC'
author = 'VICC'
html_title = "Gene Normalizer"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.linkcode",
    "sphinx_copybutton"
]

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = []

# -- autodoc things ----------------------------------------------------------
import os  # noqa: E402
import sys  # noqa: E402
sys.path.insert(0, os.path.abspath("../../gene"))


# -- get version -------------------------------------------------------------
from gene import __version__  # noqa: E402
version = __version__
release = version

# -- linkcode ----------------------------------------------------------------
def linkcode_resolve(domain, info):
    if domain != "py":
        return None
    if not info["module"]:
        return None
    filename = info["module"].replace(".", "/")
    return f"https://github.com/cancervariants/gene-normalization/blob/main/{filename}.py"  # noqa: E501

# -- code block style --------------------------------------------------------
pygments_style = "default"
pygements_dark_style = "monokai"
