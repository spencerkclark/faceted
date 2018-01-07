"""Test suite for facets module"""
from collections import OrderedDict
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pytest

from facets import facets, WidthConstrainedAxesGrid


plt.switch_backend('agg')


_TOP_PAD = _BOTTOM_PAD = _LEFT_PAD = _RIGHT_PAD = 0.25
_INTERNAL_PAD = 0.25
_ASPECT = 0.5
_WIDTH_CONSTRAINT = 8.
_SHORT_SIDE_PAD = 0.25
_LONG_SIDE_PAD = 0.25
_CBAR_THICKNESS = 0.125


def test_facets_cbar_mode_none():
    fig, axes = facets(1, 2)
    assert len(axes) == 2
    plt.close(fig)


def test_facets_cbar_mode_single():
    fig, axes, cax = facets(1, 2, cbar_mode='single')
    assert len(axes) == 2
    plt.close(fig)


def test_facets_cbar_mode_each():
    fig, axes, caxes = facets(1, 2, cbar_mode='each')
    assert len(axes) == 2
    assert len(axes) == len(caxes)
    plt.close(fig)


def test_facets_cbar_mode_invalid():
    with pytest.raises(ValueError):
        facets(1, 2, cbar_mode='invalid')


_LAYOUTS = [(1, 1), (1, 2), (2, 1), (2, 2), (5, 3)]
_CBAR_MODES = [None, 'single', 'each']
_CBAR_LOCATIONS = ['bottom', 'right', 'top', 'left']
_CG_LAYOUTS = product(_CBAR_MODES, _CBAR_LOCATIONS, _LAYOUTS)


def format_layout(layout):
    cbar_mode, cbar_loc, (rows, cols) = layout
    return 'cbar_mode={!r}, cbar_location={!r}, rows={}, cols={}'.format(
        cbar_mode, cbar_loc, rows, cols)


_CG_IDS = OrderedDict([(layout, format_layout(layout))
                       for layout in _CG_LAYOUTS])


@pytest.fixture(params=_CG_IDS.keys(), ids=_CG_IDS.values())
def grid(request):
    mode, location, (rows, cols) = request.param
    obj = WidthConstrainedAxesGrid(
        rows, cols, width=_WIDTH_CONSTRAINT, aspect=_ASPECT,
        top_pad=_TOP_PAD, bottom_pad=_BOTTOM_PAD,
        left_pad=_LEFT_PAD, right_pad=_RIGHT_PAD,
        cbar_mode=mode, cbar_pad=_LONG_SIDE_PAD,
        axes_pad=_INTERNAL_PAD, cbar_location=location,
        cbar_size=_CBAR_THICKNESS,
        cbar_short_side_pad=_SHORT_SIDE_PAD)
    yield obj
    plt.close(obj.fig)


def get_tile_width(grid, left_pad=_LEFT_PAD, right_pad=_RIGHT_PAD):
    return (grid.width - left_pad - right_pad
            - (grid.cols - 1) * _INTERNAL_PAD) / grid.cols


def get_tile_height(grid, bottom_pad=_BOTTOM_PAD, top_pad=_TOP_PAD):
    return (grid.height - bottom_pad - top_pad -
            (grid.rows - 1) * _INTERNAL_PAD) / grid.rows


def test_width_constrained_axes_positions(grid):
    if grid.cbar_mode == 'each':
        check_width_constrained_axes_positions_each(grid)
    elif grid.cbar_mode == 'single':
        check_width_constrained_axes_positions_single(grid)
    elif grid.cbar_mode is None:
        check_width_constrained_axes_positions_none(grid)


def test_width_constrained_caxes_positions(grid):
    if grid.cbar_mode == 'each':
        check_width_constrained_caxes_positions_each(grid)
    elif grid.cbar_mode == 'single':
        check_width_constrained_caxes_positions_single(grid)
    elif grid.cbar_mode is None:
        pytest.skip('Skipping colorbar positions test, because cbar_mode=None')


def check_width_constrained_axes_positions_none(grid):
    rows, cols = grid.rows, grid.cols
    width, height = grid.width, grid.height
    tile_width, tile_height = get_tile_width(grid), get_tile_height(grid)
    fig = grid.fig

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    for ax, (row, col) in zip(grid.axes, indexes):
        ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
        x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width)) / width
        y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height)) / height
        dx = tile_width / width
        dy = tile_height / height
        expected_bounds = [x0, y0, dx, dy]
        np.testing.assert_allclose(ax_bounds, expected_bounds)


