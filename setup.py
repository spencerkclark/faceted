import setuptools


LONG_DESCRIPTION = """
This is a module that I use in practice to produce both single and multi-panel
figures for presentations and manuscripts. The reason I have gone through the
trouble to write something like this is that I am particular about a few
things:

- I want tight, but easy, control over the space in between the panels of my
figures in real space (not relative space).
- I want tight control over the aspect ratio of the panels of my figure (e.g.
when plotting maps), but still work within a strict dimensional constraint over
the entire figure (e.g. I want to make a figure to fit in a column of a
manuscript).
- I want to make sure that the colorbars in all of my figures have the same
thickness throughout my presentations or manuscripts; unfortunately it is hard
to control this using the default matplotlib tools (you can set the thickness
in relative space, but you need to be careful about what that means within the
context of your figure size).
"""


setuptools.setup(
    name='faceted',
    version='0.1',
    packages=setuptools.find_packages(),
    author='Spencer K. Clark',
    description='Precisely spaced subplots',
    long_description=LONG_DESCRIPTION,
    install_requires=[
        'matplotlib >= 1.5',
        'numpy >= 1.7',
    ]
)
