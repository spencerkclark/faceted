"""Test suite for faceted module"""
from collections import OrderedDict
from itertools import product

import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import pytest

from ..faceted import (
    _DEFAULT_ASPECT,
    _DEFAULT_WIDTH,
    faceted,
    faceted_ax,
    _infer_constraints,
    _infer_grid_class,
    HeightConstrainedAxesGrid,
    HeightAndWidthConstrainedAxesGrid,
    WidthConstrainedAxesGrid,
)


plt.switch_backend("agg")


_TOP_PAD = _BOTTOM_PAD = _LEFT_PAD = _RIGHT_PAD = 0.25
_HORIZONTAL_INTERNAL_PAD = 0.25
_VERTICAL_INTERNAL_PAD = 0.5
_INTERNAL_PAD = (_HORIZONTAL_INTERNAL_PAD, _VERTICAL_INTERNAL_PAD)
_ASPECT_CONSTRAINT = 0.5
_HEIGHT_CONSTRAINT = 7.0
_WIDTH_CONSTRAINT = 8.0
_SHORT_SIDE_PAD = 0.25
_LONG_SIDE_PAD = 0.25
_CBAR_THICKNESS = 0.125


def test_faceted_cbar_mode_none():
    fig, axes = faceted(1, 2, width=_WIDTH_CONSTRAINT, aspect=_ASPECT_CONSTRAINT)
    assert len(axes) == 2
    plt.close(fig)


def test_faceted_cbar_mode_single():
    fig, axes, cax = faceted(
        1, 2, width=_WIDTH_CONSTRAINT, aspect=_ASPECT_CONSTRAINT, cbar_mode="single"
    )
    assert len(axes) == 2
    plt.close(fig)


def test_faceted_cbar_mode_each():
    fig, axes, caxes = faceted(
        1, 2, width=_WIDTH_CONSTRAINT, aspect=_ASPECT_CONSTRAINT, cbar_mode="each"
    )
    assert len(axes) == 2
    assert len(axes) == len(caxes)
    plt.close(fig)


@pytest.mark.parametrize(
    ("width", "height", "aspect"), [(1, 1, None), (1, None, 1), (None, 1, 1)]
)
def test_faceted_cbar_mode_invalid(width, height, aspect):
    with pytest.raises(ValueError):
        faceted(1, 2, width=width, height=height, aspect=aspect, cbar_mode="invalid")


def test_faceted_invalid_internal_pad():
    with pytest.raises(ValueError):
        faceted(
            1,
            2,
            width=_WIDTH_CONSTRAINT,
            aspect=_ASPECT_CONSTRAINT,
            internal_pad=(1, 2, 3),
        )


@pytest.mark.parametrize(
    ("inputs", "expected"),
    [
        ((None, None, None), (_DEFAULT_WIDTH, None, _DEFAULT_ASPECT)),
        ((3.0, None, None), (3.0, None, _DEFAULT_ASPECT)),
        ((None, 3.0, None), (None, 3.0, _DEFAULT_ASPECT)),
        ((None, None, 3.0), (_DEFAULT_WIDTH, None, 3.0)),
        ((3.0, 3.0, None), (3.0, 3.0, None)),
        ((None, 3.0, 3.0), (None, 3.0, 3.0)),
        ((3.0, None, 3.0), (3.0, None, 3.0)),
        ((3.0, 3.0, 3.0), ValueError),
    ],
    ids=lambda x: str(x),
)
def test__infer_constraints(inputs, expected):
    if not isinstance(expected, tuple) and issubclass(expected, Exception):
        with pytest.raises(expected):
            _infer_constraints(*inputs)
    else:
        result = _infer_constraints(*inputs)
        assert result == expected


@pytest.mark.parametrize(
    ("width", "height", "aspect", "expected"),
    [
        (5.0, 5.0, None, HeightAndWidthConstrainedAxesGrid),
        (5.0, None, 5.0, WidthConstrainedAxesGrid),
        (None, 5.0, 5.0, HeightConstrainedAxesGrid),
    ],
)
def test__infer_grid_class(width, height, aspect, expected):
    result = _infer_grid_class(width, height, aspect)
    assert result == expected


