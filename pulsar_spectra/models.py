"""
Spectral models from Jankowski et al. 2018 and references within
"""

import numpy as np

def simple_power_law(v, a, b):
    v0 = 1.3e9
    return b*(v/v0)**a

def broken_power_law(v, a1, a2, b, vb):
    v0 = 1.3e9
    x = v / v0
    xb = vb / v0
    y1 = b*x**a1
    y2 = b*x**a2*(xb)**(a1-a2)
    return np.where(x <= xb, y1, y2)

def double_broken_power_law(v, a1, a2, a3, b, vb1, vb2):
    v0 = 1.3e9
    x = v / v0
    xb1 = vb1 / v0
    xb2 = vb2 / v0
    y1 = b*x**a1
    y2 = b*x**a2*(xb1)**(a1-a2)
    y3 = b*x**a3*(xb2)**(a2-a3)
    return np.piecewise(x, [x <= xb1, (x > xb1) & (x <= xb2), x > xb2], [y1, y2, y3])

def log_parabolic_spectrum(v, a, b, c):
    v0 = 1.3e9
    x = np.log10( v / v0 )
    return 10**(a*x**2 + b*x + c)

def high_frequency_cut_off_power_law(v, a, b, vc):
    v0 = 1.3e9
    x = v / v0
    xc = vc / v0
    y1 = b*x**(-2) * ( 1 - x / xc )
    y2 = b*x**a
    return np.where(x < xc, y1, y2)

def low_frequency_turn_over_power_law(v, a, b, beta, vc):
    v0 = 1.3e9
    x = v / v0
    xc = v / vc
    return b * x**a * np.exp( a / beta * xc**(-beta) )