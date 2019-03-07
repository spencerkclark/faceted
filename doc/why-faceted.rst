Why faceted?
============

At first glance it might seem we are re-inventing the wheel here.  If you just
google for "matplotlib subplots with shared colorbar" you'll find `a
StackOverflow question
<https://stackoverflow.com/questions/13784201/matplotlib-2-subplots-1-colorbar>`_
with numerous answers with varying levels of 
complexity (some in fact are quite elegant).  It might be tempting to go with
one of these solutions, e.g.

.. ipython:: python
    :okwarning:

    import xarray as xr
    import matplotlib.pyplot as plt

    ds = xr.tutorial.load_dataset('rasm').isel(time=slice(0, 3))
    fig, axes = plt.subplots(1, 3, figsize=(8, 4))

    for i, ax in enumerate(axes):
          c = ds.Tair.isel(time=i).plot.pcolormesh(
              ax=ax, add_colorbar=False, vmin=-30, vmax=30)
    plt.tight_layout()
    
    @savefig example_tair.png
    fig.colorbar(c, ax=axes.ravel().tolist(), orientation='horizontal',
        label='Air temperature');

This looks ok, but things become a bit more challenging when we'd like to
have a more control over the spacing and size of elements in the figure.
:py:mod:`matplotlib` is super-flexible in that it is indeed *possible* to do this,
but if your starting point for creating paneled figures is
:py:meth:`matplotlib.pyplot.subplots`, which it so often is for many of us,
your options for exerting this type of control are somewhat tricky to use.

Let's take the example above and start to impose some contraints:

- Tight layout does a decent job of finding the right between-panel padding
  based on the axes labels, but I'd rather have direct control over this.
  Let's impose a horizontal padding of half an inch between panels.
- The colorbar is rather thick.  Let's set it to a fixed width of an eighth of
  an inch.  This thickness *should not* depend on the overall dimensions of the
  figure.
- The data we are plotting is geographic in nature; we really should be using
  :py:mod:`cartopy`, which will require that the panels have a strict aspect ratio,
  related to the extent of the domain in latitude-longitude space.  Currently
  the aspect ratio is set dynamically based on the total figure size and
  :py:mod:`matplotlib` defaults for between-plot spacing and outer padding.
  
One by one we'll go through these illustrating how much complexity this adds to
our code just to produce a simple figure.

Fixing the between-plot spacing
-------------------------------

As soon as we try to assign a certain amount of physical space to a plot
element, we need to do some algebra.  This is because to change the panel
spacing after a call to :py:meth:`matplotlib.pyplot.subplots`, we need to use
:py:meth:`matplotlib.pyplot.subplots_adjust`, which takes parameters representing an amount of
*relative* space, meaning expressed as a fraction of a plot element, be it the
whole figure or a single panel.

To help set up the problem, let's define some variables.  First,
let's say that we have :math:`m` rows of :math:`n` panels each; in our example
:math:`m = 1` and :math:`n = 3`.  Then let's say that we would like to
introduce an internal pad, :math:`p_{internal}`, representing the spacing
between the axes in inches.  In order to use :py:meth:`matplotlib.pyplot.subplots_adjust`, we need
to determine the amount of relative space :math:`p_{internal}` represents.  In
the context of the ``wspace`` parameter, the parameter that controls the
spacing between panels, we need to determine the ratio of the width of the
internal padding and the width of a single panel :math:`w_{panel}`. For
a figure of width :math:`w`, with outer left and right paddings of
:math:`p_{left}` and :math:`p_{right}` the width of a single panel is given by:

.. math::

   w_{panel} = \frac{w - p_{left} - p_{right} - (n - 1) p_{internal}}{n}.

Therefore the value we pass to ``wspace`` in :py:meth:`matplotlib.pyplot.subplots_adjust` is:

.. math::

   \texttt{wspace} = \frac{p_{internal}}{w_{panel}}.

Finally, since in this process we needed to fix the left and right pads of the
figure, we need to specify those in :py:meth:`matplotlib.pyplot.subplots_adjust` too; note these are
defined relative to the full figure width rather than the width of single panel:

.. math::

   \texttt{left} = \frac{p_{left}}{w}

.. math::

   \texttt{right} = \frac{w - p_{right}}{w}.

Writing this all out in code gives:

.. ipython:: python

    w = 8.0
    p_left = 0.5
    p_right = 0.5
    m, n = (1, 3)
    p_internal = 0.5
    w_panel = (w - p_left - p_right - (n - 1) * p_internal) / n

    wspace = p_internal / w_panel
    left = p_left / w
    right = (w - p_right) / w

If we use these values when plotting we get:
    
