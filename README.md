faceted
=======

[![Build Status](https://travis-ci.org/spencerkclark/faceted.svg?branch=master)](https://travis-ci.org/spencerkclark/faceted)[![Coverage Status](https://coveralls.io/repos/github/spencerkclark/faceted/badge.svg?branch=master)](https://coveralls.io/github/spencerkclark/faceted?branch=master)[![Documentation Status](https://readthedocs.org/projects/faceted/badge/?version=latest)](https://faceted.readthedocs.io/en/latest/?badge=latest)

Figures with precise control over overall width, plot aspect ratio,
between-plot spacing, and colorbar dimensions.

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

For information on how to use `faceted`, see the documentation:
https://faceted.readthedocs.io/en/latest/.

Installation
------------

Currently, the only way to install `faceted` is directly from the source.  You
can do so using `pip`:
```
$ git clone https://github.com/spencerkclark/faceted.git
$ cd faceted
$ pip install -e .
```