def check_width_constrained_axes_positions_single(grid):
    rows, cols = grid.rows, grid.cols
    width, height = grid.width, grid.height
    cbar_location = grid.cbar_location
    fig = grid.fig

    left_pad, right_pad = _LEFT_PAD, _RIGHT_PAD
    bottom_pad, top_pad = _BOTTOM_PAD, _TOP_PAD
    if cbar_location == 'left':
        left_pad = _LEFT_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD
    elif cbar_location == 'right':
        right_pad = _RIGHT_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD
    elif cbar_location == 'bottom':
        bottom_pad = _BOTTOM_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD
    elif cbar_location == 'top':
        top_pad = _TOP_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD

    tile_width = get_tile_width(grid, left_pad=left_pad, right_pad=right_pad)
    tile_height = get_tile_height(grid, bottom_pad=bottom_pad, top_pad=top_pad)

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    axes = grid.axes
    for ax, (row, col) in zip(axes, indexes):
        ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
        x0 = (left_pad + col * (_INTERNAL_PAD + tile_width)) / width
        y0 = (bottom_pad + row * (_INTERNAL_PAD + tile_height)) / height
        dx = tile_width / width
        dy = tile_height / height
        expected_bounds = [x0, y0, dx, dy]
        np.testing.assert_allclose(ax_bounds, expected_bounds)


def check_width_constrained_caxes_positions_single(grid):
    width, height = grid.width, grid.height
    cbar_location = grid.cbar_location
    fig = grid.fig

    cax = grid.caxes
    cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
    if cbar_location == 'bottom':
        x0 = (_LEFT_PAD + _SHORT_SIDE_PAD) / width
        y0 = _BOTTOM_PAD / height
        dx = (width - _LEFT_PAD - _RIGHT_PAD - 2. * _SHORT_SIDE_PAD) / width
        dy = _CBAR_THICKNESS / height
    elif cbar_location == 'right':
        x0 = (width - _CBAR_THICKNESS - _RIGHT_PAD) / width
        y0 = (_BOTTOM_PAD + _SHORT_SIDE_PAD) / height
        dx = _CBAR_THICKNESS / width
        dy = (height - _TOP_PAD - _BOTTOM_PAD - 2. * _SHORT_SIDE_PAD) / height
    elif cbar_location == 'top':
        x0 = (_LEFT_PAD + _SHORT_SIDE_PAD) / width
        y0 = (height - _CBAR_THICKNESS - _TOP_PAD) / height
        dx = (width - _LEFT_PAD - _RIGHT_PAD - 2. * _SHORT_SIDE_PAD) / width
        dy = _CBAR_THICKNESS / height
    elif cbar_location == 'left':
        x0 = _LEFT_PAD / width
        y0 = (_BOTTOM_PAD + _SHORT_SIDE_PAD) / height
        dx = _CBAR_THICKNESS / width
        dy = (height - _TOP_PAD - _BOTTOM_PAD - 2. * _SHORT_SIDE_PAD) / height
    expected_bounds = [x0, y0, dx, dy]
    np.testing.assert_allclose(cax_bounds, expected_bounds)


def check_width_constrained_axes_positions_each(grid):
    rows, cols = grid.rows, grid.cols
    width, height = grid.width, grid.height
    tile_width, tile_height = get_tile_width(grid), get_tile_height(grid)
    cbar_location = grid.cbar_location
    fig = grid.fig

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    axes = grid.axes
    if cbar_location == 'bottom':
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (tile_width + _INTERNAL_PAD)) / width
            y0 = (_BOTTOM_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD +
                  row * (tile_height + _INTERNAL_PAD)) / height
            dx = tile_width / width
            dy = (tile_height - _CBAR_THICKNESS - _LONG_SIDE_PAD) / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(ax_bounds, expected_bounds)
    elif cbar_location == 'top':
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width)) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height)) / height
            dx = tile_width / width
            dy = (tile_height - _CBAR_THICKNESS - _LONG_SIDE_PAD) / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(ax_bounds, expected_bounds)
    elif cbar_location == 'right':
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width)) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height)) / height
            dx = (tile_width - _CBAR_THICKNESS - _LONG_SIDE_PAD) / width
            dy = tile_height / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(ax_bounds, expected_bounds)
    elif cbar_location == 'left':
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD +
                  col * (_INTERNAL_PAD + tile_width)) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height)) / height
            dx = (tile_width - _CBAR_THICKNESS - _LONG_SIDE_PAD) / width
            dy = tile_height / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(ax_bounds, expected_bounds)


