"""
Spectral models from Jankowski et al. 2018 and references within
"""

import numpy as np

def simple_power_law(v, a, b):
    """Simple power law:

    .. math::
        S_v = b x^a

    where :math:`x=\\frac{v}{1.3e9}`

    Parameters
    ----------
    v : `list`
        Frequency in Hz.
    a : `float`
        Spectral Index.
    b : `float`
        Constant.

    Returns
    -------
    S_v : `list`
        The flux density predicted by the model.
    """
    v0 = 1.3e9
    return b*(v/v0)**a

def broken_power_law(v, vb, a1, a2, b):
    """Broken power law:

    .. math::
        S_v = b \left\{\\begin{matrix} x^{a_1} & \mathrm{if} x ≤ x_b \\\\ x^{a_2}x_b^{a_1-a_2} & \mathrm{otherwise'} \end{matrix}\\right.

    where :math:`x=\\frac{v}{1.3e9},x_b=\\frac{v_b}{1.3e9}`

    Parameters
    ----------
    v : `list`
        Frequency in Hz.
    v_b : `float`
        The frequency of the break in Hz.
    a_1 : `float`
        The spectral index before the break.
    a_2 : `float`
        The spectral index after the break.
    b : `float`
        Constant.

    Returns
    -------
    S_v : `list`
        The flux density predicted by the model.
    """
    v0 = 1.3e9
    x = v / v0
    xb = vb / v0
    y1 = b*x**a1
    y2 = b*x**a2*(xb)**(a1-a2)
    return np.where(x <= xb, y1, y2)

def double_broken_power_law(v, vb1, vb2, a1, a2, a3, b):
    v0 = 1.3e9
    x = v / v0
    xb1 = vb1 / v0
    xb2 = vb2 / v0
    y1 = b*x**a1
    y2 = b*x**a2*(xb1)**(a1-a2)
    y3 = b*x**a3*(xb2)**(a2-a3)
    return np.piecewise(x, [x <= xb1, (x > xb1) & (x <= xb2), x > xb2], [y1, y2, y3])

def log_parabolic_spectrum(v, a, b, c):
    """Log-parabolic spectrum:

    .. math::
       \mathrm{log}_{10} S_v = ax^2 + bx +c

    where :math:`x=\mathrm{log}_{10} \left ( \\frac{v}{1.3e9} \\right )`

    Parameters
    ----------
    v : `list`
        Frequency in Hz.
    a : `float`
        Curvature parameter.
    b : `float`
        The spectral index for :math:`a = 0`.
    c : `float`
        Constant.

    Returns
    -------
    S_v : `list`
        The flux density predicted by the model.
    """
    v0 = 1.3e9
    x = np.log10( v / v0 )
    return 10**(a*x**2 + b*x + c)

def high_frequency_cut_off_power_law(v, vc, a, b):
    """Power law with high-frequency cut-off off:

    .. math::
        S_v = bx^{-2} \left ( 1 - \\frac{x}{x_c} \\right ), x < x_c

    where :math:`x=\\frac{v}{1.3e9},x_c=\\frac{v_c}{1.3e9}`

    Parameters
    ----------
    v : `list`
        Frequency in Hz.
    v_c : `list`
        Cut off frequency in Hz.
    a : `float`
        The spectral index before the power cut-off.
    b : `float`
        Constant.

    Returns
    -------
    S_v : `list`
        The flux density predicted by the model.
    """
    v0 = 1.3e9
    x = v / v0
    xc = vc / v0
    y1 = b*x**(-2) * ( 1 - x / xc )
    y2 = b*x**a
    return np.where(x < xc, y1, y2)

def low_frequency_turn_over_power_law(v, vc, a, b, beta):
    """power law with low-frequency turn-over:

    .. math::
        S_v = bx^{a} exp\left ( \\frac{a}{\\beta} x_c^{-\\beta} \\right )

    where :math:`x=\\frac{v}{1.3e9},x_c=\\frac{v_c}{1.3e9}`

    Parameters
    ----------
    v : `list`
        Frequency in Hz.
    v_c : `list`
        Trun-over frequency in Hz.
    a : `float`
        The spectral index.
    b : `float`
        Constant.
    beta : `float`
        The smoothness of the turn-over.

    Returns
    -------
    S_v : `list`
        The flux density predicted by the model.
    """
    v0 = 1.3e9
    x = v / v0
    xc = v / vc
    return b * x**a * np.exp( a / beta * xc**(-beta) )