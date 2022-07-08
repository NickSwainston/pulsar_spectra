import numpy as np

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