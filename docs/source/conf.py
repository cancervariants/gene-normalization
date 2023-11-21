# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Gene Normalizer"
copyright = "2023, VICC"
author = "VICC"
html_title = "Gene Normalizer"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.linkcode",
    "sphinx_copybutton",
    "sphinx_click",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = []
html_css_files = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css",
]
html_theme_options = {
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/cancervariants/gene-normalization",
            "html": "",
            "class": "fa-brands fa-solid fa-github",
        },
        {
            "name": "Wagner Lab",
            "url": "https://www.nationwidechildrens.org/specialties/institute-for-genomic-medicine/research-labs/wagner-lab",
            "html": "",
            "class": "fa-solid fa-house",
        },
        {
            "name": "Twitter",
            "url": "https://twitter.com/genomicmedlab",
            "html": "",
            "class": "fa-solid fa-brands fa-twitter",
        },
    ],
}
# -- autodoc things ----------------------------------------------------------
import os  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.abspath("../../gene"))
autodoc_preserve_defaults = True

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

# -- sphinx-click ------------------------------------------------------------
from typing import List

def process_description(app, ctx, lines: List[str]):
    """Format sphinx-click autodocs

    * Don't show function params (they're formatted weird)
    * Format shell command examples as Sphinx code blocks
    """
    param_boundary = None
    shell_block_line = None
    for i, line_number in enumerate(lines):
        if line_number.startswith("% "):
            if shell_block_line is not None:
                raise Exception("We'll need a more complicated solution to handle multiple examples: see docs/source/conf.py")
            shell_block_line = i
        if ":param" in line_number:
            print(line_number)
            param_boundary = i
            break
    if param_boundary is not None:
        del lines[param_boundary:]
        lines[-1] = ""

    if shell_block_line:
        new_section = [".. code-block:: sh", "", "   " + lines[shell_block_line]]
        del lines[shell_block_line]
        lines[shell_block_line:shell_block_line] = new_section


def setup(app):
    app.connect("sphinx-click-process-description", process_description)
