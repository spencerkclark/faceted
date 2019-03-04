Using faceted
=============

``faceted`` is quite flexible.  Here are a couple of examples illustrating the
different features.  Using it in many ways resembles using ``plt.subplots``.

.. ipython:: python
    :okwarning:

    import matplotlib.pyplot as plt
    import xarray as xr
    from faceted import faceted

    ds = xr.tutorial.load_dataset('rasm').isel(x=slice(30, 37), y=-1,
                                               time=slice(0, 11))
    temp = ds.Tair
    
    fig, axes = faceted(2, 3, width=8)
    for i, ax in enumerate(axes):
        temp.isel(x=i).plot(ax=ax, marker='o', ls='none')
        ax.set_title('{:0.2f}'.format(temp.xc.isel(x=i).item()))
        ax.set_xlabel('Time')
        ax.set_ylabel('Temperature [C]')

    @savefig example_tair_base3.png
    fig.show()

        
Padding options
---------------

We'll notice that there are some padding issues in the above plot.  We can add
some padding using the outer and inner padding arguments.  Specifying an
``internal_pad`` as a tuple allows us to prescribe different horizontal and
vertical pad values; specifying a ``left_pad`` and ``bottom_pad`` allows us to
make room for the outer axes labels, while maintaining our prescribed figure
width. 

.. ipython:: python
    :okwarning:

    fig, axes = faceted(2, 3, width=8, left_pad=0.75, bottom_pad=0.75,
                        internal_pad=(0.33, 0.66))
    for i, ax in enumerate(axes):
        temp.isel(x=i).plot(ax=ax, marker='o', ls='none')
        ax.set_title('{:0.2f}'.format(temp.xc.isel(x=i).item()))
        ax.set_xlabel('Time')
        ax.set_ylabel('Temperature [C]')

    @savefig example_tair_padding4.png
    fig.show()
        
Sharing axes
------------

By default all axes are shared among the panels.  Let's say we wanted to plot a
different quantity on the bottom row of panels, so the y-axis would be
different.  Making use of the xarray tutorial dataset, we can plot an anomaly
from the time mean at each location in the lower row instead.

.. ipython:: python
    :okwarning:

    import numpy as np
             
    index = ds.indexes['time']
    time_weights = index.shift(1, 'MS') - index.shift(-1, 'MS')
    time_weights = xr.DataArray(time_weights, ds.time.coords)
    mean = (ds.Tair * time_weights).sum('time') / time_weights.where(np.isfinite(ds.Tair)).sum('time')
    anomaly = ds.Tair - mean
    
    fig, axes = faceted(2, 3, width=8, left_pad=0.75, bottom_pad=0.75,
                        internal_pad=(0.33, 0.66), sharey='row')
    for i, ax in enumerate(axes[:3]):
        temp.isel(x=i).plot(ax=ax, marker='o', ls='none')
        ax.set_title('{:0.2f}'.format(temp.xc.isel(x=i).item()))
        ax.set_xlabel('Time')
        ax.set_ylabel('Temperature [C]')

    for i, ax in enumerate(axes[3:]):
        anomaly.isel(x=i).plot(ax=ax, marker='o', ls='none')
        ax.set_title('{:0.2f}'.format(temp.xc.isel(x=i).item()))
        ax.set_xlabel('Time')
        ax.set_ylabel('Anomaly [C]')
        
    @savefig example_tair_share_axes.png
    fig.show()    
    
Colorbar modes and locations
----------------------------

Let's say we are plotting 2D data in the form of pcolormesh plots that require
a colorbar.  ``faceted`` comes with a number of options for placing and sizing
colorbars in a paneled figure.  We can add a colorbar to a figure by modifying
the ``cbar_mode`` argument; by default it is set to ``None``, meaning no
colorbar, as in the plots above.  For all of the examples here, we'll just plot
a time series of maps.  Since the xarray tutorial data is geographic in nature,
we'll also use this opportunity to show how to use ``cartopy`` with
``faceted``.

Single colorbar
###############

A single colorbar is useful when we use the same color scale for all panels of
a figure.  

.. ipython:: python
    :okwarning:

    import cartopy.crs as ccrs

    ds = xr.tutorial.load_dataset('rasm')
    
    aspect = 75. / 180.
    fig, axes, cax = faceted(2, 3, width=8, aspect=aspect,
                             bottom_pad=0.75, cbar_mode='single',
                             cbar_pad=0.1, internal_pad=0.1,
                             cbar_location='bottom', cbar_short_side_pad=0.,
                             axes_kwargs={'projection': ccrs.PlateCarree()})
    for i, ax in enumerate(axes):
        c = ds.Tair.isel(time=i).plot(
            ax=ax, add_colorbar=False, transform=ccrs.PlateCarree(),
            vmin=-30, vmax=30, x='xc', y='yc')
        ax.set_title('')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_extent([-180, 0, 15, 90], crs=ccrs.PlateCarree())
        ax.coastlines()

    plt.colorbar(c, cax=cax, orientation='horizontal', label='Temperature [C]');
        
    @savefig example_tair_single_cbar.png
    fig.show()

