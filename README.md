facets
======

[![Build Status](https://travis-ci.org/spencerkclark/facets.svg?branch=master)](https://travis-ci.org/spencerkclark/facets)
[![Coverage Status](https://coveralls.io/repos/github/spencerkclark/facets/badge.svg?branch=master)](https://coveralls.io/github/spencerkclark/facets?branch=master)

Figures with precise control over overall width, plot aspect ratio,
between-plot spacing, and colorbar dimensions.

Description
-----------

This is a module that I use in practice
to produce both single and multi-panel figures for presentations and
manuscripts. The reason I have gone through the trouble to write something
like this is that I am particular about a few things:

- I want tight, but easy, control over the space in between the panels of my
  figures in real space (not relative space).
- I want tight control over the aspect ratio of the panels of my figure (e.g.
  when plotting maps), but still work within a strict dimensional constraint
  over the entire figure (e.g. I want to make a figure to fit in a column of a
  manuscript).
- I want to make sure that the colorbars in all
  of my figures have the same thickness throughout my presentations or
  manuscripts; unfortunately it is hard to control this using the default 
  `matplotlib` tools (you can set the thickness in relative space, but you 
  need to be careful about what that means within the context of your 
  figure size).

I have recently re-written the entire module to make it easier to add different
layouts.  Previously, the only two layouts enabled were a basic grid layout
with no colorbar, and a grid layout with a common colorbar at the bottom of the
figure.  Now one could add a common colorbar to the bottom, left, top, or right
of the figure, or one can add colorbars to each panel (also on the bottom,
left, top, or right).

Another project with a similar motivation is [panel-plots](
https://github.com/ajdawson/panel-plots); however it does not have support
for adding colorbars to a dimensionally-constrained figure.  Some of the
re-write here was inspired by ideas in that project.  In particular, 
adding user-settable padding to the edges of the figure (to add
space for axes ticks, ticklabels, and labels) was a really good idea
implemented in `panel-plots`; it eliminates the need for using
`bbox_inches='tight'` when saving the figure, and enables the user to make sure
that their figures are *exactly* the dimensions they need for their use.  Also,
using `fig.add_axes(rect)` (as is done in `panel-plots`) is a much cleaner way of constructing axes with
specific sizes and positions than what was implemented here previously.

Examples
--------

This is a simple multi-panel plot with no colorbar(s):
```python
import matplotlib.pyplot as plt
import numpy

from facets import facets


fig, axes = facets(2, 3, width=8., aspect=0.6,
                   internal_pad=0.2, top_pad=0.5,
                   bottom_pad=0.5, left_pad=0.5, 
                   right_pad=0.5)

x = np.linspace(0., 6. * np.pi)
y = np.sin(x)

for ax in axes:
    ax.plot(x, y)
    ax.set_yticks(np.arange(-1., 1.2, 0.5))
    ax.set_xticks(np.arange(0., 18.1, 3.))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
axes[0].set_yticklabels(np.arange(-1., 1.2, 0.5))
axes[3].set_yticklabels(np.arange(-1., 1.2, 0.5))

axes[3].set_xticklabels(np.arange(0., 18.1, 3.))
axes[4].set_xticklabels(np.arange(0., 18.1, 3.))
axes[5].set_xticklabels(np.arange(0., 18.1, 3.))

fig.savefig('basic-grid-example.png')
```

![basic-grid-example.png](facets/examples/basic-grid-example.png?raw=true)

This is a multi-panel plot with a common colorbar:
```python
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

from facets import facets


fig, axes, cax = facets(
    2, 3, width=8., 
    internal_pad=0.2, top_pad=0.5,
    bottom_pad=0.5, left_pad=0.5, right_pad=1.,
    cbar_mode='figure', cbar_long_side_pad=0.1,
    cbar_short_side_pad=0.1, cbar_location='right')
    
x = np.linspace(0., 6. * np.pi)
y = np.linspace(0., 6. * np.pi)
xg, yg = np.meshgrid(x, y)
z = np.sin(xg) * np.cos(yg)
levels = np.arange(-1., 1.05, 0.1)

for ax in axes:
    ax.contourf(x, y, z, levels=levels, cmap='RdBu_r')
    ax.set_yticks(np.arange(0., 18.1, 6.))
    ax.set_xticks(np.arange(0., 18.1, 6.))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
axes[0].set_yticklabels(np.arange(0., 18.1, 6.))
axes[3].set_yticklabels(np.arange(0., 18.1, 6.))

axes[3].set_xticklabels(np.arange(0., 18.1, 6.))
axes[4].set_xticklabels(np.arange(0., 18.1, 6.))
axes[5].set_xticklabels(np.arange(0., 18.1, 6.))

cbar = mpl.colorbar.ColorbarBase(cax, cmap=cmap,
                                 boundaries=levels,
                                 orientation='vertical')
cbar.set_label('Example')

fig.savefig('colorbar-grid-example.png')
```

![colorbar-grid-example.png](facets/examples/colorbar-grid-example.png?raw=true)

Finally, this is an example of a multi-panel plot with colorbars attached to
every panel:
```python

fig, axes, caxes = facets(
    2, 3, width=8., 
    internal_pad=0.7, top_pad=0.5,
    bottom_pad=0.5, left_pad=0.5, right_pad=0.5,
    cbar_mode='tile', cbar_long_side_pad=0.1,
    cbar_short_side_pad=0.0, cbar_location='right')

x = np.linspace(0., 6. * np.pi)
y = np.linspace(0., 6. * np.pi)
xg, yg = np.meshgrid(x, y)
z = np.sin(xg) * np.cos(yg)
levels = np.arange(-1., 1.05, 0.1)

for ax in axes:
    ax.contourf(x, y, z, levels=levels, cmap='RdBu_r')
    ax.set_yticks(np.arange(0., 18.1, 6.))
    ax.set_xticks(np.arange(0., 18.1, 6.))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
axes[0].set_yticklabels(np.arange(0., 18.1, 6.))
axes[3].set_yticklabels(np.arange(0., 18.1, 6.))

axes[3].set_xticklabels(np.arange(0., 18.1, 6.))
axes[4].set_xticklabels(np.arange(0., 18.1, 6.))
axes[5].set_xticklabels(np.arange(0., 18.1, 6.))

for cax in caxes:
    cmap = mpl.cm.RdBu_r
    cbar = mpl.colorbar.ColorbarBase(cax, cmap=cmap,
                                     boundaries=levels,
                                     orientation='vertical')
    cbar.set_label('Example')
    cbar.set_ticks(np.arange(-1., 1.01, 0.5))

fig.savefig('multi-colorbar-grid-example.png')
```

![multi-colorbar-grid-example.png](facets/examples/multi-colorbar-grid-example.png?raw=true)

Some examples of the current API can be found in the Jupyter notebook in this
repository. 