.. ipython:: python
    :okwarning:

    fig, axes = plt.subplots(1, 3, figsize=(w, 4), sharey=True)
    
    for i, ax in enumerate(axes):
          c = ds.Tair.isel(time=i).plot.pcolormesh(
              ax=ax, add_colorbar=False, vmin=-30, vmax=30)
    fig.subplots_adjust(left=left, right=right, wspace=wspace)
    
    @savefig example_tair_adjusted.png
    fig.colorbar(c, ax=axes.ravel().tolist(), orientation='horizontal',
        label='Air temperature');

Fixing the colorbar thickness
-----------------------------

Keeping the colorbar thickness constant introduces some additional challenges.
Since ``fig.colorbar`` locates it on the bottom of the plot, we'll need to set
top and bottom pads for the figure, :math:`p_{top}` and
:math:`p_{bottom}`, a pad between the
colorbar and the panels, :math:`p_{cbar}`, a thickness for the colorbar,
:math:`w_{cbar}` and a height for the overall figure :math:`h`:

.. ipython:: python

    p_top = 0.5
    p_bottom = 0.5
    p_cbar = 0.5
    w_cbar = 0.125
    h = 4.

The top and bottom pads need to be passed to
:py:meth:`matplotlib.pyplot.subplots_adjust` and they 
follow similar conventions to the left and right pads, i.e. they are defined in
terms of length relative to the overall height of the figure.  The size of the
colorbar is controlled differently; we control its size when we construct it
using :py:meth:`matplotlib.pyplot.colorbar`, using the ``fraction``, ``pad``,
and ``aspect`` arguments.  ``fraction`` dictates the fraction of the height of
the colorbar would take with respect to the height of a single panel in the
*original* figure; ``pad`` dictates the fraction of a single panel in the
*original* figure the padding between the colorbar and panels would take; and
``aspect`` sets the ratio of the width of the long part of the colorbar to its
thickness. Note that since we call :py:meth:`matplotlib.pyplot.subplots_adjust`
before calling :py:meth:`matplotlib.pyplot.colorbar`, the panel height in the
original figure is determined in part by our imposed :math:`p_{top}` and
:math:`p_{bottom}`. In this case since we are only using a single row of
panels, we do not need to worry about the between panel spacing in this
dimension, but we'll include the  :math:`p_{internal}` term to keep things
general: 

.. math::

   h_{panel-original} = \frac{h - p_{top} - p_{bottom}}{m + p_{internal} (m - 1)}

.. math::

   \texttt{fraction} = \frac{w_{cbar}}{h_{panel-original}}

.. math::

   \texttt{pad} = \frac{p_{cbar}}{h_{panel-original}}

.. math::

   \texttt{aspect} = \frac{w - p_{left} - p_{right}}{w_{cbar}}.
   
.. ipython:: python

    h_panel_original = h - p_top - p_bottom
    fraction = w_cbar / h_panel_original
    pad = p_cbar / h_panel_original
    cbar_aspect = (w - p_left - p_right) / w_cbar
    top = (h - p_top) / h
    bottom = p_bottom / h

.. ipython:: python
    :okwarning:

    fig, axes = plt.subplots(1, 3, figsize=(w, h), sharey=True)
    
    for i, ax in enumerate(axes):
          c = ds.Tair.isel(time=i).plot.pcolormesh(
              ax=ax, add_colorbar=False, vmin=-30, vmax=30)
    fig.subplots_adjust(left=left, right=right, wspace=wspace, top=top, bottom=bottom)
    
    @savefig example_tair_adjusted_cbar.png
    fig.colorbar(c, ax=axes.ravel().tolist(), orientation='horizontal',
        label='Air temperature', fraction=fraction, pad=pad, aspect=cbar_aspect);   
        
Holding panels at a fixed aspect ratio
--------------------------------------

Things are starting to look much better, but there's still more work to do.
Let's introduce :py:mod:`cartopy` to the mix.  Adding a :py:mod:`cartopy`
projection turns 
out to fix the aspect ratio of the panels in the figure, regardless of the
figure size.  We'll want to address this additional constraint by adjusting our
value for the total height of the figure, because the panel height will now by
completely determined by the panel width.  In a
:py:class:`cartopy.crs.PlateCarree` projection, the 
aspect ratio will be determined by the ratio of the latitudinal extent of the
map divided by the longitudinal extent.  In this case it will be
:math:`\texttt{aspect} = \frac{75}{360}`.  :math:`h_{panel}` will now be
determined completely based on this aspect ratio and the panel width,
:math:`w_{panel}` we determined earlier:

.. math::

   h_{panel} = a w_{panel}.

The total height, :math:`h` is now just the sum of the height of the plot
elements:

.. math::

   h = m h_{panel} + (m - 1) p_{internal} + p_{bottom} + p_{top} + p_{cbar} + w_{cbar}.

As a result of the height values changing, we'll need to update the ``bottom`` and
``top`` parameters for :py:meth:`matplotlib.pyplot.subplots_adjust` as well as
the colorbar size parameters:
   