_LAYOUTS = [(1, 1), (1, 2), (2, 1), (2, 2), (5, 3)]
_CBAR_MODES = [None, "single", "each", "edge"]
_CBAR_LOCATIONS = ["bottom", "right", "top", "left"]
_CONSTRAINTS = ["height-and-aspect", "width-and-aspect", "height-and-width"]
_CG_LAYOUTS = product(_CBAR_MODES, _CBAR_LOCATIONS, _LAYOUTS, _CONSTRAINTS)


def format_layout(layout):
    cbar_mode, cbar_loc, (rows, cols), constraint = layout
    return "cbar_mode={!r}, cbar_location={!r}, rows={}, cols={}, constraint={}".format(
        cbar_mode, cbar_loc, rows, cols, constraint
    )


_CG_IDS = OrderedDict([(layout, format_layout(layout)) for layout in _CG_LAYOUTS])


@pytest.fixture(params=_CG_IDS.keys(), ids=_CG_IDS.values())
def grid(request):
    mode, location, (rows, cols), constraint = request.param
    if constraint == "width-and-aspect":
        obj = WidthConstrainedAxesGrid(
            rows,
            cols,
            width=_WIDTH_CONSTRAINT,
            aspect=_ASPECT_CONSTRAINT,
            top_pad=_TOP_PAD,
            bottom_pad=_BOTTOM_PAD,
            left_pad=_LEFT_PAD,
            right_pad=_RIGHT_PAD,
            cbar_mode=mode,
            cbar_pad=_LONG_SIDE_PAD,
            axes_pad=_INTERNAL_PAD,
            cbar_location=location,
            cbar_size=_CBAR_THICKNESS,
            cbar_short_side_pad=_SHORT_SIDE_PAD,
        )
    elif constraint == "height-and-aspect":
        obj = HeightConstrainedAxesGrid(
            rows,
            cols,
            height=_HEIGHT_CONSTRAINT,
            aspect=_ASPECT_CONSTRAINT,
            top_pad=_TOP_PAD,
            bottom_pad=_BOTTOM_PAD,
            left_pad=_LEFT_PAD,
            right_pad=_RIGHT_PAD,
            cbar_mode=mode,
            cbar_pad=_LONG_SIDE_PAD,
            axes_pad=_INTERNAL_PAD,
            cbar_location=location,
            cbar_size=_CBAR_THICKNESS,
            cbar_short_side_pad=_SHORT_SIDE_PAD,
        )
    elif constraint == "height-and-width":
        obj = HeightAndWidthConstrainedAxesGrid(
            rows,
            cols,
            height=_HEIGHT_CONSTRAINT,
            width=_WIDTH_CONSTRAINT,
            top_pad=_TOP_PAD,
            bottom_pad=_BOTTOM_PAD,
            left_pad=_LEFT_PAD,
            right_pad=_RIGHT_PAD,
            cbar_mode=mode,
            cbar_pad=_LONG_SIDE_PAD,
            axes_pad=_INTERNAL_PAD,
            cbar_location=location,
            cbar_size=_CBAR_THICKNESS,
            cbar_short_side_pad=_SHORT_SIDE_PAD,
        )
    else:
        raise NotImplementedError()
    yield obj
    plt.close(obj.fig)


def get_tile_width(grid, left_pad=_LEFT_PAD, right_pad=_RIGHT_PAD):
    return (
        grid.width - left_pad - right_pad - (grid.cols - 1) * _HORIZONTAL_INTERNAL_PAD
    ) / grid.cols


def get_tile_height(grid, bottom_pad=_BOTTOM_PAD, top_pad=_TOP_PAD):
    return (
        grid.height - bottom_pad - top_pad - (grid.rows - 1) * _VERTICAL_INTERNAL_PAD
    ) / grid.rows


def test_constrained_axes_positions(grid):
    if grid.cbar_mode == "each":
        check_constrained_axes_positions_each(grid)
    elif grid.cbar_mode == "single":
        check_constrained_axes_positions_single(grid)
    elif grid.cbar_mode == "edge":
        check_constrained_axes_positions_edge(grid)
    elif grid.cbar_mode is None:
        check_constrained_axes_positions_none(grid)


def test_constrained_caxes_positions(grid):
    if grid.cbar_mode == "each":
        check_constrained_caxes_positions_each(grid)
    elif grid.cbar_mode == "single":
        check_constrained_caxes_positions_single(grid)
    elif grid.cbar_mode == "edge":
        check_constrained_caxes_positions_edge(grid)
    elif grid.cbar_mode is None:
        pytest.skip("Skipping colorbar positions test, because cbar_mode=None")


