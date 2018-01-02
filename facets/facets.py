from itertools import product

import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.axes_grid1 import AxesGrid


def facets(rows, cols, width=8., aspect=0.618, top_pad=0.25,
           bottom_pad=0.25, left_pad=0.25, right_pad=0.25, internal_pad=0.33,
           cbar_mode=None, cbar_short_side_pad=0.5, cbar_long_side_pad=0.5,
           cbar_thickness=0.125, cbar_location='right', axes_kwargs={}):
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
    cbar_long_side_pad : float
        Spacing between plot axes and the colorbar axes (in inches)
    cbar_thickness : float
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
    if cbar_mode is None:
        bg = BasicGrid(
            rows, cols, width_constraint=width, aspect=aspect,
            top_pad=top_pad, bottom_pad=bottom_pad,
            left_pad=left_pad, right_pad=right_pad, internal_pad=internal_pad)
        return bg.fig, bg.axes(**axes_kwargs)
    elif cbar_mode == 'figure':
        cg = ColorbarGrid(
            rows, cols, width_constraint=width, aspect=aspect,
            top_pad=top_pad, bottom_pad=bottom_pad, left_pad=left_pad,
            right_pad=right_pad, internal_pad=internal_pad,
            short_side_pad=cbar_short_side_pad,
            long_side_pad=cbar_long_side_pad, cbar_thickness=cbar_thickness,
            cbar_location=cbar_location)
        axes, cax = cg.axes(**axes_kwargs)
        return cg.fig, axes, cax
    elif cbar_mode == 'tile':
        mcg = MultiColorbarGrid(
            rows, cols, width_constraint=width, aspect=aspect,
            top_pad=top_pad, bottom_pad=bottom_pad, left_pad=left_pad,
            right_pad=right_pad, internal_pad=internal_pad,
            short_side_pad=cbar_short_side_pad,
            long_side_pad=cbar_long_side_pad, cbar_thickness=cbar_thickness,
            cbar_location=cbar_location)
        axes, cax = mcg.axes(**axes_kwargs)
        return mcg.fig, axes, cax
    else:
        raise ValueError('Invalid cbar_mode specified')


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

        # For some reason when the colorbar is placed at the bottom and
        # the colorbar mode is 'single', AxesGrid adds an extra vertical
        # axes pad to the colorbar padding; we correct this manually here.
        if self.cbar_location == 'bottom' and self.cbar_mode == 'single':
            self.cbar_pad = self.cbar_pad - self.axes_pad[1]

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
        else:
            raise ValueError('Invalid cbar_mode or cbar_location provided')

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
        else:
            raise ValueError('Invalid cbar_location')


class Tile(object):
    def __init__(self, x0, y0, width, height, axes_bounds):
        """Create a Tile object

        A Tile object is an element to be tiled in a larger
        Figure.

        Parameters
        ----------
        x0 : float
            Lower left corner x coordinate in root Figure
        y0 : float
            Lower left corner y coordinate in root Figure
        width : float
            Width in figure coordinates of root Figure
        height : float
            Height in figure coordinates of root Figure
        axes_bounds : list
            List of axes_bounds of the axes in a single
            Tile (i.e. in sub-figure space)
        """
        self.x0 = x0
        self.y0 = y0
        self.width = width
        self.height = height
        self.axes_bounds = axes_bounds

    def transform(self, bounds):
        """Transform the bounds of an axis in sub-figure space
        to root Figure space.

        Parameters
        ----------
        bounds : list
            x0, y0, width, height

        Returns
        -------
        list
        """
        _x0, _y0, _width, _height = bounds
        coords = [self.x0 + _x0 * self.width,
                  self.y0 + _y0 *
                  self.height,
                  _width * self.width,
                  _height *
                  self.height]
        return coords

    def transformed_axes_bounds(self):
        """Transform axes bounds to root Figure space."""
        return [self.transform(bounds) for bounds in self.axes_bounds]


