"""Test suite for facets module"""
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pytest

from facets.facets import (Tile, BasicGrid, ColorbarGrid, MultiColorbarGrid,
                           facets)


plt.switch_backend('agg')


@pytest.fixture
def tile():
    return Tile(0., 0., 0.45, 0.45, [[0., 0., 1., 1.]])


@pytest.mark.parametrize(
    ('bounds', 'expected'),
    [([0., 0., 1., 1.], [0., 0., 0.45, 0.45]),
     ([0.3, 0.2, 0.5, 0.5], [0.135, 0.09, 0.225, 0.225])])
def test_tile_transform(tile, bounds, expected):
    result = tile.transform(bounds)
    np.testing.assert_allclose(result, expected)


def test_tile_transformed_axes_bounds(tile):
    result = tile.transformed_axes_bounds()
    expected = [[0., 0., 0.45, 0.45]]
    assert result == expected


_TOP_PAD = _BOTTOM_PAD = _LEFT_PAD = _RIGHT_PAD = 0.25
_INTERNAL_PAD = 0.33
_ASPECT = 0.5
_WIDTH_CONSTRAINT = 8.


def format_layout(layout):
    rows, cols = layout
    return 'rows={}-cols={}'.format(rows, cols)


_LAYOUTS = [(1, 1), (1, 2), (2, 1), (2, 2), (5, 3)]
_IDS = {layout: format_layout(layout) for layout in _LAYOUTS}


@pytest.fixture(params=_IDS.keys(), ids=_IDS.values())
def basic_grid(request):
    rows, cols = request.param
    bg =  BasicGrid(
        rows, cols, width_constraint=_WIDTH_CONSTRAINT,
        aspect=_ASPECT, top_pad=_TOP_PAD, bottom_pad=_BOTTOM_PAD,
        left_pad=_LEFT_PAD, right_pad=_RIGHT_PAD,
        internal_pad=_INTERNAL_PAD)
    yield bg

    # Close figure to prevent too many open figures warning
    plt.close(bg.fig)


def test_basic_grid_tile_width(basic_grid):
    cols = basic_grid.cols
    expected_tile_width = (_WIDTH_CONSTRAINT - _LEFT_PAD - _RIGHT_PAD -
                           (cols - 1) * _INTERNAL_PAD) / cols
    assert expected_tile_width == basic_grid.tile_width


def test_basic_grid_tile_height(basic_grid):
    expected_tile_height = basic_grid.tile_width * _ASPECT
    assert expected_tile_height == basic_grid.tile_height


def test_basic_grid_figure_width(basic_grid):
    expected_figure_width = _WIDTH_CONSTRAINT
    result_width, _ = basic_grid.fig.get_size_inches()
    assert expected_figure_width == result_width
    assert expected_figure_width == basic_grid.width


def test_basic_grid_figure_height(basic_grid):
    rows = basic_grid.rows
    expected_figure_height = (
        rows * basic_grid.tile_height + (rows - 1) * _INTERNAL_PAD +
        _BOTTOM_PAD + _TOP_PAD)
    _, result_height = basic_grid.fig.get_size_inches()
    assert expected_figure_height == result_height
    assert expected_figure_height == basic_grid.height


def test_basic_grid_axes_bounds(basic_grid):
    rows = basic_grid.rows
    cols = basic_grid.cols
    fig = basic_grid.fig
    width = basic_grid.width
    height = basic_grid.height
    tile_width = basic_grid.tile_width
    tile_height = basic_grid.tile_height

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    for ax, (row, col) in zip(basic_grid.axes(), indexes):
        ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
        x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width)) / width
        y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height)) / height
        x = basic_grid.tile_width / width
        y = basic_grid.tile_height / height
        expected_bounds = [x0, y0, x, y]
        np.testing.assert_allclose(ax_bounds, expected_bounds)


_SHORT_SIDE_PAD = 0.25
_LONG_SIDE_PAD = 0.25
_CBAR_THICKNESS = 0.125
_CG_LAYOUTS = product(_LAYOUTS, ['bottom', 'right', 'top', 'left'])


def format_layout_cbar(layout):
    (rows, cols), cbar_loc = layout
    return 'rows={}-cols={}-cbar_location={!r}'.format(rows, cols, cbar_loc)


_CG_IDS = {layout: format_layout_cbar(layout) for layout in _CG_LAYOUTS}


