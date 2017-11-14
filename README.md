facets
------

This is a module that I use in practice
to produce both single and multi-panel figures for presentations and
manuscripts.  The reason I have gone through the trouble to write something
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

This module is not perfect -- one minor flaw in the design is
that it does not in any way take into account the size of the font used for the
axes labels.  Therefore, the total width of the figure, when saved using
`bbox_inches='tight'` argument in `matplotlib`, is not *exactly* as specified,
but for most cases it is close (so influences of scaling when put in
presentations or manuscripts are small).  Another is that currently it only
supports adding a uniform colorbar at the bottom of the figure.  You cannot add
colorbars to each panel, or to any other side of the figure.  Lastly, there are
no `sharex` or `sharey` options, so axes ticks and tick labels must be
controlled manually.  Those drawbacks
aside, I have found this module to be unreasonably effective at satisfying my
needs over the years.  Others have found it useful as well, so I am posting it
on GitHub as is for now, and may work on it more if I have the time and
motivation.

Another project, with a similar motivation is [panel-plots](
https://github.com/ajdawson/panel-plots); however it does not have any support
for adding colorbars.

Example usage
-------------

Here is a short example using `facets` for creating a set of plots each with an
aspect ratio of 0.6, and an overall figure width of 8.0.  The `pad` argument
specifies that we want a quarter inch in between each panel.

```python

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

from facets import facets

fig, axes = facets(2, 3, pad=0.25, aspect=0.6, width=8.0)

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

fig.savefig('facets_example.png', bbox_inches='tight')
```
![facets_example.png](facets_example.png?raw=true)

Here is an example of using `facets` to create a plot with a colorbar.  Note
that we are using the default `cbar_thickness`, which is set to an eighth of an
inch.
```python

fig, axes, cax = facets(2, 3, pad=0.3, aspect=1.0, width=7.0, cbar=True)

x = np.linspace(0., 6. * np.pi)
y = np.linspace(0., 6. * np.pi)
xg, yg = np.meshgrid(x, y)
z = np.sin(xg) * np.cos(yg)
levels = np.arange(-1., 1.05, 0.1)

for ax in axes:
    ax.contourf(x, y, z, levels=levels, cmap='RdBu_r')
    ax.set_yticks(np.arange(0., 18.1, 3.))
    ax.set_xticks(np.arange(0., 18.1, 3.))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
axes[0].set_yticklabels(np.arange(0., 18.1, 3.))
axes[3].set_yticklabels(np.arange(0., 18.1, 3.))

axes[3].set_xticklabels(np.arange(0., 18.1, 3.))
axes[4].set_xticklabels(np.arange(0., 18.1, 3.))
axes[5].set_xticklabels(np.arange(0., 18.1, 3.))

cmap = mpl.cm.RdBu_r
cbar = mpl.colorbar.ColorbarBase(cax, cmap=cmap,
                                 boundaries=levels,
                                 orientation='horizontal')
cbar.set_label('Example')
fig.savefig('facets_example2.png', bbox_inches='tight')
```
![facets_example2.png](facets_example2.png?raw=true)