class BaseGrid(object):
    def __init__(self, rows, cols, internal_pad=0.33, top_pad=0.25,
                 bottom_pad=0.25, left_pad=0.25, right_pad=0.25):
        """Create a new BaseGrid object

        Padding on the outside of the grid is required for axes
        ticks, ticklabels, and labels to be included in the output
        of saving a figure.

        Parameters
        ----------
        rows : int
            Number of rows of Tile objects
        cols : int
            Number of columns of Tile objects
        internal_pad : float
            Padding between Tile objects (in inches)
        top_pad : float
            Padding on top side of grid (in inches)
        bottom_pad : float
            Padding on bottom side of grid (in inches)
        left_pad : float
            Padding on left side of grid (in inches)
        right_pad : float
            Padding on right side of grid (in inches)
        """
        self.rows = rows
        self.cols = cols

        self.internal_pad = internal_pad
        self.top_pad = top_pad
        self.bottom_pad = bottom_pad
        self.left_pad = left_pad
        self.right_pad = right_pad
        self.set_padding()
        self.tiles = self._generate_grid()
        self.fig = self.figure()

    @property
    def height(self):
        """The height (in inches) of the entire grid (including padding)"""
        tiles = self.rows * self.tile_height
        inner_padding = (self.rows - 1) * self.internal_pad
        outer_padding = self.top_pad + self.bottom_pad
        return tiles + inner_padding + outer_padding

    @property
    def width(self):
        """The width (in inches) of the entire grid (including padding)"""
        tiles = self.cols * self.tile_width
        inner_padding = (self.cols - 1) * self.internal_pad
        outer_padding = self.left_pad + self.right_pad
        return tiles + inner_padding + outer_padding

    def _tile_x0(self, col):
        """x-coordinate of lower left corner of Tile in figure space

        Parameters
        ----------
        col : int
            Column number in grid

        Returns
        -------
        float
        """
        x = col * (self.tile_width + self.internal_pad) + self.left_pad
        return x / self.width

    def _tile_y0(self, row):
        """y-coordinate of lower left corner of Tile in figure space

        Parameters
        ----------
        row : int
            Row number in grid

        Returns
        -------
        float
        """
        y = row * (self.tile_height + self.internal_pad) + self.bottom_pad
        return y / self.height

    def _generate_grid(self):
        """Generate a grid of Tile objects with the proper bounds

        Make sure ordering of tiles is in plt.subplots order.  This
        requires being mindful about the order in which itertools.product
        iterates over things and using np.flipud at the end.
        """
        x0_s = [self._tile_x0(col) for col in range(self.cols)]
        y0_s = [self._tile_y0(row) for row in range(self.rows)]
        width = self.tile_width / self.width
        height = self.tile_height / self.height
        tiles = [Tile(x0, y0, width, height,
                      self.axes_bounds) for y0, x0 in product(y0_s, x0_s)]
        return np.flipud(np.array(tiles).reshape(self.rows, self.cols))

    def figure(self):
        """Create a Figure object of the proper dimensions for the grid"""
        fig = plt.figure()
        fig.set_size_inches(self.width, self.height)
        return fig

    def set_padding(self):
        """Optional method for logic to automatically add additional padding

        This is used in sub-classes which add colorbars to the outside of the 
        grid for instance.
        """
        pass

    @property
    def axes_bounds(self):
        """Coordinates in local figure space of axes elements in a Tile

        This is used in sub-classes to add colorbars to each Tile.  By 
        default we draw one set of Axes to cover the entire Tile, but
        in practice any number of Axes can be drawn in a Tile.
        """
        return [[0., 0., 1., 1.]]


class BasicGrid(BaseGrid):
    def __init__(self, rows, cols, width_constraint=8.0,
                 aspect=0.618, **kwargs):
        """Create a new BasicGrid object

        A BasicGrid object is used to create a width-constrained
        plot with no colorbar(s).

        Padding on the outside of the grid is required for axes
        ticks, ticklabels, and labels to be included in the output
        of saving a figure.

        Parameters
        ----------
        rows : int
            Number of rows of Tile objects
        cols : int
            Number of columns of Tile objects
        width_constraint : float
            Width of full grid (in inches)
        aspect : float
            Aspect ratio of plots in tiles (height / width)
        internal_pad : float
            Padding between Tile objects (in inches)
        top_pad : float
            Padding on top side of grid (in inches)
        bottom_pad : float
            Padding on bottom side of grid (in inches)
        left_pad : float
            Padding on left side of grid (in inches)
        right_pad : float
            Padding on right side of grid (in inches)
        """
        self.width_constraint = width_constraint
        self.aspect = aspect
        super(BasicGrid, self).__init__(rows, cols, **kwargs)

    @property
    def tile_width(self):
        """The width of a Tile in the grid object"""
        return (self.width_constraint -
                (self.internal_pad * (self.cols - 1) +
                 self.left_pad + self.right_pad)) / self.cols

    @property
    def tile_height(self):
        """The height of a Tile in the grid object"""
        return self.tile_width * self.aspect

    def axes(self, **add_axes_kwargs):
        """Creates the axes associated with all tiles in the grid

        Parameters
        ----------
        **add_axes_kwargs
            Any keyword arguments that can be passed to ``fig.add_axes``
            (e.g. if one wanted to pass a Cartopy projection)

        Returns
        -------
        list of Axes objects
        """
        return [self.fig.add_axes(
            tile.transformed_axes_bounds()[0],
            **add_axes_kwargs) for tile in self.tiles.flatten()]