@pytest.fixture(params=_CG_IDS.keys(), ids=_CG_IDS.values())
def colorbar_grid(request):
    (rows, cols), cbar_location = request.param
    cg = ColorbarGrid(
        rows, cols, width_constraint=_WIDTH_CONSTRAINT,
        aspect=_ASPECT, top_pad=_TOP_PAD, bottom_pad=_BOTTOM_PAD,
        left_pad=_LEFT_PAD, right_pad=_RIGHT_PAD,
        internal_pad=_INTERNAL_PAD, long_side_pad=_LONG_SIDE_PAD,
        short_side_pad=_SHORT_SIDE_PAD, cbar_thickness=_CBAR_THICKNESS,
        cbar_location=cbar_location)
    yield cg

    # Close figure to prevent too many open figures warning
    plt.close(cg.fig)


def test_colorbar_grid_left_pad(colorbar_grid):
    if colorbar_grid.cbar_location == 'left':
        expected_left_pad = _LEFT_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD
    else:
        expected_left_pad = _LEFT_PAD
    assert expected_left_pad == colorbar_grid.left_pad


def test_colorbar_grid_right_pad(colorbar_grid):
    if colorbar_grid.cbar_location == 'right':
        expected_right_pad = _RIGHT_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD
    else:
        expected_right_pad = _RIGHT_PAD
    assert expected_right_pad == colorbar_grid.right_pad


def test_colorbar_grid_top_pad(colorbar_grid):
    if colorbar_grid.cbar_location == 'top':
        expected_top_pad = _TOP_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD
    else:
        expected_top_pad = _TOP_PAD
    assert expected_top_pad == colorbar_grid.top_pad


def test_colorbar_grid_bottom_pad(colorbar_grid):
    if colorbar_grid.cbar_location == 'bottom':
        expected_bottom_pad = _BOTTOM_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD
    else:
        expected_bottom_pad = _BOTTOM_PAD
    assert expected_bottom_pad == colorbar_grid.bottom_pad


def test_colorbar_grid_tile_width(colorbar_grid):
    cols = colorbar_grid.cols
    expected_tile_width = (
        _WIDTH_CONSTRAINT - colorbar_grid.left_pad - colorbar_grid.right_pad -
        (cols - 1) * _INTERNAL_PAD) / cols
    assert expected_tile_width == colorbar_grid.tile_width


def test_colorbar_grid_tile_height(colorbar_grid):
    expected_tile_height = colorbar_grid.tile_width * _ASPECT
    assert expected_tile_height == colorbar_grid.tile_height


def test_colorbar_grid_figure_width(colorbar_grid):
    expected_figure_width = _WIDTH_CONSTRAINT
    result_width, _ = colorbar_grid.fig.get_size_inches()
    assert expected_figure_width == result_width
    assert expected_figure_width == colorbar_grid.width


def test_colorbar_grid_figure_height(colorbar_grid):
    rows = colorbar_grid.rows
    expected_figure_height = (
        rows * colorbar_grid.tile_height + (rows - 1) * _INTERNAL_PAD +
        colorbar_grid.bottom_pad + colorbar_grid.top_pad)
    _, result_height = colorbar_grid.fig.get_size_inches()
    assert expected_figure_height == result_height
    assert expected_figure_height == colorbar_grid.height


def test_colorbar_grid_axes_bounds(colorbar_grid):
    rows = colorbar_grid.rows
    cols = colorbar_grid.cols
    fig = colorbar_grid.fig
    width = colorbar_grid.width
    height = colorbar_grid.height
    tile_width = colorbar_grid.tile_width
    tile_height = colorbar_grid.tile_height

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    axes, _ = colorbar_grid.axes()
    for ax, (row, col) in zip(axes, indexes):
        ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
        x0 = (colorbar_grid.left_pad +
              col * (_INTERNAL_PAD + tile_width)) / width
        y0 = (colorbar_grid.bottom_pad +
              row * (_INTERNAL_PAD + tile_height)) / height
        x = tile_width / width
        y = tile_height / height
        expected_bounds = [x0, y0, x, y]
        np.testing.assert_allclose(ax_bounds, expected_bounds)


