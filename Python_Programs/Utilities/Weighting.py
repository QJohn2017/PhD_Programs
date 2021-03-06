import numpy as np

import sdf


def first_order_weight_2d(x, y, dx, dy, p_values, values=None, weight=None):
    """
    Perform first-order (linear or area) weighting for mapping
    particles onto a grid

    Parameters
    ----------
    x, y : arrays containing the physical x and y values for the
        original grid
    dx, dy : floats providing the physical spacing between cells
    p_values : array containing the physical particle positions;
        elements should be of form (x_pos, y_pos)
    values (opt) : an array containing some physical quantity
        of the particle (velocity, temp, etc.) to weight onto
        the grid
    weight (opt) : an array containing the particle weightings

    Returns
    -------
    weighted_grid : the grid with the weighted particle
        values mapped onto it; has the same shape as
        (size(x) x size(y)); the origin of this matrix
        is the upper left corner
    """

    x_size = np.size(x)
    y_size = np.size(y)
    weighted_grid = np.zeros((x_size, y_size), dtype=np.float64)

    # x_grid, y_grid = np.meshgrid(x, y)

    x_min = np.min(x)
    y_min = np.min(y)

    for p_index, p in enumerate(p_values):
        x_pos = p[0]
        y_pos = p[1]

        fi = (x_pos - x_min) / dx
        i  = int(np.floor(fi))
        hx = fi - i

        fj = (y_pos - y_min) / dy
        j  = int(np.floor(fj))
        hy = fj - j

        if values is not None:
            v = values[p_index]
        else:
            v = 1.0
        if weight is not None:
            w = weight[p_index]
        else:
            w = 1.0

        if i >= 0 and i < x_size and \
           j >= 0 and j < y_size:
            weighted_grid[i, j] += (1 - hx) * (1 - hy) * v * w / dx / dy
        if (i+1) >= 0 and (i+1) < x_size and \
           j     >= 0 and j     < y_size:
            weighted_grid[i+1, j] += (1 - hx) * hy * v * w / dx / dy
        if i     >= 0 and i     < x_size and \
           (j+1) >= 0 and (j+1) < y_size:
            weighted_grid[i, j+1] += hx * (1 - hy) * v * w / dx / dy
        if (i+1) >= 0 and (i+1) < x_size and \
           (j+1) >= 0 and (j+1) < y_size:
            weighted_grid[i+1, j+1] += hx * hy * v * w / dx / dy

        # weighted_grid[i, j] += (1 - hx) * (1 - hy) * v * w / dx / dy
        # weighted_grid[i+1, j] += (1 - hx) * hy * v * w / dx / dy
        # weighted_grid[i, j+1] += hx * (1 - hy) * v * w / dx / dy
        # weighted_grid[i+1, j+1] += hx * hy * v * w / dx / dy

    return weighted_grid
