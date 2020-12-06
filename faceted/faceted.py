from itertools import product

import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.axes_grid1 import AxesGrid


def faceted(
    rows,
    cols,
    width=None,
    height=None,
    aspect=None,
    top_pad=0.25,
    bottom_pad=0.25,
    left_pad=0.25,
    right_pad=0.25,
    internal_pad=0.33,
    cbar_mode=None,
    cbar_short_side_pad=0.0,
    cbar_pad=0.5,
    cbar_size=0.125,
    cbar_location="right",
    sharex="all",
    sharey="all",
    axes_kwargs=None,
):
    """Create figure and tiled axes objects with precise attributes.

    Exactly two of width, height, and aspect must be defined.  The third is
    inferred based on the other two values.

    Parameters
    ----------
    rows : int
        Number of rows of tiles in figure
    cols : int
        Number of columns of tiles in figure
    width : float
        Width of figure
    height : float
        Height of figure
    aspect : float
        Aspect ratio of plots in each tile
    top_pad : float
        Spacing (in inches) between top of figure and axes
    bottom_pad : float
        Spacing (in inches) between bottom of figure and axes
    left_pad : float
        Spacing (in inches) between left of figure and axes
    right_pad : float
        Spacing (in inches) between right of figure and axes
    internal_pad : float or tuple
        Spacing in between panels in both the horizontal and vertical
        directions (in inches); if an individual number, the spacing is the
        same in the horizontal and vertical; if a tuple is specified, the left
        value is the horizontal pad, and the right value is the vertical pad.
    cbar_mode : {None, 'single', 'edge', 'each'}
        Mode for adding colorbar(s) to figure
    cbar_short_side_pad : float
        Spacing between the ends of the colorbar and the edges
        of the axes (in inches); controls the length of the
        colorbar
    cbar_pad : float
        Spacing between plot axes and the colorbar axes (in inches)
    cbar_size : float
        Width of the colorbar in inches
    cbar_location : {'top', 'bottom', 'left', 'right'}
        Side of the plot axes (or figure) for the colorbar
    sharex : bool or {'all', 'col', 'row', 'none'}
        Share x-axis limits, ticks, and tick labels
    sharey : bool or {'all', 'col', 'row', 'none'}
        Share y-axis limits, ticks, and tick labels
    axes_kwargs : dict
        Keyword arguments to pass to Axes constructor

    Returns
    -------
    fig, axes, caxes (if caxes requested)
    """
    if isinstance(internal_pad, (float, int)):
        internal_pad = (internal_pad, internal_pad)
    if len(internal_pad) != 2:
        raise ValueError(
            "Invalid internal pad provided; it must either be a "
            "float or a sequence of two values.  Got "
            "{}".format(internal_pad)
        )
    if cbar_mode not in [None, "single", "edge", "each"]:
        raise ValueError(f"Invalid cbar mode provided.  Got {cbar_mode}.")

    grid_class = _infer_grid_class(width, height, aspect)
    grid = grid_class(
        rows,
        cols,
        width=width,
        height=height,
        aspect=aspect,
        top_pad=top_pad,
        bottom_pad=bottom_pad,
        left_pad=left_pad,
        right_pad=right_pad,
        cbar_mode=cbar_mode,
        cbar_location=cbar_location,
        cbar_pad=cbar_pad,
        cbar_size=cbar_size,
        cbar_short_side_pad=cbar_short_side_pad,
        axes_pad=internal_pad,
        sharex=sharex,
        sharey=sharey,
        axes_kwargs=axes_kwargs,
    )
    if cbar_mode is None:
        return grid.fig, grid.axes
    elif cbar_mode in ["each", "edge", "single"]:
        return grid.fig, grid.axes, grid.caxes