def test_plot_aspect(grid):
    fig = grid.fig
    width, height = fig.get_size_inches()
    for ax in grid.axes:
        ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
        _, _, _plot_width, _plot_height = ax_bounds
        plot_width = _plot_width * width
        plot_height = _plot_height * height
        expected = grid.aspect
        result = plot_height / plot_width
        np.testing.assert_allclose(result, expected)


def check_constrained_axes_positions_none(grid):
    rows, cols = grid.rows, grid.cols
    width, height = grid.width, grid.height
    tile_width, tile_height = get_tile_width(grid), get_tile_height(grid)
    fig = grid.fig

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    for ax, (row, col) in zip(grid.axes, indexes):
        ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
        x0 = (_LEFT_PAD + col * (_HORIZONTAL_INTERNAL_PAD + tile_width)) / width
        y0 = (_BOTTOM_PAD + row * (_VERTICAL_INTERNAL_PAD + tile_height)) / height
        dx = tile_width / width
        dy = tile_height / height
        expected_bounds = [x0, y0, dx, dy]
        np.testing.assert_allclose(ax_bounds, expected_bounds)


def check_constrained_axes_positions_single(grid):
    rows, cols = grid.rows, grid.cols
    width, height = grid.width, grid.height
    cbar_location = grid.cbar_location
    fig = grid.fig

    left_pad, right_pad = _LEFT_PAD, _RIGHT_PAD
    bottom_pad, top_pad = _BOTTOM_PAD, _TOP_PAD
    if cbar_location == "left":
        left_pad = _LEFT_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD
    elif cbar_location == "right":
        right_pad = _RIGHT_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD
    elif cbar_location == "bottom":
        bottom_pad = _BOTTOM_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD
    elif cbar_location == "top":
        top_pad = _TOP_PAD + _CBAR_THICKNESS + _LONG_SIDE_PAD

    tile_width = get_tile_width(grid, left_pad=left_pad, right_pad=right_pad)
    tile_height = get_tile_height(grid, bottom_pad=bottom_pad, top_pad=top_pad)

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    axes = grid.axes
    for ax, (row, col) in zip(axes, indexes):
        ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
        x0 = (left_pad + col * (_HORIZONTAL_INTERNAL_PAD + tile_width)) / width
        y0 = (bottom_pad + row * (_VERTICAL_INTERNAL_PAD + tile_height)) / height
        dx = tile_width / width
        dy = tile_height / height
        expected_bounds = [x0, y0, dx, dy]
        np.testing.assert_allclose(ax_bounds, expected_bounds)


def check_constrained_caxes_positions_single(grid):
    width, height = grid.width, grid.height
    cbar_location = grid.cbar_location
    fig = grid.fig

    cax = grid.caxes
    cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
    if cbar_location == "bottom":
        x0 = (_LEFT_PAD + _SHORT_SIDE_PAD) / width
        y0 = _BOTTOM_PAD / height
        dx = (width - _LEFT_PAD - _RIGHT_PAD - 2.0 * _SHORT_SIDE_PAD) / width
        dy = _CBAR_THICKNESS / height
    elif cbar_location == "right":
        x0 = (width - _CBAR_THICKNESS - _RIGHT_PAD) / width
        y0 = (_BOTTOM_PAD + _SHORT_SIDE_PAD) / height
        dx = _CBAR_THICKNESS / width
        dy = (height - _TOP_PAD - _BOTTOM_PAD - 2.0 * _SHORT_SIDE_PAD) / height
    elif cbar_location == "top":
        x0 = (_LEFT_PAD + _SHORT_SIDE_PAD) / width
        y0 = (height - _CBAR_THICKNESS - _TOP_PAD) / height
        dx = (width - _LEFT_PAD - _RIGHT_PAD - 2.0 * _SHORT_SIDE_PAD) / width
        dy = _CBAR_THICKNESS / height
    elif cbar_location == "left":
        x0 = _LEFT_PAD / width
        y0 = (_BOTTOM_PAD + _SHORT_SIDE_PAD) / height
        dx = _CBAR_THICKNESS / width
        dy = (height - _TOP_PAD - _BOTTOM_PAD - 2.0 * _SHORT_SIDE_PAD) / height
    expected_bounds = [x0, y0, dx, dy]
    np.testing.assert_allclose(cax_bounds, expected_bounds)


