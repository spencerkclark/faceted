facets
======

[![Build Status](https://travis-ci.org/spencerkclark/facets.svg?branch=master)](https://travis-ci.org/spencerkclark/facets)
[![Coverage Status](https://coveralls.io/repos/github/spencerkclark/facets/badge.svg?branch=master)](https://coveralls.io/github/spencerkclark/facets?branch=master)

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

fig.savefig('basic-grid-example.png')
```

![basic-grid-example.png](facets/examples/basic-grid-example.png?raw=true)

This is a multi-panel plot with a common colorbar.  Note that
despite [matplotlib/matplotlib#9778](https://github.com/matplotlib/matplotlib/issues/9778)
we can draw a colorbar in the standard way with `extend='both'` specified in
the filled contour plot.  This is because we replace the colorbar axes
generated in `AxesGrid` (which are of type
`mpl_toolkits.axes_grid1.axes_grid.CbarAxes`) with standard `matplotlib` axes
objects (of type `matplotlib.axes._axes.Axes`).
```python
import matplotlib.pyplot as plt
import numpy as np

from facets import facets


fig, axes, cax = facets(
    2, 3, width=8., 
    internal_pad=0.2, top_pad=0.5,
    bottom_pad=0.5, left_pad=0.5, right_pad=1.,
    cbar_mode='single', cbar_pad=0.1,
    cbar_short_side_pad=0.1, cbar_location='right')
    
x = np.linspace(0., 6. * np.pi)
y = np.linspace(0., 6. * np.pi)
xg, yg = np.meshgrid(x, y)
z = np.sin(xg) * np.cos(yg)
levels = np.arange(-1., 1.05, 0.1)

for ax in axes:
    c = ax.contourf(x, y, z, levels=levels, cmap='RdBu_r', extend='both')
    ax.set_yticks(np.arange(0., 18.1, 6.))
    ax.set_xticks(np.arange(0., 18.1, 6.))

plt.colorbar(c, cax=cax, orientation='vertical', label='Example')

fig.savefig('colorbar-grid-example.png')
```

![colorbar-grid-example.png](facets/examples/colorbar-grid-example.png?raw=true)

Finally, this is an example of a multi-panel plot with colorbars attached to
every panel:
```python
import matplotlib.pyplot as plt
import numpy as np

from facets import facets


fig, axes, caxes = facets(
    2, 3, width=8., 
    internal_pad=0.7, top_pad=0.5,
    bottom_pad=0.5, left_pad=0.5, right_pad=0.5,
    cbar_mode='each', cbar_pad=0.1,
    cbar_short_side_pad=0.0, cbar_location='right')

x = np.linspace(0., 6. * np.pi)
y = np.linspace(0., 6. * np.pi)
xg, yg = np.meshgrid(x, y)
z = np.sin(xg) * np.cos(yg)
levels = np.arange(-1., 1.05, 0.1)

for ax, cax in zip(axes, caxes):
    c = ax.contourf(x, y, z, levels=levels, cmap='RdBu_r')
    ax.set_yticks(np.arange(0., 18.1, 6.))
    ax.set_xticks(np.arange(0., 18.1, 6.))
    plt.colorbar(c, cax, label='Example', orientation='vertical',
                 ticks=np.arange(-1., 1.01, 0.5))

fig.savefig('multi-colorbar-grid-example.png')
```

![multi-colorbar-grid-example.png](facets/examples/multi-colorbar-grid-example.png?raw=true)