def faceted_ax(cbar_mode=None, **kwargs):
    """A convenience version of faceted for creating single-axis figures.

    Exactly two of width, height, and aspect must be defined.  The third is
    inferred based on the other two values.  

    Parameters
    ----------
    width : float
        Width of figure
    height : float
        Height of figure
    aspect : float
        Aspect ratio of plots in each tile
    top_pad : float
        Spacing (in inches) between top of figure and axes
    bottom_pad : float
        Spacing (in inches) between bottom of figure and axes
    left_pad : float
        Spacing (in inches) between left of figure and axes
    right_pad : float
        Spacing (in inches) between right of figure and axes
    internal_pad : float or tuple
        Spacing in between panels in both the horizontal and vertical
        directions (in inches); if an individual number, the spacing is the
        same in the horizontal and vertical; if a tuple is specified, the left
        value is the horizontal pad, and the right value is the vertical pad.
    cbar_mode : {None, 'single', 'edge', 'each'}
        Mode for adding colorbar(s) to figure
    cbar_short_side_pad : float
        Spacing between the ends of the colorbar and the edges
        of the axes (in inches); controls the length of the
        colorbar
    cbar_pad : float
        Spacing between plot axes and the colorbar axes (in inches)
    cbar_size : float
        Width of the colorbar in inches
    cbar_location : {'top', 'bottom', 'left', 'right'}
        Side of the plot axes (or figure) for the colorbar
    sharex : bool or {'all', 'col', 'row', 'none'}
        Share x-axis limits, ticks, and tick labels
    sharey : bool or {'all', 'col', 'row', 'none'}
        Share y-axis limits, ticks, and tick labels
    axes_kwargs : dict
        Keyword arguments to pass to Axes constructor

    Returns
    -------
    fig, ax, cax (if cax requested)
    """
    if cbar_mode is None:
        fig, (ax,) = faceted(1, 1, **kwargs)
        return fig, ax
    elif cbar_mode == "single":
        fig, (ax,), cax = faceted(1, 1, cbar_mode=cbar_mode, **kwargs)
        return fig, ax, cax
    elif cbar_mode in ("edge", "each"):
        fig, (ax,), (cax,) = faceted(1, 1, cbar_mode=cbar_mode, **kwargs)
        return fig, ax, cax


_LR = ["left", "right"]
_BT = ["bottom", "top"]


def _assert_valid_constraint(width, height, aspect):
    constraints = (width, height, aspect)
    if not (sum(constraint is not None for constraint in constraints) == 2):
        raise ValueError("Exactly two of width, height, and aspect must be floats")


def _infer_grid_class(width, height, aspect):
    _assert_valid_constraint(width, height, aspect)
    if width is not None and aspect is not None:
        return WidthConstrainedAxesGrid
    elif height is not None and aspect is not None:
        return HeightConstrainedAxesGrid
    else:
        return HeightAndWidthConstrainedAxesGrid


class CbarShortSidePadMixin(object):
    """Methods to redraw colorbar Axes created in AxesGrid, allowing for
    customization of their length."""

    def resize_colorbar(self, cax):
        """Add a short-side pad to a given AxesGrid colorbar"""
        locator = cax.get_axes_locator()
        position = locator(cax, None)
        cax.set_visible(False)  # Maybe we should delete it completely?
        new_position = self.cax_position(position)
        return self.fig.add_axes(new_position)

    def resize_colorbars(self):
        """Depending on the cbar_mode resize colorbar(s) to accomodate
        short-side pad option"""
        if self.cbar_mode == "each":
            return [self.resize_colorbar(cax) for cax in self.grid.cbar_axes]
        elif self.cbar_mode == "edge":
            return [
                self.resize_colorbar(cax)
                for cax in self.grid.cbar_axes
                if cax.get_axes_locator() is not None
            ]
        elif self.cbar_mode == "single":
            return self.resize_colorbar(self.grid.cbar_axes[0])
        else:
            return None

    def cax_position(self, position):
        """Compute a new colorbar position from an old one"""
        if self.cbar_location in _BT:
            x0 = position.x0 + self.cbar_short_side_pad / self.width
            y0 = position.y0
            width = position.width - 2.0 * self.cbar_short_side_pad / self.width
            height = position.height
            return [x0, y0, width, height]
        elif self.cbar_location in _LR:
            x0 = position.x0
            y0 = position.y0 + self.cbar_short_side_pad / self.height
            width = position.width
            height = position.height - 2.0 * self.cbar_short_side_pad / self.height
            return [x0, y0, width, height]