.. ipython:: python

    a = 75. / 360.
    p_cbar = 0.25
    h_panel = a * w_panel
    h = p_bottom + p_top + h_panel + p_cbar + w_cbar
    h_panel_original = h - p_top - p_bottom
    fraction = w_cbar / h_panel_original
    pad = p_cbar / h_panel_original
    cbar_aspect = (w - p_left - p_right) / w_cbar
    top = (h - p_top) / h
    bottom = p_bottom / h

.. ipython:: python
    :okwarning:

    import cartopy.crs as ccrs

    ds = xr.tutorial.load_dataset('rasm').isel(time=slice(0, 3))
    fig, axes = plt.subplots(1, 3, figsize=(w, h),
        subplot_kw={'projection': ccrs.PlateCarree()})

    for i, ax in enumerate(axes):
          c = ds.Tair.isel(time=i).plot.pcolormesh(
              ax=ax, x='xc', y='yc', add_colorbar=False, vmin=-30, vmax=30,
              transform=ccrs.PlateCarree())
          ax.coastlines()
          ax.set_extent([-180, 180, 15, 90], crs=ccrs.PlateCarree())

    fig.subplots_adjust(left=left, right=right, wspace=wspace, top=top, bottom=bottom)
    
    @savefig example_tair_adjusted_cartopy.png
    fig.colorbar(c, ax=axes.ravel().tolist(), orientation='horizontal',
        label='Air temperature', fraction=fraction, pad=pad, aspect=cbar_aspect);

As examples go, this one was actually fairly simple; we only had one row of
panels, rather than multiple, and we only had one colorbar.  Taking the
:py:meth:`matplotlib.pyplot.subplots` approach was remarkably complicated.
Admittedly, it would be 
*slightly* more straightforward to use the :py:class:`mpl_toolkits.axes_grid1.AxesGrid` framework to do this,
but other problems remain with that approach; e.g. using :py:class:`mpl_toolkits.axes_grid1.AxesGrid` with
cartopy is not ideal due to axes sharing issues (`SciTools/cartopy#939
<https://github.com/SciTools/cartopy/issues/939>`_), and colorbars drawn using
:py:class:`mpl_toolkits.axes_grid1.AxesGrid` are drawn using an outdated colorbar class in :py:mod:`matplotlib`,
which is different than the one used by default (`matplotlib/matplotlib#9778
<https://github.com/matplotlib/matplotlib/issues/9778>`_). In
:py:meth:`faceted.faceted` we use :py:class:`mpl_toolkits.axes_grid1.AxesGrid` to aid in the placing the axes
and colorbars (some math is still required to determine the figure height), but
we do not use the axes generated by it.  Instead we create our own, 
which are modern and have working axes-sharing capabilities.  In so doing we
create a :py:meth:`matplotlib.pyplot.subplots`-like interface, which is
slightly more intuitive to use than :py:class:`mpl_toolkits.axes_grid1.AxesGrid`.

How would you do this in faceted?
---------------------------------

In :py:meth:`faceted.faceted` this becomes much simpler; there is no need to do any algebra
or post-hoc adjustment of the axes placement; everything gets handled in the
top-level function.

.. ipython:: python
    :okwarning:

    from faceted import faceted

    fig, axes, cax = faceted(1, 3, width=w, aspect=a,
                             left_pad=p_left, right_pad=p_right,
                             bottom_pad=p_bottom, top_pad=p_top,
                             internal_pad=p_internal,
                             cbar_mode='single', cbar_location='bottom',
                             cbar_size=w_cbar, cbar_pad=p_cbar, cbar_short_side_pad=0.,
                             axes_kwargs={'projection': ccrs.PlateCarree()})

    for i, ax in enumerate(axes):
          c = ds.Tair.isel(time=i).plot.pcolormesh(
              ax=ax, x='xc', y='yc', add_colorbar=False, vmin=-30, vmax=30,
              transform=ccrs.PlateCarree())
          ax.coastlines()
          ax.set_extent([-180, 180, 15, 90], crs=ccrs.PlateCarree())

     @savefig example_tair_faceted.png     
     plt.colorbar(c, cax=cax, orientation='horizontal',
                  label='Air temperature');


What can't you do in faceted?
-----------------------------

The main thing that :py:meth:`faceted.faceted` cannot do is create a
constrained set of axes 
that have varying size, or varying properties. For more complex figure
construction tasks we recommend using a more fundamental :py:mod:`matplotlib`
approach, either using :py:class:`mpl_toolkits.axes_grid1.AxesGrid`,
:py:class:`matplotlib.GridSpec`, or `Constrained Layout
<https://matplotlib.org/tutorials/intermediate/constrainedlayout_guide.html#>`_. The
main reason for creating :py:meth:`faceted.faceted` was that these other tools
were *too* flexible at the expense of simplicity.  For a large percentage of
the use cases, they are not required, but for the remaining percentage they are
indeed quite useful.