def check_constrained_axes_positions_each(grid):
    rows, cols = grid.rows, grid.cols
    width, height = grid.width, grid.height
    tile_width, tile_height = get_tile_width(grid), get_tile_height(grid)
    cbar_location = grid.cbar_location
    fig = grid.fig

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    axes = grid.axes
    if cbar_location == "bottom":
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (tile_width + _HORIZONTAL_INTERNAL_PAD)) / width
            y0 = (
                _BOTTOM_PAD
                + _CBAR_THICKNESS
                + _LONG_SIDE_PAD
                + row * (tile_height + _VERTICAL_INTERNAL_PAD)
            ) / height
            dx = tile_width / width
            dy = (tile_height - _CBAR_THICKNESS - _LONG_SIDE_PAD) / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(ax_bounds, expected_bounds)
    elif cbar_location == "top":
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_HORIZONTAL_INTERNAL_PAD + tile_width)) / width
            y0 = (_BOTTOM_PAD + row * (_VERTICAL_INTERNAL_PAD + tile_height)) / height
            dx = tile_width / width
            dy = (tile_height - _CBAR_THICKNESS - _LONG_SIDE_PAD) / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(ax_bounds, expected_bounds)
    elif cbar_location == "right":
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_HORIZONTAL_INTERNAL_PAD + tile_width)) / width
            y0 = (_BOTTOM_PAD + row * (_VERTICAL_INTERNAL_PAD + tile_height)) / height
            dx = (tile_width - _CBAR_THICKNESS - _LONG_SIDE_PAD) / width
            dy = tile_height / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(ax_bounds, expected_bounds)
    elif cbar_location == "left":
        for ax, (row, col) in zip(axes, indexes):
            ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (
                _LEFT_PAD
                + _CBAR_THICKNESS
                + _LONG_SIDE_PAD
                + col * (_HORIZONTAL_INTERNAL_PAD + tile_width)
            ) / width
            y0 = (_BOTTOM_PAD + row * (_VERTICAL_INTERNAL_PAD + tile_height)) / height
            dx = (tile_width - _CBAR_THICKNESS - _LONG_SIDE_PAD) / width
            dy = tile_height / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(ax_bounds, expected_bounds)


def check_constrained_caxes_positions_each(grid):
    rows, cols = grid.rows, grid.cols
    width, height = grid.width, grid.height
    tile_width, tile_height = get_tile_width(grid), get_tile_height(grid)
    cbar_location = grid.cbar_location
    fig = grid.fig

    indexes = list(product(range(rows - 1, -1, -1), range(cols)))
    caxes = grid.caxes
    if cbar_location == "bottom":
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (
                _LEFT_PAD
                + col * (_HORIZONTAL_INTERNAL_PAD + tile_width)
                + _SHORT_SIDE_PAD
            ) / width
            y0 = (_BOTTOM_PAD + row * (_VERTICAL_INTERNAL_PAD + tile_height)) / height
            dx = (tile_width - 2.0 * _SHORT_SIDE_PAD) / width
            dy = _CBAR_THICKNESS / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == "top":
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (
                _LEFT_PAD
                + col * (_HORIZONTAL_INTERNAL_PAD + tile_width)
                + _SHORT_SIDE_PAD
            ) / width
            y0 = (
                _BOTTOM_PAD
                + row * (_VERTICAL_INTERNAL_PAD + tile_height)
                + tile_height
                - _CBAR_THICKNESS
            ) / height
            dx = (tile_width - 2.0 * _SHORT_SIDE_PAD) / width
            dy = _CBAR_THICKNESS / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == "right":
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (
                _LEFT_PAD
                + col * (_HORIZONTAL_INTERNAL_PAD + tile_width)
                + tile_width
                - _CBAR_THICKNESS
            ) / width
            y0 = (
                _BOTTOM_PAD
                + row * (_VERTICAL_INTERNAL_PAD + tile_height)
                + _SHORT_SIDE_PAD
            ) / height
            dx = _CBAR_THICKNESS / width
            dy = (tile_height - 2.0 * _SHORT_SIDE_PAD) / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == "left":
        for cax, (row, col) in zip(caxes, indexes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (_LEFT_PAD + col * (_HORIZONTAL_INTERNAL_PAD + tile_width)) / width
            y0 = (
                _BOTTOM_PAD
                + row * (_VERTICAL_INTERNAL_PAD + tile_height)
                + _SHORT_SIDE_PAD
            ) / height
            dx = _CBAR_THICKNESS / width
            dy = (tile_height - 2.0 * _SHORT_SIDE_PAD) / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)