class ColorbarGrid(BaseGrid):
    def __init__(self, rows, cols, width_constraint=8.0, aspect=0.618,
                 cbar_location='bottom', cbar_thickness=0.125,
                 short_side_pad=0.5, long_side_pad=0.5,
                 internal_pad=0.33, top_pad=0.,
                 bottom_pad=0., left_pad=0., right_pad=0.):
        """Create a new ColorbarGrid object

        A ColorbarGrid object is used to create a width-constrained
        plot with a single colorbar.

        Padding on the outside of the grid is required for axes
        ticks, ticklabels, and labels to be included in the output
        of saving a figure.  Padding for the colorbar is added 
        automatically.

        Parameters
        ----------
        rows : int
            Number of rows of Tile objects
        cols : int
            Number of columns of Tile objects
        width_constraint : float
            Width of full grid (in inches)
        aspect : float
            Aspect ratio of plots in tiles (height / width)
        internal_pad : float
            Padding between Tile objects (in inches)
        top_pad : float
            Padding on top side of grid (in inches)
        bottom_pad : float
            Padding on bottom side of grid (in inches)
        left_pad : float
            Padding on left side of grid (in inches)
        right_pad : float
            Padding on right side of grid (in inches)
        cbar_location : {'bottom', 'top', 'left', 'right'}
            Location of common colorbar
        short_side_pad : float
            Padding on the short side of the colorbar (in inches)
        long_side_pad : float
            Padding on the long side of the colorbar (in inches)
        cbar_thickness : float
            Thickness of the colorbar (in inches)
        """
        self.width_constraint = width_constraint
        self.aspect = aspect
        self.cbar_location = cbar_location
        self.cbar_thickness = cbar_thickness
        self.short_side_pad = short_side_pad
        self.long_side_pad = long_side_pad
        super(ColorbarGrid, self).__init__(rows, cols, internal_pad,
                                           top_pad, bottom_pad, left_pad,
                                           right_pad)

    def set_padding(self):
        """Reset padding to make room for a common colorbar"""
        if self.cbar_location == 'bottom':
            self.bottom_pad = (self.bottom_pad + self.cbar_thickness +
                               self.long_side_pad)
        elif self.cbar_location == 'left':
            self.left_pad = (self.left_pad + self.cbar_thickness +
                             self.long_side_pad)
        elif self.cbar_location == 'right':
            self.right_pad = (self.right_pad + self.cbar_thickness +
                              self.long_side_pad)
        elif self.cbar_location == 'top':
            self.top_pad = (self.top_pad + self.cbar_thickness +
                            self.long_side_pad)
        else:
            raise ValueError('Invalid cbar_location provided')

    def add_colorbar(self):
        width = self.width
        height = self.height
        if self.cbar_location in ['top', 'bottom']:
            cbar_width = (width - 2. * self.short_side_pad - self.left_pad -
                          self.right_pad) / width
            cbar_height = self.cbar_thickness / height
            cbar_x0 = (self.left_pad + self.short_side_pad) / width
        elif self.cbar_location in ['left', 'right']:
            cbar_height = (height - 2. * self.short_side_pad - self.top_pad -
                           self.bottom_pad) / height
            cbar_width = self.cbar_thickness / width
            cbar_y0 = (self.bottom_pad + self.short_side_pad) / height

        if self.cbar_location == 'bottom':
            cbar_y0 = (self.bottom_pad - self.cbar_thickness -
                       self.long_side_pad) / height
        elif self.cbar_location == 'right':
            cbar_x0 = (width - self.right_pad + self.long_side_pad) / width
        elif self.cbar_location == 'top':
            cbar_y0 = (height - self.top_pad + self.long_side_pad) / height
        elif self.cbar_location == 'left':
            cbar_x0 = (self.left_pad - self.cbar_thickness -
                       self.long_side_pad) / width
        return self.fig.add_axes([cbar_x0, cbar_y0, cbar_width, cbar_height])

    @property
    def tile_width(self):
        """The width of a Tile in the grid object"""
        return (self.width_constraint -
                (self.internal_pad * (self.cols - 1) +
                 self.left_pad + self.right_pad)) / self.cols

    @property
    def tile_height(self):
        """The height of a Tile in the grid object"""
        return self.tile_width * self.aspect

    def axes(self, **add_axes_kwargs):
        """Creates the axes associated with all tiles in the grid

        Parameters
        ----------
        **add_axes_kwargs
            Any keyword arguments that can be passed to ``fig.add_axes``
            (e.g. if one wanted to pass a Cartopy projection).  These
            are not passed to the command to create the colorbar axes.

        Returns
        -------
        list of Axes objects, colorbar axes
        """
        cax = self.add_colorbar()
        axes_ = [self.fig.add_axes(
            tile.transformed_axes_bounds()[0],
            **add_axes_kwargs) for tile in
                 self.tiles.flatten()]
        return axes_, cax


