import glob
import os
import sys

import pytest

import facets


def test_example_notebook():
    pytest.importorskip('nbformat')
    pytest.importorskip('nbconvert')
    pytest.importorskip('matplotlib')

    import nbformat
    from nbconvert.preprocessors import ExecutePreprocessor

    rootdir = os.path.join(facets.__path__[0], 'examples')
    with open(os.path.join(rootdir, 'examples.ipynb')) as nb_file:
        notebook = nbformat.read(nb_file, as_version=nbformat.NO_CONVERT)
    kernel_name = 'python' + str(sys.version[0])
    ep = ExecutePreprocessor(timeout=600, kernel_name=kernel_name)
    ep.preprocess(notebook, {})
