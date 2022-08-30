"""
Spectral models from Jankowski et al. 2018 and references within
"""

import numpy as np
from mpmath import gammainc

def gammainc_up(a,z):
    """Vectorised upper incomplete gamma function.
    Taken from: https://stackoverflow.com/questions/10542780/incomplete-gamma-function-in-python
    """
    return np.asarray([gammainc(a, zi, regularized=False)
                       for zi in z]).astype(float)


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


def simple_power_law_intergrate(vmin_vmax, a, c, v0):
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
    vmin, vmax = vmin_vmax
    return c * (vmax**(a+1) - vmin**(a+1)) / ( (vmax - vmin) * v0**a * (a+1) )


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


def broken_power_law_intergral(vmin_vmax, vb, a1, a2, c, v0):
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
    vmin, vmax = vmin_vmax
    return np.select(
        [
            (vmin < vmax) & (vmax <= vb),
            (vb <= vmin) & (vmin < vmax),
            (vmin < vb) & (vb < vmax)
        ],
        [
            c * ( vmax**(a1+1) - vmin**(a1+1) ) / ( (vmax - vmin) * v0**a1 * (a1+1) ),
            c * ( vmax**(a2+1) - vmin**(a2+1) ) / ( (vmax - vmin) * v0**a2 * (a2+1) ) * ( vb / v0 )**(a1-a2),
            c * ( vmax**(a1+1) - vmin**(a1+1) ) / ( (vb - vmin) * v0**a1 * (a1+1) ) + c * ( vmax**(a2+1) - vmin**(a2+1) ) / ( (vmax - vb) * v0**a2 * (a2+1) ) * ( vb / v0 )**(a1-a2),
        ]
    )


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


def high_frequency_cut_off_power_law_intergral(vmin_vmax, vc, a, c, v0):
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
    vmin, vmax = vmin_vmax
    BW = vmax - vmin
    v = vmin + BW / 2
    y1 = c / ( BW * v0**a ) * ( (vmax**(a+1) - vmin**(a+1)) / (a+1) + (vmax**(a+2) - vmin**(a+2)) / (v0 * vc * (a+2)))
    y2 = 0.
    return np.where(v < vc, y1, y2)


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


def low_frequency_turn_over_power_law_intergral(vmin_vmax, vpeak, a, c, beta, v0):
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
    vmin, vmax = vmin_vmax
    BW = vmax - vmin
    Xmin = ( vmin / v0 )**a
    Ymin = - ( a / beta ) * ( vmin / vpeak )**( -beta )
    Xmax = ( vmax / v0 )**a
    Ymax = - ( a / beta ) * ( vmax / vpeak )**( -beta )
    Z = - ( a + 1 ) / beta
    return ( c / (BW * beta) ) * ( (vmax * Xmax * Ymax**(-Z) * gammainc_up(Z,Ymax)) - (vmin * Xmin * Ymin**(-Z) * gammainc_up(Z,Ymin)) )


def low_frequency_turn_over_power_law_taylor(vmin_vmax, vpeak, a, c, beta, v0):
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
    vmin, vmax = vmin_vmax
    BW = vmax - vmin
    v = (vmax + vmin) / 2
    X = (v / vpeak)**beta
    s0 = low_frequency_turn_over_power_law(v, vpeak, a, c, beta, v0)
    s2 = (s0 * a) / (v**2 * X**2) * (X**2* (a - 1) + X*(-2*a + beta + 1) + a)
    s4 = (s0 * a) / (v**4 * X**4) * ( \
        X**4 * (a**3 - 4*a**3 + 6*a**2 + 11*a - 6) + \
        X**3 * (6*a**2*beta - 4*a*beta**2 + 18*a*beta + 18*a**2 - 22*a + beta**3 + 6*beta**2 + 11*beta - 6) + \
        X**2*a*(6*a**2 - 12*a*beta + 18*a + 7*beta**2 - 18*beta + 11) + \
        X*a**2*(4*a + 6*beta - 6) + \
        a**3\
    )
    return s0 + (s2*BW**2) / 12 + (s4*BW**4) / 80



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