def test_colorbar_grid_cax_bounds(colorbar_grid):
    fig = colorbar_grid.fig
    width = colorbar_grid.width
    height = colorbar_grid.height
    _, cax = colorbar_grid.axes()
    cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
    if colorbar_grid.cbar_location == 'bottom':
        x0 = (_LEFT_PAD + _SHORT_SIDE_PAD) / width
        y0 = _BOTTOM_PAD / height
        x = (width - _LEFT_PAD - _RIGHT_PAD - 2. * _SHORT_SIDE_PAD) / width
        y = _CBAR_THICKNESS / height
    elif colorbar_grid.cbar_location == 'right':
        x0 = (width - _CBAR_THICKNESS - _RIGHT_PAD) / width
        y0 =  (_BOTTOM_PAD + _SHORT_SIDE_PAD) / height
        x = _CBAR_THICKNESS / width
        y = (height - _TOP_PAD - _BOTTOM_PAD - 2. * _SHORT_SIDE_PAD) / height
    elif colorbar_grid.cbar_location == 'top':
        x0 = (_LEFT_PAD + _SHORT_SIDE_PAD) / width
        y0 = (height - _CBAR_THICKNESS - _TOP_PAD) / height
        x = (width - _LEFT_PAD - _RIGHT_PAD - 2. * _SHORT_SIDE_PAD) / width
        y = _CBAR_THICKNESS / height
    elif colorbar_grid.cbar_location == 'left':
        x0 = _LEFT_PAD / width
        y0 = (_BOTTOM_PAD + _SHORT_SIDE_PAD) / height
        x = _CBAR_THICKNESS / width
        y = (height - _TOP_PAD - _BOTTOM_PAD - 2. * _SHORT_SIDE_PAD) / height
    expected_bounds = [x0, y0, x, y]
    np.testing.assert_allclose(cax_bounds, expected_bounds)


def test_colorbar_grid_invalid_cbar_location():
    with pytest.raises(ValueError):
        ColorbarGrid(1, 1, cbar_location='invalid')


_MCG_LAYOUTS = product(_LAYOUTS, ['bottom', 'top', 'left', 'right'])
_MCG_IDS = {layout: format_layout_cbar(layout) for layout in _MCG_LAYOUTS}


@pytest.fixture(params=_MCG_IDS.keys(), ids=_MCG_IDS.values())
def multicolorbar_grid(request):
    (rows, cols), cbar_location = request.param
    mcg = MultiColorbarGrid(
        rows, cols, width_constraint=_WIDTH_CONSTRAINT,
        aspect=_ASPECT, top_pad=_TOP_PAD, bottom_pad=_BOTTOM_PAD,
        left_pad=_LEFT_PAD, right_pad=_RIGHT_PAD,
        internal_pad=_INTERNAL_PAD, long_side_pad=_LONG_SIDE_PAD,
        short_side_pad=_SHORT_SIDE_PAD, cbar_thickness=_CBAR_THICKNESS,
        cbar_location=cbar_location)
    yield mcg

    # Close figure to prevent too many open figures warning
    plt.close(mcg.fig)


def test_multicolorbar_grid_outer_padding(multicolorbar_grid):
    # Outer padding goes un-modified for a MultiColorbarGrid
    assert _LEFT_PAD == multicolorbar_grid.left_pad
    assert _RIGHT_PAD == multicolorbar_grid.right_pad
    assert _TOP_PAD == multicolorbar_grid.top_pad
    assert _BOTTOM_PAD == multicolorbar_grid.bottom_pad


def test_multicolorbar_tile_width(multicolorbar_grid):
    cols = multicolorbar_grid.cols
    if multicolorbar_grid.cbar_location in ['bottom', 'top', 'left', 'right']:
        expected = (_WIDTH_CONSTRAINT - _LEFT_PAD - _RIGHT_PAD -
                    _INTERNAL_PAD * (cols - 1)) / cols
    assert expected == multicolorbar_grid.tile_width


def test_multicolorbar_tile_height(multicolorbar_grid):
    tile_width = multicolorbar_grid.tile_width
    if multicolorbar_grid.cbar_location in ['bottom', 'top']:
        expected = tile_width * _ASPECT + _CBAR_THICKNESS + _LONG_SIDE_PAD
    elif multicolorbar_grid.cbar_location in ['left', 'right']:
        expected = (tile_width - _CBAR_THICKNESS - _LONG_SIDE_PAD) * _ASPECT
    assert expected == multicolorbar_grid.tile_height


def test_multicolorbar_grid_figure_width(multicolorbar_grid):
    expected_figure_width = _WIDTH_CONSTRAINT
    result_width, _ = multicolorbar_grid.fig.get_size_inches()
    assert expected_figure_width == result_width
    assert expected_figure_width == multicolorbar_grid.width


def test_multicolorbar_grid_figure_height(multicolorbar_grid):
    rows = multicolorbar_grid.rows
    expected_figure_height = (
        rows * multicolorbar_grid.tile_height + (rows - 1) * _INTERNAL_PAD +
        _BOTTOM_PAD + _TOP_PAD)
    _, result_height = multicolorbar_grid.fig.get_size_inches()
    assert expected_figure_height == result_height
    assert expected_figure_height == multicolorbar_grid.height