class ShareAxesMixin(object):
    """Methods for redrawing axes created by an AxesGrid object

    Enables axes sharing in the style of plt.subplots and for the passing of
    custom keyword arguments to the Axes constructor (e.g. this allows one to
    pass a cartopy projection).
    """

    @property
    def sharex(self):
        """The sharex mode of the object."""
        if isinstance(self._sharex, bool):
            result = "all" if self._sharex else "none"
        else:
            result = self._sharex
        return result

    @property
    def sharey(self):
        """The sharey mode of the object"""
        if isinstance(self._sharey, bool):
            result = "all" if self._sharey else "none"
        else:
            result = self._sharey
        return result

    def redraw_ax(self, ax, sharex=None, sharey=None, axes_kwargs={}):
        """Redraw an Axes object created in AxesGrid with additional sharing
        and keyword arguments."""
        locator = ax.get_axes_locator()
        position = locator(ax, None)
        ax.set_visible(False)
        return self.fig.add_axes(position, sharex=sharex, sharey=sharey, **axes_kwargs)

    def redraw_axes(self):
        """Redraw all Axes objects created in AxesGrid with appropriate shared
        axes depending on the sharing modes."""
        col_ref_axes = [None] * self.cols
        row_ref_axes = [None] * self.rows
        all_ref = None

        axes = []
        rows_cols = product(range(self.rows), range(self.cols))
        for ax, (row, col) in zip(self.grid.axes_all, rows_cols):
            if self.sharex == "all":
                sharex = all_ref
            elif self.sharex == "col":
                sharex = col_ref_axes[col]
            elif self.sharex == "row":
                sharex = row_ref_axes[row]
            else:
                sharex = None

            if self.sharey == "all":
                sharey = all_ref
            elif self.sharey == "col":
                sharey = col_ref_axes[col]
            elif self.sharey == "row":
                sharey = row_ref_axes[row]
            else:
                sharey = None

            new = self.redraw_ax(
                ax, sharex=sharex, sharey=sharey, axes_kwargs=self.axes_kwargs
            )
            axes.append(new)
            all_ref = new
            col_ref_axes[col] = new
            row_ref_axes[row] = new

        return axes

    def make_shared_ticklabels_invisible(self):
        """Make inner Axes tick labels of shared Axes invisible."""
        axes = np.reshape(self.axes, (self.rows, self.cols))
        if self.sharex in ["col", "all"]:
            for ax in axes[:-1, :].flatten():
                ax.xaxis.set_tick_params(
                    which="both", labelbottom=False, labeltop=False
                )

        if self.sharey in ["row", "all"]:
            for ax in axes[:, 1:].flatten():
                ax.yaxis.set_tick_params(
                    which="both", labelbottom=False, labeltop=False
                )


