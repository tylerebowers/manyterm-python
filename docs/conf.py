# Configuration file for the Sphinx documentation builder.
import os
import sys

project = 'Manyterm'
copyright = '2024, Tyler Bowers'
author = 'Tyler Bowers'
release = '1.0.1'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]
autosummary_generate = True

sys.path.insert(0, os.path.abspath('../..'))
#templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

#html_theme = 'alabaster'
#html_static_path = ['_static']