Edge colorbars
##############

Edge colorbars are useful when rows or columns of a figure share a colorbar.
We'll show an example where the rows share a colorbar.

.. ipython:: python
    :okwarning:

    aspect = 75. / 180.
    fig, axes, (cax1, cax2) = faceted(2, 3, width=8, aspect=aspect, right_pad=0.75,
                                      cbar_mode='edge',
                                      cbar_pad=0.1, internal_pad=0.1,
                                      cbar_location='right', cbar_short_side_pad=0.,
                                      axes_kwargs={'projection': ccrs.PlateCarree()})
    for i, ax in enumerate(axes[:3]):
        c1 = ds.Tair.isel(time=i).plot(
            ax=ax, add_colorbar=False, transform=ccrs.PlateCarree(),
            vmin=-30, vmax=30, x='xc', y='yc')
        ax.set_title('')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_extent([-180, 0, 15, 90], crs=ccrs.PlateCarree())
        ax.coastlines()

    plt.colorbar(c1, cax=cax1, label='[C]');

    for i, ax in enumerate(axes[3:], start=3):
        c2 = ds.Tair.isel(time=i).plot(
            ax=ax, add_colorbar=False, transform=ccrs.PlateCarree(),
            vmin=-50, vmax=50, x='xc', y='yc')
        ax.set_title('')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_extent([-180, 0, 15, 90], crs=ccrs.PlateCarree())
        ax.coastlines()

    plt.colorbar(c2, cax=cax2, label='[C]');
        
    @savefig example_tair_edge_cbar.png
    fig.show()

Colorbars for each panel
########################

One more common use case is a colorbar for each panel.  This can be done by
specifying ``cbar_mode='each'`` as an argument in the call to ``faceted``.

.. ipython:: python
    :okwarning:

    from matplotlib import ticker
    tick_locator = ticker.MaxNLocator(nbins=3)
    
    aspect = 75. / 180.
    fig, axes, caxes = faceted(2, 3, width=8, aspect=aspect, right_pad=0.75,
                               cbar_mode='each',
                               cbar_pad=0.1, internal_pad=(0.75, 0.1),
                               cbar_location='right', cbar_short_side_pad=0.,
                               axes_kwargs={'projection': ccrs.PlateCarree()})
    for i, (ax, cax) in enumerate(zip(axes, caxes)):
        c = ds.Tair.isel(time=i).plot(
            ax=ax, add_colorbar=False, transform=ccrs.PlateCarree(),
            x='xc', y='yc', cmap='viridis')
        ax.set_title('')
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_extent([-180, 0, 15, 90], crs=ccrs.PlateCarree())
        ax.coastlines()
        cb = plt.colorbar(c, cax=cax, label='[C]')
        cb.locator = tick_locator
        cb.update_ticks()
        
    @savefig example_tair_each_cbar2.png
    fig.show()


Parameter defintions
--------------------

A full summary of the meanings of the different arguments to ``faceted`` can be
found here.  

Parameters controlling figure and axes dimensions
#################################################

.. image:: dimensions.png

- W: ``width`` controls the overall width of the figure in inches.
- y / x: ``aspect`` controls the aspect ratio of the panels.
- z: ``cbar_size`` controls the thickness of the colorbar in inches.

Parameters controlling padding
##############################

.. image:: padding.png

- A: ``left_pad`` controls the spacing between the left-most axes and the edge
  of the figure in inches.
- B: ``right_pad`` controls the spacing between the right-most axes and the
  edge of the figure in inches.
- C: ``bottom_pad`` controls the spacing between the bottom-most axes and the
  edge of the figure in inches.
- D: ``top_pad`` controls the spacing between the top-most axes and the edge of
  the figure in inches.
- E: ``cbar_short_side_pad`` controls the spacing between the edges of the
  colorbar and the edges of the axes in inches.
- F: ``internal_pad`` controls the spacing between the non-colorbar axes in
  inches. It can either be a number (and specify the horizontal and vertical
  pad at the same time) or it can be a length-two sequence (and specify both
  the horizontal and vertical pads, respectively).
- G: ``cbar_pad`` controls the spacing (in inches) between the edge of the
  non-colorbar axes and the colorbar axes.
