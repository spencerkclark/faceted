"""Test suite for facets module"""
from itertools import product

import numpy as np
import pytest

from facets.facets import Tile, BasicGrid


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


@pytest.mark.parametrize(
    ('rows', 'cols'),
    [(1, 1), (1, 2), (2, 1), (2, 2), (3, 5)])
def test_basic_grid(rows, cols):
    top_pad = bottom_pad = left_pad = right_pad = 0.25
    internal_pad = 0.33
    aspect = 0.5
    width_constraint = 8.

    bg = BasicGrid(
        rows, cols, width_constraint=width_constraint,
        aspect=aspect, top_pad=top_pad, bottom_pad=bottom_pad,
        left_pad=left_pad, right_pad=right_pad,
        internal_pad=internal_pad
    )
    fig = bg.fig
    expected_plot_width = (width_constraint - left_pad - right_pad -
                           (cols - 1) * internal_pad) / cols
    expected_plot_height = expected_plot_width * aspect
    expected_height = (rows * expected_plot_height +
                       (rows - 1) * internal_pad + bottom_pad + top_pad)
    expected_width = width_constraint
    result_width, result_height = fig.get_size_inches()
    assert result_width == expected_width
    assert result_height == expected_height
    assert bg.tile_width == expected_plot_width
    assert bg.tile_height == expected_plot_height

    places = list(product(range(rows - 1, -1, -1), range(cols)))
    for ax, (row, col) in zip(bg.axes(), places):
        ax_bounds = ax.bbox.inverse_transformed(fig.transFigure).bounds
        x0 = (left_pad +
              col * (internal_pad + expected_plot_width)) / expected_width
        y0 = (bottom_pad +
              row * (internal_pad + expected_plot_height)) / expected_height
        x = expected_plot_width / expected_width
        y = expected_plot_height / expected_height
        expected_bounds = [x0, y0, x, y]
        np.testing.assert_allclose(ax_bounds, expected_bounds)
