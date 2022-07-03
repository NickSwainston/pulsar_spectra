"""
Spectral models from Jankowski et al. 2018 and references within
"""

import numpy as np

def simple_power_law(v, a, c, v0):
    """Simple power law:

    .. math::
        S_v =  c \\left( \\frac{v}{v_0} \\right)^a

    Parameters
    ----------
    v : `list`
        Frequency in Hz.
    a : `float`
        Spectral Index.
    c : `float`
        Constant.
    v0 : `float`
        Reference frequency.

    Returns
    -------
    S_v : `list`
        The flux density predicted by the model.
    """
    return c*(v/v0)**a

def broken_power_law(v, vb, a1, a2, c, v0):
    """Broken power law:

    .. math::

        S_v = \\begin{cases}
        c \\left( \\frac{v}{v0} \\right)^{a1}   & \\mathrm{if}\\: v \\leq vb \\\\
        c \\left( \\frac{v}{v0} \\right)^{a2} \\left( \\frac{vb}{v0} \\right)^{a1-a2} & \\mathrm{otherwise} \\\\
        \\end{cases}

    Parameters
    ----------
    v : `list`
        Frequency in Hz.
    vb : `float`
        The frequency of the break in Hz.
    a1 : `float`
        The spectral index before the break.
    a2 : `float`
        The spectral index after the break.
    c : `float`
        Constant.
    v0 : `float`
        Reference frequency.

    Returns
    -------
    S_v : `list`
        The flux density predicted by the model.
    """
    x = v / v0
    xb = vb / v0
    y1 = c*x**a1
    y2 = c*x**a2*(xb)**(a1-a2)
    return np.where(x <= xb, y1, y2)

def double_broken_power_law(v, vb1, vb2, a1, a2, a3, c, v0):
    x = v / v0
    xb1 = vb1 / v0
    xb2 = vb2 / v0
    return np.piecewise(x, [x <= xb1, (x > xb1) & (x <= xb2), x > xb2], \
    [lambda x: c*x**a1, \
     lambda x: c*x**a2*(xb1)**(a1-a2), \
     lambda x: c*x**a3*(xb1)**(a1-a2)*(xb2)**(a2-a3)])

def log_parabolic_spectrum(v, a, b, c, v0):
    """Log-parabolic spectrum:

    .. math::
        \\log_{10} S_v = a  \\left [ \\log_{10} \\left ( \\frac{v}{v0} \\right ) \\right]^2 +
        b \\, \\log_{10} \\left ( \\frac{v}{v0} \\right ) + c

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
    v0 : `float`
        Reference frequency.

    Returns
    -------
    S_v : `list`
        The flux density predicted by the model.
    """
    x = np.log10( v / v0 )
    return 10**(a*x**2 + b*x + c)

def calc_log_parabolic_spectrum_max_freq(a, b, v0, u_a, u_b, u_ab):
    """Calculate the frequency where the flux is at its maximum for the log parabolic model (:py:meth:`pulsar_spectra.models.log_parabolic_spectrum`).

    Parameters
    ----------
    a : `float`
        Curvature parameter.
    b : `float`
        The spectral index for :math:`a = 0`.
    v0 : `float`
        Reference frequency.
    u_a : `float`
        The uncertainty of the curvature parameter, a.
    u_b : `float`
        The uncertainty of b.
    u_ab : `float`
        The covariance between a and b.

    Returns
    -------
    v_peak : `float`
        The frequency in Hz where the flux is at its maximum for the log parabolic model.
    u_v_peak : `float`
        The uncertainty of v_peak in Hz.
    """
    v_peak = v0 * 10**(-b/(2*a))
    u_v_peak = abs(v_peak * np.log(10) / (2*a) * np.sqrt( (u_b)**2 + (b*u_a/a)**2 - 2*b*u_ab/a ))
    return v_peak, u_v_peak

def high_frequency_cut_off_power_law(v, vc, a, c, v0):
    """Power law with high-frequency cut-off off:

    .. math::
        S_v = c \\left( \\frac{v}{v0} \\right)^{a} \\left ( 1 - \\frac{v}{vc} \\right ),\\qquad v < vc

    Parameters
    ----------
    v : `list`
        Frequency in Hz.
    vc : `list`
        Cut off frequency in Hz.
    a : `float`
        Spectral Index.
    c : `float`
        Constant.
    v0 : `float`
        Reference frequency.

    Returns
    -------
    S_v : `list`
        The flux density predicted by the model.
    """
    x = v / v0
    xc = vc / v0
    y1 = c*x**a * ( 1 - x / xc )
    y2 = 0.
    return np.where(x < xc, y1, y2)

