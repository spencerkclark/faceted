facets
------

[![Build Status](https://travis-ci.org/spencerkclark/facets.svg?branch=master)](https://travis-ci.org/spencerkclark/facets)

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
figure.  In addition to those, I have now added support for a common colorbar
on the right of the figure, and colorbars at the bottom for every subplot in
the figure.

It should be straightforward to enable other colorbar positions (e.g. left
and top in the common colorbar case, and left, right, and top in the multiple
colobar case), but I have not gotten to that yet.  Other layouts like colorbars
on the ends of rows of subplots or columns of subplots should be possible
to add without too much effort too.

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

Some examples of the current API can be found in the Jupyter notebook in this
repository.  Eventually it would nice to add tests and a more formal package
structure to this project, but I am just posting it as is for now.