class ConstrainedAxesGrid(CbarShortSidePadMixin, ShareAxesMixin):
    def __init__(
        self,
        rows,
        cols,
        width=None,
        height=None,
        aspect=None,
        top_pad=0.0,
        bottom_pad=0.0,
        left_pad=0.0,
        right_pad=0.0,
        cbar_size=0.125,
        cbar_pad=0.125,
        axes_pad=(0.2, 0.2),
        cbar_mode=None,
        cbar_location="bottom",
        cbar_short_side_pad=0.0,
        sharex=False,
        sharey=False,
        axes_kwargs=None,
    ):
        self.rows = rows
        self.cols = cols
        self._width = width
        self._height = height
        self._aspect = aspect

        self.axes_pad = axes_pad

        self.top_pad = top_pad
        self.bottom_pad = bottom_pad
        self.left_pad = left_pad
        self.right_pad = right_pad

        self.cbar_mode = cbar_mode
        self.cbar_size = cbar_size
        self.cbar_pad = cbar_pad
        self.cbar_location = cbar_location
        self.cbar_short_side_pad = cbar_short_side_pad

        self._sharex = sharex
        self._sharey = sharey

        if axes_kwargs is None:
            self.axes_kwargs = {}
        else:
            self.axes_kwargs = axes_kwargs

        self.construct_axes()

    def construct_axes(self):
        self.fig = plt.figure()
        self.grid = AxesGrid(
            self.fig,
            self.rect,
            nrows_ncols=(self.rows, self.cols),
            cbar_size=self.cbar_size,
            cbar_pad=self.axes_grid_cbar_pad,
            axes_pad=self.axes_pad,
            cbar_mode=self.cbar_mode,
            cbar_location=self.cbar_location,
            aspect=False,
        )
        self.fig.set_size_inches(self.width, self.height)
        self.axes = self.redraw_axes()
        self.make_shared_ticklabels_invisible()
        self.caxes = self.resize_colorbars()

    @property
    def axes_grid_cbar_pad(self):
        """For some reason the colorbar when the colorbar is placed at the
        bottom or left and the colorbar mode is 'single', AxesGrid adds an
        extra axes pad to the colorbar padding; we correct this manually
        here.
        """
        horizontal_pad, vertical_pad = self.axes_pad
        if self.cbar_location == "bottom" and self.cbar_mode == "single":
            return self.cbar_pad - vertical_pad
        elif self.cbar_location == "left" and self.cbar_mode == "single":
            return self.cbar_pad - horizontal_pad
        else:
            return self.cbar_pad

    @property
    def rect(self):
        """Compute the rect defining the area within the outer padding"""
        x0 = self.left_pad / self.width
        y0 = self.bottom_pad / self.height
        width = (self.width - self.left_pad - self.right_pad) / self.width
        height = (self.height - self.top_pad - self.bottom_pad) / self.height
        return [x0, y0, width, height]


class WidthConstrainedAxesGrid(
    ConstrainedAxesGrid, CbarShortSidePadMixin, ShareAxesMixin
):
    """An AxesGrid object with a figure constrained to a precise width
    with panels with a prescribed aspect ratio.
    """

    @property
    def plot_width(self):
        """Width of plot area in each panel (in inches)"""
        hpad, _ = self.axes_pad
        inner_width = self.width - self.left_pad - self.right_pad
        inner_pad = (self.cols - 1) * hpad
        cbar_width = self.cbar_pad + self.cbar_size

        if self.cbar_mode is None or self.cbar_location in _BT:
            return (inner_width - inner_pad) / self.cols
        elif self.cbar_mode == "each" and self.cbar_location in _LR:
            return (inner_width - inner_pad - self.cols * cbar_width) / self.cols
        elif (
            self.cbar_mode == "single" or self.cbar_mode == "edge"
        ) and self.cbar_location in _LR:
            return (inner_width - inner_pad - cbar_width) / self.cols

    @property
    def plot_height(self):
        """Height of plot area in panel (in inches)"""
        return self.plot_width * self.aspect

    @property
    def width(self):
        """Width of the complete figure in inches"""
        return self._width

    @property
    def aspect(self):
        """Aspect ratio of each panel in the figure (height / width)"""
        return self._aspect

    @property
    def height(self):
        """Height of the complete figure in inches"""
        _, vpad = self.axes_pad
        total_plot_height = self.rows * self.plot_height
        total_axes_pad = (self.rows - 1) * vpad
        outer_pad = self.top_pad + self.bottom_pad
        cbar_width = self.cbar_size + self.cbar_pad

        if self.cbar_mode is None or self.cbar_location in _LR:
            return total_plot_height + total_axes_pad + outer_pad
        elif self.cbar_mode == "each" and self.cbar_location in _BT:
            return (
                total_plot_height + total_axes_pad + outer_pad + self.rows * cbar_width
            )
        elif (
            self.cbar_mode == "single" or self.cbar_mode == "edge"
        ) and self.cbar_location in _BT:
            return total_plot_height + total_axes_pad + outer_pad + cbar_width


