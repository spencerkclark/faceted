import matplotlib.pyplot as plt

from mpl_toolkits.axes_grid1 import AxesGrid


def facets(rows, cols, width=8., aspect=0.618, top_pad=0.25,
           bottom_pad=0.25, left_pad=0.25, right_pad=0.25, internal_pad=0.33,
           cbar_mode=None, cbar_short_side_pad=0.5, cbar_pad=0.5,
           cbar_size=0.125, cbar_location='right', axes_kwargs={}):
    """Create figure and tiled axes objects with precise attributes

    Parameters
    ----------
    rows : int
        Number of rows of tiles in figure
    cols : int
        Number of columns of tiles in figure
    width : float
        Width of figure
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
    internal_pad : float
        Spacing in between tiles (in inches)
    cbar_mode : {None, 'figure', 'tile'}
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
    axes_kwargs : dict
        Keyword arguments to pass to ``fig.add_axes()`` when creating
        the plot axes for each tile (e.g. for specifying a Cartopy projection).

    Returns
    -------
    fig, axes, caxes (if caxes requested)
    """
    grid = WidthConstrainedAxesGrid(
        rows, cols, width=width, aspect=aspect, top_pad=top_pad,
        bottom_pad=bottom_pad, left_pad=left_pad, right_pad=right_pad,
        cbar_mode=cbar_mode, cbar_location=cbar_location, cbar_pad=cbar_pad,
        cbar_size=cbar_size, cbar_short_side_pad=cbar_short_side_pad,
        axes_pad=internal_pad
    )
    if cbar_mode is None:
        return grid.fig, grid.axes
    elif cbar_mode in ['each', 'single']:
        return grid.fig, grid.axes, grid.caxes


_LR = ['left', 'right']
_BT = ['bottom', 'top']


class WidthConstrainedAxesGrid(object):
    """An AxesGrid object with a figure constrained to a precise width
    with panels with a prescribed aspect ratio.
    """
    def __init__(self, rows, cols, width, top_pad=0., bottom_pad=0.,
                 left_pad=0., right_pad=0., cbar_size=0.125,
                 cbar_pad=0.125, axes_pad=0.2, cbar_mode=None,
                 cbar_location='bottom', aspect=0.5, cbar_short_side_pad=0.):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.aspect = aspect

        # We'll put off supporting a tuple axes_pad until later
        self.axes_pad = (axes_pad, axes_pad)

        self.top_pad = top_pad
        self.bottom_pad = bottom_pad
        self.left_pad = left_pad
        self.right_pad = right_pad

        self.cbar_mode = cbar_mode
        self.cbar_size = cbar_size
        self.cbar_pad = cbar_pad
        self.cbar_location = cbar_location

        # For some reason when the colorbar is placed at the bottom or left
        # and the colorbar mode is 'single', AxesGrid adds an extra
        # axes pad to the colorbar padding; we correct this manually here.
        if self.cbar_location == 'bottom' and self.cbar_mode == 'single':
            self.cbar_pad = self.cbar_pad - self.axes_pad[1]
        elif self.cbar_location == 'left' and self.cbar_mode == 'single':
            self.cbar_pad = self.cbar_pad - self.axes_pad[0]

        self.cbar_short_side_pad = cbar_short_side_pad

        self.fig = plt.figure()
        self.grid = AxesGrid(
            self.fig, self.rect(), nrows_ncols=(self.rows, self.cols),
            cbar_size=self.cbar_size, cbar_pad=self.cbar_pad,
            axes_pad=self.axes_pad, cbar_mode=self.cbar_mode,
            cbar_location=self.cbar_location, aspect=False
        )
        self.fig.set_size_inches(self.width, self.height)
        self.axes = self.grid.axes_all
        self.caxes = self.resize_colorbars()

    @property
    def plot_width(self):
        """Width of plot area in each panel (in inches)"""
        hpad, _ = self.axes_pad
        inner_width = self.width - self.left_pad - self.right_pad
        inner_pad = (self.cols - 1) * hpad
        cbar_width = self.cbar_pad + self.cbar_size

        if self.cbar_mode is None or self.cbar_location in _BT:
            return (inner_width - inner_pad) / self.cols
        elif self.cbar_mode == 'each' and self.cbar_location in _LR:
            return (inner_width - inner_pad
                    - self.cols * cbar_width) / self.cols
        elif self.cbar_mode == 'single' and self.cbar_location in _LR:
            return (inner_width - inner_pad - cbar_width) / self.cols
        else:
            raise ValueError('Invalid cbar_mode or cbar_location provided')

    @property
    def plot_height(self):
        return self.plot_width * self.aspect

    @property
    def height(self):
        _, vpad = self.axes_pad
        total_plot_height = self.rows * self.plot_height
        total_axes_pad = (self.rows - 1) * vpad
        outer_pad = self.top_pad + self.bottom_pad
        cbar_width = self.cbar_size + self.cbar_pad

        if self.cbar_mode is None or self.cbar_location in _LR:
            return total_plot_height + total_axes_pad + outer_pad
        elif self.cbar_mode == 'each' and self.cbar_location in _BT:
            return (total_plot_height + total_axes_pad + outer_pad + self.rows
                    * cbar_width)
        elif self.cbar_mode == 'single' and self.cbar_location in _BT:
            return (total_plot_height + total_axes_pad + outer_pad +
                    cbar_width)

    def rect(self):
        """Compute the rect defining the area within the outer padding"""
        x0 = self.left_pad / self.width
        y0 = self.bottom_pad / self.height
        width = (self.width - self.left_pad - self.right_pad) / self.width
        height = (self.height - self.top_pad - self.bottom_pad) / self.height
        return [x0, y0, width, height]

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
        if self.cbar_mode == 'each':
            return [self.resize_colorbar(cax) for cax in self.grid.cbar_axes]
        elif self.cbar_mode == 'single':
            return self.resize_colorbar(self.grid.cbar_axes[0])
        else:
            return None

    def cax_position(self, position):
        """Compute a new colorbar position from an old one"""
        if self.cbar_location in _BT:
            x0 = position.x0 + self.cbar_short_side_pad / self.width
            y0 = position.y0
            width = position.width - 2. * self.cbar_short_side_pad / self.width
            height = position.height
            return [x0, y0, width, height]
        elif self.cbar_location in _LR:
            x0 = position.x0
            y0 = position.y0 + self.cbar_short_side_pad / self.height
            width = position.width
            height = (position.height -
                      2. * self.cbar_short_side_pad / self.height)
            return [x0, y0, width, height]
