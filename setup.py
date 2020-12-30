import setuptools

import versioneer

LONG_DESCRIPTION = """
The purpose of this module is to make it easy to produce single-or-multi-panel
figures in matplotlib with strict dimensional constraints. For example, perhaps
you would like to make a figure that fits exactly within a column of a
manuscript without any scaling, and you would like the panels to be as large as
possible, but retain a fixed aspect ratio (height divided by width). Maybe some
(or all) of your panels require an accompanying colorbar. With out of the box
matplotlib tools this is actually somewhat tricky.

Internally, this module uses the flexible [`matplotlib` `AxesGrid` toolkit](https://matplotlib.org/2.0.2/mpl_toolkits/axes_grid/users/overview.html#axes-grid1),
with some additional logic to enable making these kinds of
dimensionally-constrained
panel plots with precise padding and colorbar size(s).

Another project with a similar motivation is [panel-plots](
https://github.com/ajdawson/panel-plots); however it does not have support
for adding colorbars to a dimensionally-constrained figure.  One part of the
implementation there that inspired part of what is done here is the ability
to add user-settable padding to the edges of the figure (to add space for
axes ticks, ticklabels, and labels).  This eliminates the need for using
`bbox_inches='tight'` when saving the figure, and enables you
to make sure that your figures are *exactly* the dimensions you need for your
use.

Important links
---------------
- HTML documentation: https://faceted.readthedocs.io/en/latest/
- Issue tracker: https://github.com/spencerkclark/faceted/issues
- Source code: https://github.com/spencerkclark/faceted
"""


setuptools.setup(
    name="faceted",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=setuptools.find_packages(),
    author="Spencer K. Clark",
    author_email="spencerkclark@gmail.com",
    description="Precisely spaced subplots",
    long_description=LONG_DESCRIPTION,
    install_requires=[
        "matplotlib >= 1.5",
        "numpy >= 1.7",
    ],
    keywords="matplotlib cartopy multi-panel plots colorbars",
    url="https://github.com/spencerkclark/faceted",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
    ],
)
