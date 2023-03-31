# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Gene Normalizer'
copyright = '2023, VICC'
author = 'VICC'



# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# -- autodoc things ----------------------------------------------------------
extensions = ["sphinx.ext.autodoc", "sphinx_autodoc_typehints"]
import os
import sys
sys.path.insert(0, os.path.abspath("../../gene"))


# -- get version -------------------------------------------------------------
# from gene import __version__  # noqa: E402
# version = __version__
# release = version