def low_frequency_turn_over_power_law(v, vpeak, a, c, beta, v0):
    """power law with low-frequency turn-over:

    .. math::
        S_v = c \\left( \\frac{v}{v0} \\right)^{a} \\exp\\left [ \\frac{a}{\\beta} \\left( \\frac{v}{vc} \\right)^{-\\beta} \\right ]

    Parameters
    ----------
    v : `list`
        Frequency in Hz.
    vpeak : `list`
        Peak/Turn-over frequency in Hz.
    a : `float`
        The spectral index.
    c : `float`
        Constant.
    beta : `float`
        The smoothness of the turn-over.
    v0 : `float`
        Reference frequency.

    Returns
    -------
    S_v : `list`
        The flux density predicted by the model.
    """
    x = v / v0
    xpeak = v / vpeak
    return c * x**a * np.exp( a / beta * xpeak**(-beta) )

def double_turn_over_spectrum(v, vc, vpeak, a, beta, c, v0):
    """Double turn over spectrum, has a low frequency turn over and a high frequency cut off:

    .. math::
        S_v = c \\left( \\frac{v}{v0} \\right)^{a} \\left ( 1 - \\frac{v}{vc} \\right ) \\exp\\left [ \\frac{a}{\\beta} \\left( \\frac{v}{vc} \\right)^{-\\beta} \\right ],\\qquad v < vc

    Parameters
    ----------
    v : `list`
        Frequency in Hz.
    vc : `list`
        Cut off frequency in Hz.
    vpeak : `list`
        Peak/turn-over frequency in Hz.
    a : `float`
        Spectral Index.
    beta : `float`
        The smoothness of the turn-over.
    c : `float`
        Constant.
    v0 : `float`
        Reference frequency.

    Returns
    -------
    S_v : `list`
        The flux density predicted by the model.
    """
    x = v / v0
    xc = vc / v0
    xpeak = v / vpeak
    y1 = c*x**a * ( 1 - x / xc ) * np.exp( a / beta * xpeak**(-beta) )
    y2 = 0.
    return np.where(x < xc, y1, y2)

def model_settings(print_models=False):
    """Holds metadata about spectral models such as common names and default fit parameters.

    Parameters
    ----------
    print_models : `boolean`, optional
        If true, will print the models dictionary which is useful for debuging new models. Default False.

    Returns
    -------
    model_dict : `dict`
        Returns a dictionary in the format

        {model_name: [model_function, short_name, start_params, mod_limits]}
    """
    model_dict = {
        # Name: [model_function, short_name, start_params, mod_limits]
        "simple_power_law" : [
            simple_power_law,
            "simple pl",
            (-1.6, 0.003),
            [(None, 0), (0, None)],
        ],
        "broken_power_law" : [
            broken_power_law,
            "broken pl",
            (1e9, -1.6, -1.6, 0.1),
            [(50e6, 5e9), (-5, 5), (-5, 5), (0, None)],
        ],
        "log_parabolic_spectrum" : [
            log_parabolic_spectrum,
            "lps",
            (-1, -1., 1.),
            [(-5, 2), (-5, 2), (None, None)],
        ],
        "high_frequency_cut_off_power_law" : [
            high_frequency_cut_off_power_law,
            "pl hard cut-off",
            (4e9, -1.6, 1.),
            [None, (-5, 5), (0, None)], # will set the cut off frequency based on the data set's frequency range
        ],
        "low_frequency_turn_over_power_law" : [
            low_frequency_turn_over_power_law,
            "pl low turn-over",
            (100e6, -2.5, 1.e1, 1.),
            [(10e6, 2e9), (-5, -.5), (0, 1e4) , (.1, 2.1)],
        ],
        #"double_broken_power_law" : [
        #    double_broken_power_law,
        #    "double bpl",
        #    (100e6, 1e9, -1.6, -1.6, -1.6, 0.1),
        #    [(10e6, 100e9), (1e9, 100e9), (-5, 5), (-5, 5), (-5, 5), (0, None)],
        #],
    }

    if print_models:
        # Print the models dictionary which is useful for debuging new models
        for mod in model_dict.keys():
            print(f"\n{mod}")
            model_function, short_name, start_params, mod_limits = model_dict[mod]
            print(f"    model_function: {model_function}")
            print(f"    short_name: {short_name}")
            print(f"    start_params: {start_params}")
            print(f"    mod_limits: {mod_limits}")

    return model_dict