class HeightConstrainedAxesGrid(
    ConstrainedAxesGrid, CbarShortSidePadMixin, ShareAxesMixin
):
    """An AxesGrid object with a figure constrained to a precise height
    with panels with a prescribed aspect ratio.
    """

    @property
    def plot_height(self):
        """Height of plot area in each panel (in inches)"""
        _, vertical_pad = self.axes_pad
        inner_height = self.height - self.bottom_pad - self.top_pad
        inner_pad = (self.rows - 1) * vertical_pad
        cbar_width = self.cbar_pad + self.cbar_size

        if self.cbar_mode is None or self.cbar_location in _LR:
            return (inner_height - inner_pad) / self.rows
        elif self.cbar_mode == "each" and self.cbar_location in _BT:
            return (inner_height - inner_pad - self.rows * cbar_width) / self.rows
        elif (
            self.cbar_mode == "single" or self.cbar_mode == "edge"
        ) and self.cbar_location in _BT:
            return (inner_height - inner_pad - cbar_width) / self.rows

    @property
    def plot_width(self):
        """Width of plot area in panel (in inches)"""
        return self.plot_height / self.aspect

    @property
    def height(self):
        """Height of the complete figure in inches"""
        return self._height

    @property
    def aspect(self):
        """Aspect ratio of each panel in the figure (height / width)"""
        return self._aspect

    @property
    def width(self):
        """Width of the complete figure in inches"""
        horizontal_pad, _ = self.axes_pad
        total_plot_width = self.cols * self.plot_width
        total_axes_pad = (self.cols - 1) * horizontal_pad
        outer_pad = self.left_pad + self.right_pad
        cbar_width = self.cbar_size + self.cbar_pad

        if self.cbar_mode is None or self.cbar_location in _BT:
            return total_plot_width + total_axes_pad + outer_pad
        elif self.cbar_mode == "each" and self.cbar_location in _LR:
            return (
                total_plot_width + total_axes_pad + outer_pad + self.cols * cbar_width
            )
        elif (
            self.cbar_mode == "single" or self.cbar_mode == "edge"
        ) and self.cbar_location in _LR:
            return total_plot_width + total_axes_pad + outer_pad + cbar_width


class HeightAndWidthConstrainedAxesGrid(
    ConstrainedAxesGrid, CbarShortSidePadMixin, ShareAxesMixin
):
    """An AxesGrid object with a figure constrained to a precise height and width
    with panels with a flexible aspect ratio.
    """

    @property
    def plot_width(self):
        """Width of plot area in each panel (in inches)"""
        hpad, _ = self.axes_pad
        inner_width = self.width - self.left_pad - self.right_pad
        inner_pad = (self.cols - 1) * hpad
        cbar_width = self.cbar_pad + self.cbar_size

        if self.cbar_mode is None or self.cbar_location in _BT:
            return (inner_width - inner_pad) / self.cols
        elif self.cbar_mode == "each" and self.cbar_location in _LR:
            return (inner_width - inner_pad - self.cols * cbar_width) / self.cols
        elif (
            self.cbar_mode == "single" or self.cbar_mode == "edge"
        ) and self.cbar_location in _LR:
            return (inner_width - inner_pad - cbar_width) / self.cols

    @property
    def plot_height(self):
        """Height of plot area in each panel (in inches)"""
        _, vertical_pad = self.axes_pad
        inner_height = self.height - self.bottom_pad - self.top_pad
        inner_pad = (self.rows - 1) * vertical_pad
        cbar_width = self.cbar_pad + self.cbar_size

        if self.cbar_mode is None or self.cbar_location in _LR:
            return (inner_height - inner_pad) / self.rows
        elif self.cbar_mode == "each" and self.cbar_location in _BT:
            return (inner_height - inner_pad - self.rows * cbar_width) / self.rows
        elif (
            self.cbar_mode == "single" or self.cbar_mode == "edge"
        ) and self.cbar_location in _BT:
            return (inner_height - inner_pad - cbar_width) / self.rows

    @property
    def height(self):
        """Height of the complete figure in inches"""
        return self._height

    @property
    def width(self):
        """Width of the complete figure in inches"""
        return self._width

    @property
    def aspect(self):
        """Aspect ratio of each panel in the figure (height / width)"""
        return self.plot_height / self.plot_width