def test_multicolorbar_grid_axes_bounds(multicolorbar_grid):
    rows = multicolorbar_grid.rows
    cols = multicolorbar_grid.cols
    fig = multicolorbar_grid.fig
    width = multicolorbar_grid.width
    height = multicolorbar_grid.height
    tile_width = multicolorbar_grid.tile_width
    tile_height = multicolorbar_grid.tile_height
    cbar_location = multicolorbar_grid.cbar_location

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    axes, _ = multicolorbar_grid.axes()
    if cbar_location == 'bottom':
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width)) / width
            y0 = (_BOTTOM_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD +
                  row * (_INTERNAL_PAD + tile_height)) / height
            x = tile_width / width
            y = (tile_height - _CBAR_THICKNESS - _LONG_SIDE_PAD) / height
            expected_bounds = [x0, y0, x, y]
            np.testing.assert_allclose(ax_bounds, expected_bounds)
    elif cbar_location == 'top':
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width)) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height)) / height
            x = tile_width / width
            y = (tile_height - _CBAR_THICKNESS - _LONG_SIDE_PAD) / height
            expected_bounds = [x0, y0, x, y]
            np.testing.assert_allclose(ax_bounds, expected_bounds)
    elif cbar_location == 'right':
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width)) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height)) / height
            x = (tile_width - _CBAR_THICKNESS - _LONG_SIDE_PAD) / width
            y = tile_height / height
            expected_bounds = [x0, y0, x, y]
            np.testing.assert_allclose(ax_bounds, expected_bounds)
    elif cbar_location == 'left':
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD +
                  col * (_INTERNAL_PAD + tile_width)) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height)) / height
            x = (tile_width - _CBAR_THICKNESS - _LONG_SIDE_PAD) / width
            y = tile_height / height
            expected_bounds = [x0, y0, x, y]
            np.testing.assert_allclose(ax_bounds, expected_bounds)


def test_multicolorbar_grid_caxes_bounds(multicolorbar_grid):
    rows = multicolorbar_grid.rows
    cols = multicolorbar_grid.cols
    fig = multicolorbar_grid.fig
    width = multicolorbar_grid.width
    height = multicolorbar_grid.height
    tile_width = multicolorbar_grid.tile_width
    tile_height = multicolorbar_grid.tile_height
    cbar_location = multicolorbar_grid.cbar_location

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    _, caxes = multicolorbar_grid.axes()
    if cbar_location == 'bottom':
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width) +
                  _SHORT_SIDE_PAD) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height)) / height
            x = (tile_width - 2. * _SHORT_SIDE_PAD) / width
            y = _CBAR_THICKNESS / height
            expected_bounds = [x0, y0, x, y]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == 'top':
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width) +
                  _SHORT_SIDE_PAD) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height) +
                  tile_height - _CBAR_THICKNESS) / height
            x = (tile_width - 2. * _SHORT_SIDE_PAD) / width
            y = _CBAR_THICKNESS / height
            expected_bounds = [x0, y0, x, y]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == 'right':
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width) + tile_width -
                  _CBAR_THICKNESS) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height) +
                  _SHORT_SIDE_PAD) / height
            x = _CBAR_THICKNESS / width
            y = (tile_height - 2. * _SHORT_SIDE_PAD) / height
            expected_bounds = [x0, y0, x, y]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == 'left':
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width)) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height) +
                  _SHORT_SIDE_PAD) / height
            x = _CBAR_THICKNESS / width
            y = (tile_height - 2. * _SHORT_SIDE_PAD) / height
            expected_bounds = [x0, y0, x, y]
            np.testing.assert_allclose(cax_bounds, expected_bounds)


def test_multicolorbar_grid_invalid_cbar_location():
    with pytest.raises(ValueError):
        MultiColorbarGrid(1, 1, cbar_location='invalid')


def test_facets_cbar_mode_none():
    fig, axes = facets(1, 2)
    assert len(axes) == 2
    plt.close(fig)


def test_facets_cbar_mode_figure():
    fig, axes, cax = facets(1, 2, cbar_mode='figure')
    assert len(axes) == 2
    plt.close(fig)


def test_facets_cbar_mode_tile():
    fig, axes, caxes = facets(1, 2, cbar_mode='tile')
    assert len(axes) == 2
    assert len(axes) == len(caxes)
    plt.close(fig)