def check_constrained_axes_positions_edge(grid):
    # The positions of the axes are the same as for cbar_mode='single'
    check_constrained_axes_positions_single(grid)


def check_constrained_caxes_positions_edge(grid):
    rows, cols = grid.rows, grid.cols
    width, height = grid.width, grid.height
    tile_width, tile_height = get_tile_width(grid), get_tile_height(grid)
    cbar_location = grid.cbar_location
    fig = grid.fig

    caxes = grid.caxes
    if cbar_location == "bottom":
        for col, cax in zip(range(cols), caxes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (
                _LEFT_PAD
                + col * (_HORIZONTAL_INTERNAL_PAD + tile_width)
                + _SHORT_SIDE_PAD
            ) / width
            y0 = _BOTTOM_PAD / height
            dx = (tile_width - 2.0 * _SHORT_SIDE_PAD) / width
            dy = _CBAR_THICKNESS / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == "top":
        for col, cax in zip(range(cols), caxes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (
                _LEFT_PAD
                + col * (_HORIZONTAL_INTERNAL_PAD + tile_width)
                + _SHORT_SIDE_PAD
            ) / width
            y0 = (height - _CBAR_THICKNESS - _TOP_PAD) / height
            dx = (tile_width - 2.0 * _SHORT_SIDE_PAD) / width
            dy = _CBAR_THICKNESS / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == "right":
        for row, cax in zip(range(rows - 1, -1, -1), caxes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = (width - _CBAR_THICKNESS - _RIGHT_PAD) / width
            y0 = (
                _BOTTOM_PAD
                + row * (_VERTICAL_INTERNAL_PAD + tile_height)
                + _SHORT_SIDE_PAD
            ) / height
            dx = _CBAR_THICKNESS / width
            dy = (tile_height - 2.0 * _SHORT_SIDE_PAD) / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)
    elif cbar_location == "left":
        for row, cax in zip(range(rows - 1, -1, -1), caxes):
            cax_bounds = cax.bbox.inverse_transformed(fig.transFigure).bounds
            x0 = _LEFT_PAD / width
            y0 = (
                _BOTTOM_PAD
                + row * (_VERTICAL_INTERNAL_PAD + tile_height)
                + _SHORT_SIDE_PAD
            ) / height
            dx = _CBAR_THICKNESS / width
            dy = (tile_height - 2.0 * _SHORT_SIDE_PAD) / height
            expected_bounds = [x0, y0, dx, dy]
            np.testing.assert_allclose(cax_bounds, expected_bounds)


def shared_grid(sharex, sharey):
    return WidthConstrainedAxesGrid(
        2,
        2,
        width=_WIDTH_CONSTRAINT,
        aspect=_ASPECT_CONSTRAINT,
        sharex=sharex,
        sharey=sharey,
        cbar_mode="single",
    )


def assert_visible_xticklabels(ax):
    assert ax.xaxis._get_tick(ax.xaxis.major).label1.get_visible()
    assert ax.xaxis._get_tick(ax.xaxis.minor).label1.get_visible()


def assert_invisible_xticklabels(ax):
    assert not ax.xaxis._get_tick(ax.xaxis.major).label1.get_visible()
    assert not ax.xaxis._get_tick(ax.xaxis.minor).label1.get_visible()


def assert_visible_yticklabels(ax):
    assert ax.yaxis._get_tick(ax.yaxis.major).label1.get_visible()
    assert ax.yaxis._get_tick(ax.yaxis.minor).label1.get_visible()


def assert_invisible_yticklabels(ax):
    assert not ax.yaxis._get_tick(ax.yaxis.major).label1.get_visible()
    assert not ax.yaxis._get_tick(ax.yaxis.minor).label1.get_visible()


def assert_valid_x_sharing(shared_grid, sharex):
    axes = np.reshape(shared_grid.axes, (shared_grid.rows, shared_grid.cols))
    if sharex in ["all", True]:
        ax_ref = axes.flatten()[0]
        for ax in axes.flatten():
            assert ax.xaxis.major == ax_ref.xaxis.major
            assert ax.xaxis.minor == ax_ref.xaxis.minor
        for ax in axes[:-1, :].flatten():
            assert_invisible_xticklabels(ax)
        for ax in axes[-1, :].flatten():
            assert_visible_xticklabels(ax)
    elif sharex == "row":
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
        for ax in axes.flatten():
            assert_visible_xticklabels(ax)
    elif sharex == "col":
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
        for ax in axes[:-1, :].flatten():
            assert_invisible_xticklabels(ax)
        for ax in axes[-1, :].flatten():
            assert_visible_xticklabels(ax)
    elif sharex in ["none", False]:
        ax_ref = axes.flatten()[0]
        for ax in axes.flatten()[1:]:
            assert ax.xaxis.major != ax_ref.xaxis.major
            assert ax.xaxis.minor != ax_ref.xaxis.minor
        for ax in axes.flatten():
            assert_visible_xticklabels(ax)


def assert_valid_y_sharing(shared_grid, sharey):
    axes = np.reshape(shared_grid.axes, (shared_grid.rows, shared_grid.cols))
    if sharey in ["all", True]:
        ax_ref = axes.flatten()[0]
        for ax in axes.flatten():
            assert ax.yaxis.major == ax_ref.yaxis.major
            assert ax.yaxis.minor == ax_ref.yaxis.minor
        for ax in axes[:, 1:].flatten():
            assert_invisible_yticklabels(ax)
        for ax in axes[:, 0].flatten():
            assert_visible_yticklabels(ax)
    elif sharey == "row":
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
        for ax in axes[:, 1:].flatten():
            assert_invisible_yticklabels(ax)
        for ax in axes[:, 0].flatten():
            assert_visible_yticklabels(ax)
    elif sharey == "col":
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
        for ax in axes.flatten():
            assert_visible_yticklabels(ax)
    elif sharey in ["none", False]:
        ax_ref = axes.flatten()[0]
        for ax in axes.flatten()[1:]:
            assert ax.yaxis.major != ax_ref.yaxis.major
            assert ax.yaxis.minor != ax_ref.yaxis.minor
        for ax in axes.flatten():
            assert_visible_yticklabels(ax)


_SHARE_OPTIONS = ["all", "row", "col", "none", True, False]


@pytest.mark.parametrize(("sharex", "sharey"), product(_SHARE_OPTIONS, _SHARE_OPTIONS))
def test_share_axes_mixin(sharex, sharey):
    grid = shared_grid(sharex, sharey)
    assert_valid_x_sharing(grid, sharex)
    assert_valid_y_sharing(grid, sharey)
    plt.close(grid.fig)


def test_cartopy():
    pytest.importorskip("cartopy")
    import cartopy.crs as ccrs
    from cartopy.mpl.geoaxes import GeoAxes

    fig, axes = faceted(
        2,
        2,
        width=_WIDTH_CONSTRAINT,
        aspect=_ASPECT_CONSTRAINT,
        axes_kwargs={"projection": ccrs.PlateCarree()},
    )
    for ax in axes:
        assert isinstance(ax, GeoAxes)
    plt.close(fig)


@pytest.mark.parametrize(
    ("cbar_mode", "cbar_expected"),
    [(None, False), ("single", True), ("edge", True), ("each", True)],
)
def test_faceted_ax(cbar_mode, cbar_expected):
    if cbar_expected:
        fig, ax, cax = faceted_ax(
            cbar_mode=cbar_mode, width=_WIDTH_CONSTRAINT, aspect=_ASPECT_CONSTRAINT
        )
        assert isinstance(fig, matplotlib.figure.Figure)
        assert isinstance(ax, matplotlib.axes.Axes)
        assert isinstance(cax, matplotlib.axes.Axes)
    else:
        fig, ax = faceted_ax(
            cbar_mode=cbar_mode, width=_WIDTH_CONSTRAINT, aspect=_ASPECT_CONSTRAINT
        )
        assert isinstance(fig, matplotlib.figure.Figure)
        assert isinstance(ax, matplotlib.axes.Axes)
