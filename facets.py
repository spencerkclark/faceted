"""Methods for making fine-tuned panel plots

2017-03-02: This is a work in progress, but methods in this module
allow for precise control over colorbar thickness, and padding
(in *physical* (i.e. inches) rather than relative space) in between axes
in panel plots."""
from itertools import product

import matplotlib.pyplot as plt
import mpl_toolkits.axes_grid.axes_size as size
import numpy as np
import xarray as xr

from mpl_toolkits.axes_grid import Divider


def _construct_horiz_grid(columns, pad, cbar_pad, panel_width):
    """Create the horiz list to pass to Divider"""
    if columns > 1:
        horiz = [size.Fixed(cbar_pad)]
        horiz.append(size.Fixed(panel_width - cbar_pad))
        horiz.append(size.Fixed(pad))
        for i in range(1, columns - 1):
            horiz.append(size.Fixed(panel_width))
            horiz.append(size.Fixed(pad))
        horiz.append(size.Fixed(panel_width - cbar_pad))
        horiz.append(size.Fixed(cbar_pad))
        return horiz

    elif columns == 1:
        horiz = [size.Fixed(cbar_pad)]
        horiz.append((size.Fixed(panel_width - 2 * cbar_pad)))
        horiz.append(size.Fixed(cbar_pad))
        return horiz


def _construct_vert_grid(rows, pad, cbar, cbar_thickness, panel_height):
    """Create the vert list to pass to Divider"""
    if not cbar:
        cbar_thickness = 0.0
        cbar_vert_pad = 0.0
    else:
        cbar_vert_pad = pad

    vert = [size.Fixed(cbar_thickness), size.Fixed(cbar_vert_pad)]
    for j in range(rows):
        vert.append(size.Fixed(panel_height))
        if j < rows - 1:
            vert.append(size.Fixed(pad))
    return vert


def _n_center(rows, columns):
    """Number of panels in the region excluding the left and right columns"""
    return rows * (columns - 2)