class MultiColorbarGrid(ColorbarGrid):
    def set_padding(self):
        """Override the version in ColorbarGrid; here we don't need
        the method to do anything."""
        pass

    @property
    def tile_width(self):
        """The width of a Tile in the grid object"""
        if self.cbar_location in ['bottom', 'top', 'left', 'right']:
            return (self.width_constraint -
                    (self.internal_pad * (self.cols - 1) +
                     self.left_pad + self.right_pad)) / self.cols
        else:
            raise ValueError('Invalid cbar_location')

    @property
    def tile_height(self):
        """The height of a Tile in the grid object"""
        if self.cbar_location in ['bottom', 'top']:
            return (self.tile_width * self.aspect +
                    self.cbar_thickness + self.long_side_pad)
        elif self.cbar_location in ['left', 'right']:
            return (self.tile_width - self.cbar_thickness -
                    self.long_side_pad) * self.aspect

    @property
    def axes_bounds(self):
        if self.cbar_location in ['bottom', 'top']:
            plot_width = 1.
            plot_height = (self.tile_width *
                           self.aspect) / self.tile_height

            cbar_width = (self.tile_width - 2. *
                          self.short_side_pad) / self.tile_width
            cbar_height = self.cbar_thickness / self.tile_height

            plot_x0 = 0.
            cbar_x0 = self.short_side_pad / self.tile_width
        elif self.cbar_location in ['left', 'right']:
            plot_width = (self.tile_width - self.cbar_thickness -
                          self.long_side_pad) / self.tile_width
            plot_height = 1.

            cbar_width = self.cbar_thickness / self.tile_width
            cbar_height = (self.tile_height -
                           2. * self.short_side_pad) / self.tile_height

            plot_y0 = 0.
            cbar_y0 = self.short_side_pad / self.tile_height

        if self.cbar_location == 'bottom':
            plot_y0 = (self.cbar_thickness +
                       self.long_side_pad) / self.tile_height
            cbar_y0 = 0.
        elif self.cbar_location == 'top':
            plot_y0 = 0.
            cbar_y0 = plot_height + self.long_side_pad / self.tile_height
        elif self.cbar_location == 'left':
            plot_x0 = (self.cbar_thickness +
                       self.long_side_pad) / self.tile_width
            cbar_x0 = 0.
        elif self.cbar_location == 'right':
            plot_x0 = 0.
            cbar_x0 = plot_width + self.long_side_pad / self.tile_width

        return ([plot_x0, plot_y0, plot_width, plot_height],
                [cbar_x0, cbar_y0, cbar_width, cbar_height])

    def axes(self, **add_axes_kwargs):
        """Creates the axes associated with all tiles in the grid

        Parameters
        ----------
        **add_axes_kwargs
            Any keyword arguments that can be passed to ``fig.add_axes``
            (e.g. if one wanted to pass a Cartopy projection).  These
            are not passed to the command to create the colorbar axes.

        Returns
        -------
        list of Axes objects, list colorbar Axes objects
        """
        axes_ = [self.fig.add_axes(tile.transformed_axes_bounds()[0],
                                   **add_axes_kwargs) for tile in
                 self.tiles.flatten()]
        caxes = [self.fig.add_axes(tile.transformed_axes_bounds()[1]) for
                 tile in self.tiles.flatten()]
        return axes_, caxes
