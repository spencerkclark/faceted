faceted
=======

[![Build
Status](https://github.com/spencerkclark/faceted/workflows/tests/badge.svg?branch=master)](https://github.com/spencerkclark/faceted/actions) [![codecov](https://codecov.io/gh/spencerkclark/faceted/branch/master/graph/badge.svg?token=H1DBBSTQ2V)](https://codecov.io/gh/spencerkclark/faceted) [![Documentation
Status](https://readthedocs.org/projects/faceted/badge/?version=latest)](https://faceted.readthedocs.io/en/latest/?badge=latest) [![PyPI](https://img.shields.io/pypi/v/faceted.svg)](https://pypi.python.org/pypi/faceted/) [![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

Figures with precise control over overall width, overall height,
plot aspect ratio, between-plot spacing, and colorbar dimensions.

Description
-----------

The purpose of this module is to make it easy to produce single-or-multi-panel
figures in `matplotlib` with strict dimensional constraints.  For example,
perhaps you would like to make a figure that fits exactly within a column of a
manuscript *without any scaling*, and you would like the panels to be as large
as possible, but retain a fixed aspect ratio (height divided by width).  Maybe
some (or all) of your panels require an accompanying colorbar.  With
out of the box `matplotlib` tools this is actually somewhat tricky.

![readme-example.png](readme-example.png?raw=true)

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
to make sure that your figures are *exactly* the dimensions you need for your use.

I intend to keep the scope of this project quite limited. I want the results it
produces to remain extremely easy to understand and control.  For more
complicated figure layouts, e.g. multiple panels with different sizes and
aspect ratios, and a more magical approach to setting figure boundary padding
and between-panel spacing, a library worth checking out is
[proplot](https://github.com/lukelbd/proplot).  The ["smart tight layout" feature
it provides](https://proplot.readthedocs.io/en/stable/why.html#id5) is an impressive 
automated method of solving some of the same problems addressed by this library.

For information on how to use `faceted`, see the documentation:
https://faceted.readthedocs.io/en/latest/.

Installation
------------

You can install `faceted` either from PyPI:
```
$ pip install faceted
```
or directly from source:
```
$ git clone https://github.com/spencerkclark/faceted.git
$ cd faceted
$ pip install -e .
```