def check_width_constrained_caxes_positions_each(grid):
    rows, cols = grid.rows, grid.cols
    width, height = grid.width, grid.height
    tile_width, tile_height = get_tile_width(grid), get_tile_height(grid)
    cbar_location = grid.cbar_location
    fig = grid.fig

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    caxes = grid.caxes
    if cbar_location == 'bottom':
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width) +
                  _SHORT_SIDE_PAD) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height)) / height
            dx = (tile_width - 2. * _SHORT_SIDE_PAD) / width
            dy = _CBAR_THICKNESS / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == 'top':
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width) +
                  _SHORT_SIDE_PAD) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height) +
                  tile_height - _CBAR_THICKNESS) / height
            dx = (tile_width - 2. * _SHORT_SIDE_PAD) / width
            dy = _CBAR_THICKNESS / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == 'right':
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width) + tile_width -
                  _CBAR_THICKNESS) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height) +
                  _SHORT_SIDE_PAD) / height
            dx = _CBAR_THICKNESS / width
            dy = (tile_height - 2. * _SHORT_SIDE_PAD) / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == 'left':
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_INTERNAL_PAD + tile_width)) / width
            y0 = (_BOTTOM_PAD + row * (_INTERNAL_PAD + tile_height) +
                  _SHORT_SIDE_PAD) / height
            dx = _CBAR_THICKNESS / width
            dy = (tile_height - 2. * _SHORT_SIDE_PAD) / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)


def shared_grid(sharex, sharey):
    return WidthConstrainedAxesGrid(
        2, 2, _WIDTH_CONSTRAINT, sharex=sharex, sharey=sharey,
        cbar_mode='single')


def assert_valid_x_sharing(shared_grid, sharex):
    axes = np.reshape(shared_grid.axes, (shared_grid.rows, shared_grid.cols))
    if sharex == 'all':
        ax_ref = axes.flatten()[0]
        for ax in axes.flatten():
            assert ax.xaxis.major == ax_ref.xaxis.major
            assert ax.xaxis.minor == ax_ref.xaxis.minor
    elif sharex == 'row':
        for row in axes:
            ax_ref = row[0]
            for ax in row:
                assert ax.xaxis.major == ax_ref.xaxis.major
                assert ax.xaxis.minor == ax_ref.xaxis.minor
        for col in axes.T:
            ax_ref = col[0]
            for ax in col[1:]:
                assert ax.xaxis.major != ax_ref.xaxis.major
                assert ax.xaxis.minor != ax_ref.xaxis.minor
    elif sharex == 'col':
        for col in axes.T:
            ax_ref = col[0]
            for ax in col:
                assert ax.xaxis.major == ax_ref.xaxis.major
                assert ax.xaxis.minor == ax_ref.xaxis.minor
        for row in axes:
            ax_ref = row[0]
            for ax in row[1:]:
                assert ax.xaxis.major != ax_ref.xaxis.major
                assert ax.xaxis.minor != ax_ref.xaxis.minor
    elif sharex == 'none':
        ax_ref = axes.flatten()[0]
        for ax in axes.flatten()[1:]:
            assert ax.xaxis.major != ax_ref.xaxis.major
            assert ax.xaxis.minor != ax_ref.xaxis.minor        


def assert_valid_y_sharing(shared_grid, sharey):
    axes = np.reshape(shared_grid.axes, (shared_grid.rows, shared_grid.cols))
    if sharey == 'all':
        ax_ref = axes.flatten()[0]
        for ax in axes.flatten():
            assert ax.yaxis.major == ax_ref.yaxis.major
            assert ax.yaxis.minor == ax_ref.yaxis.minor
    elif sharey == 'row':
        for row in axes:
            ax_ref = row[0]
            for ax in row:
                assert ax.yaxis.major == ax_ref.yaxis.major
                assert ax.yaxis.minor == ax_ref.yaxis.minor
        for col in axes.T:
            ax_ref = col[0]
            for ax in col[1:]:
                assert ax.yaxis.major != ax_ref.yaxis.major
                assert ax.yaxis.minor != ax_ref.yaxis.minor
    elif sharey == 'col':
        for col in axes.T:
            ax_ref = col[0]
            for ax in col:
                assert ax.yaxis.major == ax_ref.yaxis.major
                assert ax.yaxis.minor == ax_ref.yaxis.minor
        for row in axes:
            ax_ref = row[0]
            for ax in row[1:]:
                assert ax.yaxis.major != ax_ref.yaxis.major
                assert ax.yaxis.minor != ax_ref.yaxis.minor
    elif sharey == 'none':
        ax_ref = axes.flatten()[0]
        for ax in axes.flatten()[1:]:
            assert ax.yaxis.major != ax_ref.yaxis.major
            assert ax.yaxis.minor != ax_ref.yaxis.minor


_SHARE_OPTIONS = ['all', 'row', 'col', 'none']


@pytest.mark.parametrize(
    ('sharex', 'sharey'), product(_SHARE_OPTIONS, _SHARE_OPTIONS))
def test_share_axes_mixin(sharex, sharey):
    grid = shared_grid(sharex, sharey)
    assert_valid_x_sharing(grid, sharex)
    assert_valid_y_sharing(grid, sharey)