def _middle_axes(rows, columns, divider, fig, rect, projection):
    """Create the axes for the panels in the region excluding the left and
    right columns."""
    n_center = _n_center(rows, columns)
    middle_axes = [fig.add_axes(rect, label='{}'.format(i),
                                projection=projection)
                   for i in range(n_center)]
    for (nx, ny), ax in zip(product(np.arange(3, 2 * columns - 2, 2),
                                    np.arange(2, 2 * rows + 1, 2)),
                            middle_axes):
        ax.set_axes_locator(divider.new_locator(nx=nx, ny=ny))
        ax.set_label('{}'.format(((ny - 1) // 2) * columns + (nx - 1) // 2))
    return fig, middle_axes


def _left_axes(rows, columns, divider, fig, rect, projection):
    """Create the axes for the panels in the left column."""
    n_center = _n_center(rows, columns)
    left_axes = [fig.add_axes(rect, label='{}'.format(i + n_center),
                             projection=projection) for i in range(rows)]
    for (nx, ny), ax in zip(product([0], np.arange(2, 2 * rows + 1, 2)),
                            left_axes):
        ax.set_axes_locator(divider.new_locator(nx=nx, nx1=nx + 2, ny=ny))
        ax.set_label('{}'.format(((ny - 1) // 2) * columns + (nx) // 2))
    return fig, left_axes


def _right_axes(rows, columns, divider, fig, rect, projection):
    """Create the axes for the panels in the right column."""
    n_center = _n_center(rows, columns)
    right_axes = [fig.add_axes(rect, label='{}'.format(i + n_center + rows),
                               projection=projection) for i in range(rows)]
    for (nx, ny), ax in zip(product([2 * columns - 1],
                                    np.arange(2, 2 * rows + 1, 2)),
                            right_axes):
        ax.set_axes_locator(divider.new_locator(nx=nx, nx1=nx + 2, ny=ny))
        ax.set_label('{}'.format(((ny - 1) // 2) * columns + (nx - 1) // 2))
    return fig, right_axes


def _single_column_axes(rows, divider, fig, rect, projection):
    """Create the axes in the special case that we are making a plot
    with a single column."""
    left_axes = []
    right_axes = []
    middle_axes = [fig.add_axes(rect, label='{}'.format(i),
                                projection=projection) for i in range(rows)]
    for (nx, ny), ax in zip(product([0], np.arange(2, 2 * rows + 1, 2)),
                            middle_axes):
        ax.set_axes_locator(divider.new_locator(nx=nx, nx1=nx + 3, ny=ny))
        ax.set_label('{}'.format(((ny - 1) // 2) + (nx) // 2))
    return fig, left_axes, middle_axes, right_axes


def facets(rows=1, columns=1, pad=0.5, width=8.0, aspect=0.618,
           cbar_pad=0.5, cbar_thickness=0.125, projection=None, cbar=False):
    """Create a paneled plot with precise spacing specifications

    The height of the figure is inferred based on the desired width,
    aspect ratio of the panels, and number of rows.

    Parameters
    ----------
    rows : int
        Number of rows in panel plot
    columns : int
        Number of columns in panel plot
    pad : float
        Distance between panels in inches
    width : float
        Total width of the figure in inches
    aspect : float
        Aspect ratio of an individual panel (panel_height / panel_width)
    cbar_pad : float
        Distance in inches from the absolute edge of the figure that a
        colorbar centered at the bottom of the figure is extended to.
    cbar_thickness : float
        Thickness of the colorbar (in inches)
    projection : cartopy.crs (optional)
        Projection used for all axes in panel plot
    cbar : bool
        True if to draw and return axes for a colorbar, centered at the
        bottom of the figure

    Returns
    -------
    fig : plt.Figure
        Figure instance for plot
    axes : list
        List of axes (in plt.subplots order) of the axes in the panel plot
    cax : plt.Axes
        Axes instance used for plotting the colorbar
    """
    panel_width = (width - (float(columns) - 1.) * pad) / float(columns)
    panel_height = aspect * panel_width
    height = float(rows) * panel_height + (float(rows) - 1.) * pad

    horiz = _construct_horiz_grid(columns, pad, cbar_pad, panel_width)
    vert = _construct_vert_grid(rows, pad, cbar, cbar_thickness, panel_height)

    fig = plt.figure()
    rect = (0.1, 0.1, 0.8, 0.8)  # This will be overriden automatically
    divider = Divider(fig, rect, horiz, vert, aspect=False)

    if columns > 1:
        fig, middle_axes = _middle_axes(
            rows, columns, divider, fig, rect, projection)
        fig, left_axes = _left_axes(
            rows, columns, divider, fig, rect, projection)
        fig, right_axes = _right_axes(
            rows, columns, divider, fig, rect, projection)
    elif columns == 1:
        fig, left_axes, middle_axes, right_axes = _single_column_axes(
            rows, divider, fig, rect, projection)

    if cbar:
        cax = fig.add_axes(rect, label='cbar')
        cax.set_axes_locator(divider.new_locator(nx=1, nx1=columns * 2, ny=0))

    # Return the axes as a flattened list, in the same order that
    # plt.subplots() orders the axes.
    axes = middle_axes + left_axes + right_axes
    axes = sorted(axes, key=lambda ax: int(ax.get_label()), reverse=True)
    axes = np.fliplr(np.array(axes).reshape((rows, columns))).flatten()

    if cbar:
        return fig, axes, cax
    else:
        return fig, axes


def standard_style(context='paper', font_scale=1.):
    """Set my preferred seaborn style parameters.

    Note that CMU Sans Serif is a custom font.  Defaults to
    the matplotlib default (Bitstream Vera Sans) if not installed.
    """
    import seaborn as sns
    sns.set_style('white')
    sns.set_style('ticks', {'font.family': u'CMU Sans Serif',
                            'text.color': '0.0'})
    sns.set_context(context, font_scale=font_scale)
    sns.set_palette('hls', 4)
    return sns



def add_cyclic_to_right(arr, dim, num_points, circumf):
    """Adapted from Spencer Hill's Infinite Diff

    A utility used to add a cyclic point so that there are no gaps
    in contour or pcolormesh figures.
    """
    if not num_points:
        return arr
    arr_out = arr.copy()
    trunc = {dim: slice(0, num_points)}
    edge = arr.isel(**trunc).copy()
    new_edge = edge[dim] + circumf
    new_coord_values = np.concatenate([arr_out[dim].values,
                                       new_edge.values])
    new_arr = xr.concat([arr_out, edge], dim=dim)
    new_arr[dim].values = new_coord_values
    return new_arr
