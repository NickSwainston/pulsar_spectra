import numpy as np
from math import pi
from psrqpy import QueryATNF

from pulsar_spectra.catalogue import ATNF_VER

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

def calc_high_frequency_cutoff_emission_height(psrname, v_c, u_v_c, z_surf=12, u_z_surf=2):
    """Calculate emission height and magetic field strengths using high-frequency cut-off model (:py:meth:`pulsar_spectra.models.high_frequency_cut_off_power_law`).
    Details on the calculation procedure can be found in Jankowski et al. (2018) and Lee et al. (2022). The default neutron star radius is based on a canonical
    1.4 solar mass neutron star as per Steiner et al. (2018).

    Parameters
    ----------
    psrname : `string`
        Pulsar name.
    v_c : `float`
        Cut-off frequency in units of Hz.
    u_v_c : `float`
        Uncertainty in cut-off frequency in units of Hz.
    z_surf : `float`, optional
        Radius of the neutron star in km. |br| Default: 12.
    u_z_surf : `float`, optional
        Uncertainty on the radius of the neutron star in km. |br| Default: 2.

    Returns
    -------
    B_pc : `float`
        Magnetic field strength at the centre of the polar cap in units of Gauss.
    u_B_pc : `float`
        Uncertainty of B_pc in Gauss.
    B_surf : `float`
        Magnetic field strength at the neutron star surface.
    B_lc : `float`
        Magnetic field strength at the light cylinder radius in Gauss.
    r_lc : `float`
        Light cylinder radius in km.
    z_e : `float`
        Estimated emission height (i.e. the altitude of the centre of the polar cap) in km.
    u_z_e : `float`
        Uncertainty of z_e in km.
    z_percent : `float`
        Estimated emission height as a percentage of light-cylinder radius.
    u_z_percent : `float`
        Uncertainty of z_percent as a percentage of light-cylinder radius.
    """
    m_e = 9.1094e-28 # electron mass (g)
    c0 = 2.99792458e10 # speed of light (cm s^{-1})
    e = 4.8032e-10 # electron charge (cm^{3/2} g^{1/2} s^{-1})
    c_lc = 4.77e4 # light cylinder calculation constant (km s^{-1})
    c_B = m_e*c0/(pi*e) # magnetic field calculation constant

    query = QueryATNF(params=["P0", "BSurf", "B_LC"], psrs=[psrname], version=ATNF_VER)
    psrs = query.get_pulsars()

    P = psrs[psrname].P0
    B_surf = psrs[psrname].BSurf
    B_lc = psrs[psrname].B_LC

    B_pc = c_B*P*v_c**2
    u_B_pc = 2*c_B*P*v_c*u_v_c

    z_e = z_surf*(B_pc/B_surf)**(-1/3)
    u_z_e = (B_pc/B_surf)**(-1/3) * np.sqrt(u_z_surf**2 + (u_B_pc*z_surf/(3*B_pc))**2)

    r_lc = c_lc*P

    z_percent = z_e/r_lc*100
    u_z_percent = u_z_e*100/r_lc

    return B_pc, u_B_pc, B_surf, B_lc, r_lc, z_e, u_z_e, z_percent, u_z_percent