def double_turn_over_spectrum_intergral(vmin_vmax, vc, vpeak, a, beta, c, v0):
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
    vmin, vmax = vmin_vmax
    BW = vmax - vmin
    v = vmin + BW / 2
    Xmin = ( vmin / v0 )**a
    Xmax = ( vmax / v0 )**a
    dXmin = ( vmin / v0 )**(a + 1)
    dXmax = ( vmax / v0 )**(a + 1)
    Ymin = - ( a / beta ) * ( vmin / vpeak )**( -beta )
    Ymax = - ( a / beta ) * ( vmax / vpeak )**( -beta )
    Z = - ( a + 1 ) / beta
    dZ = - ( a + 2 ) / beta
    part1 = vmax * Xmax * Ymax**(-Z) * gammainc_up(Z, Ymax) - vmin * Xmin * Ymin**(-Z) * gammainc_up(Z, Ymin)
    part2 = ( v0 / vc ) * ( vmax * dXmax * Ymax**(-dZ) * gammainc_up(dZ, Ymax) - vmin * dXmin * Ymin**(-dZ) * gammainc_up(dZ, Ymin) )
    y1 = ( c / ( BW * beta ) ) * (part1 - part2)
    y2 = 0
    return np.where(v < vc, y1, y2)


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
    # fit starting value, min and max
    # constant
    c_s = 1.
    c_min = 0.
    c_max = None
    # spectral index
    a_s = -1.6
    a_min = -8.
    a_max = 3.
    # Beta, he smoothness of the turn-over
    beta_s = 1.
    beta_min = 0.1
    beta_max = 2.1
    # High frequency cut off frequency
    vc_s = 4e9
    vc_both = None # will set the cut off frequency based on the data set's frequency range
    # Lof frequency turn over frequency peak
    vpeak_s = 100e6
    vpeak_min = 10e6
    vpeak_max = 2e9


    model_dict = {
        # Name: [model_function, short_name, start_params, mod_limits]
        "simple_power_law" : [
            simple_power_law,
            "simple pl",
            # (a, c)
            (a_s, c_s),
            [(a_min, a_max), (c_min, c_max)],
            simple_power_law_intergrate,
        ],
        "broken_power_law" : [
            broken_power_law,
            "broken pl",
            #(vb, a1, a2, c)
            (1e9, a_s, a_s, c_s),
            [(50e6, 5e9), (a_min, a_max), (a_min, a_max), (c_min, c_max)],
            broken_power_law_intergral,
        ],
        # "log_parabolic_spectrum" : [
        #     log_parabolic_spectrum,
        #     "lps",
        #     #(a, b, c)
        #     (-1, -1., c_s),
        #     [(-5, 2), (-5, 2), (None, c_max)],
        # ],
        "high_frequency_cut_off_power_law" : [
            high_frequency_cut_off_power_law,
            "pl hard cut-off",
            #(vc, a, c)
            (vc_s, a_s, c_s),
            [vc_both, (a_min, 0.), (c_min, c_max)],
            high_frequency_cut_off_power_law_intergral,
        ],
        "low_frequency_turn_over_power_law" : [
            low_frequency_turn_over_power_law,
            "pl low turn-over",
            #(vpeak, a, c, beta)
            (vpeak_s, a_s, c_s, beta_s),
            [(vpeak_min, vpeak_max), (a_min, 0.), (c_min, c_max) , (beta_min, beta_max)],
            low_frequency_turn_over_power_law_taylor,
        ],
        "double_turn_over_spectrum" : [
            double_turn_over_spectrum,
            "double turn over spectrum",
            #(vc, vpeak, a, beta, c)
            (vc_s, vpeak_s, a_s, beta_s, c_s),
            [(vc_both), (vpeak_min, vpeak_max), (a_min, 0.), (beta_min, beta_max), (c_min, c_max)],
            double_turn_over_spectrum_intergral,
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