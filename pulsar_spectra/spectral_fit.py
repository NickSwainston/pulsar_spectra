"""
Function used to fit different spectral models to the flux densities of pulsars
"""

import numpy as np
from iminuit import Minuit
from iminuit.cost import LeastSquares
from iminuit.util import propagate

import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from cycler import cycler

from pulsar_spectra.models import simple_power_law, broken_power_law, log_parabolic_spectrum, \
                                  high_frequency_cut_off_power_law, low_frequency_turn_over_power_law, \
                                  double_broken_power_law

import logging
logger = logging.getLogger(__name__)

def robust_cost_function(f_y, y, sigma_y, k=1.345):
    beta_array = []
    for fi, yi, sigma_i in zip(f_y, y, sigma_y):
        relative_error = (fi - yi)/sigma_i
        if abs(relative_error) < k:
            beta_array.append( 1./2. * relative_error**2 )
        else:
            beta_array.append( k * abs(relative_error) - 1./2. * k**2 )
    return sum(beta_array)


def plot_fit(freq, flux, flux_err, model, iminuit_result, fit_info,
             save_name="fit.png", plot_error=True, data_dict=None):
    fitted_freq = np.logspace(np.log10(min(freq)), np.log10(max(freq)), 100) / 1e6 # Convert to MHz
    if iminuit_result.valid:
        fitted_flux, fitted_flux_cov = propagate(lambda p: model(fitted_freq * 1e6, *p) * 1e3, iminuit_result.values, iminuit_result.covariance)
    else:
        # No convariance values so use old method
        fitted_flux = model(fitted_freq * 1e6, *iminuit_result.values) * 1e3
    fig, ax = plt.subplots()
    marker_scale = 0.7
    capsize = 1.5
    errorbar_linewidth = 0.7
    marker_border_thickness = 0.5
    custom_cycler = (cycler(color = ["#006ddb","#24ff24",'r',"#920000","#6db6ff","#ff6db6",'m',"#b6dbff","#db6d00","#b66dff","#009292","#490092","#ffb6db","#004949",'k']) 
                    + cycler(marker = [            'o', '^', 'D', 's', 'p', '*', 'v', 'd', 'P','h', '>', 'H', 'X', '<', 'x'])
                    + cycler(markersize = np.array([6,   7,   5,   5.5, 6.5, 9,   7,   7,   7.5,  7,   7,   7,   7.5,   7,   7])*marker_scale))
    ax.set_prop_cycle(custom_cycler)
    if data_dict:
        for ref in data_dict.keys():
            freq_all = np.array(data_dict[ref]['Frequency MHz'])
            flux_all = np.array(data_dict[ref]['Flux Density mJy'])
            flux_err_all = np.array(data_dict[ref]['Flux Density error mJy'])
            plt.errorbar(freq_all, flux_all, yerr=flux_err_all, linestyle='None', mec='k', markeredgewidth=marker_border_thickness, elinewidth=errorbar_linewidth, capsize=capsize, label=ref)
    else:
        plt.errorbar(np.array(freq), flux, yerr=flux_err, fmt='o', label="Input data", color="orange")
    plt.plot(fitted_freq, fitted_flux, 'k--', label=fit_info) # Modelled line
    if plot_error and iminuit_result.valid:
        # draw 1 sigma error band
        fitted_flux_prop = np.diag(fitted_flux_cov) ** 0.5
        plt.fill_between(fitted_freq, fitted_flux - fitted_flux_prop, fitted_flux + fitted_flux_prop, facecolor="C1", alpha=0.5)
    plt.xscale('log')
    plt.yscale('log')
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    ax.get_yaxis().set_major_formatter(ScalarFormatter())
    ax.tick_params(which='both', direction='in', top=1, right=1)
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Flux (mJy)')
    plt.legend(loc='center left', bbox_to_anchor=(1.1, 0.5))
    plt.savefig(save_name, bbox_inches='tight', dpi=200)
    plt.clf()

    
def iminuit_fit_spectral_model(freq, flux, flux_err, model=simple_power_law,
                               plot=False, plot_error=True,
                               save_name="fit.png", data_dict=None):
    # Model dependent defaults
    if model == simple_power_law:
        # a, b
        start_params = (-1.6, 0.003)
        mod_limits = [(None, 0), (0, None)]
    elif model == broken_power_law:
        # a1, a2, b, vb
        start_params = (-2.6, -2.6, 0.1, 5e8)
        mod_limits = [(None, 0), (None, 0), (0, None), (1e3, 1e9)]
    elif model == double_broken_power_law:
        # a1, a2, a3, b, vb1, vb2
        start_params = (-2.6, -2.6, -2.6, 0.1, 5e8, 5e8)
        mod_limits = [(None, 0), (None, 0), (None, 0), (0, None), (1e3, 1e9), (1e3, 1e9)]
    elif model == log_parabolic_spectrum:
        # a, b, c
        start_params = (-1.6, 1., 1.)
        mod_limits = [(-5, 2), (-5, 2), (None, None)]
    elif model == high_frequency_cut_off_power_law:
        # a, b, vc
        start_params = (-1.6, 1., 4e9)
        mod_limits = [(None, 0), (0, None), (3e9, 1e12)]
    elif model == low_frequency_turn_over_power_law:
        # a, b, beta, vc
        start_params = (-2.5, 1.e1, 1., 100e6)
        #mod_limits = [(None, 0), (0, None) , (1e-3, 2.1), (1e6, 1e9)]
        #mod_limits = [(-10, -0.1), (0, 100) , (.1, 2.1), (10e6, 500e6)]
        mod_limits = [(-5, -.5), (0, 100) , (.1, 2.1), (10e6, 500e6)]
        #-3.4, 1e-2, .5, 53e6
    model_str = str(model).split(" ")[1]
    k = len(start_params) # number of model parameters

    # Check if enough inputs
    if len(freq) <= k + 1:
        logger.warn(f"Only {len(freq)} supplied for {model_str} model fit. This is not enough so skipping")
        return 1e9, None, None

    # Fit model
    least_squares = LeastSquares(np.array(freq,     dtype=np.float128),
                                 np.array(flux,     dtype=np.float128),
                                 np.array(flux_err, dtype=np.float128),
                                 model)
    least_squares.loss = "soft_l1"
    m = Minuit(least_squares, *start_params)
    m.limits = mod_limits
    m.migrad()  # finds minimum of least_squares function
    if not m.valid:
        # Failed so try simplix method
        m.simplex()
        m.migrad()
    if not m.valid:
        # Use scan
        m.scan(ncall=500)
    m.hesse()   # accurately computes uncertainties
    logger.debug(m)

    # display legend with some fit info
    fit_info = [model_str]
    for p, v, e in zip(m.parameters, m.values, m.errors):
        fit_info.append(f"{p} = ${v:.5f} \\pm {e:.5}$")
    fit_info = "\n".join(fit_info)

    # Calculate AIC
    beta = robust_cost_function(model(np.array(freq), *m.values), flux, flux_err)
    aic = 2*beta * 2*k + (2*k*(k+1)) / (len(freq) - k -1)

    if plot:
        plot_fit(freq, flux, flux_err, model, m, fit_info,
                 save_name=save_name, data_dict=data_dict, plot_error=plot_error)
    return aic, m, fit_info


def find_best_spectral_fit(pulsar, freq_all, flux_all, flux_err_all,
                           plot_all=False, plot_best=False, plot_compare=False,
                           plot_error=True, data_dict=None):
    # Prepare plots and fitting frequencies
    if plot_compare:
        nrows = 5
        plot_size = 3
        fitted_freq = np.logspace(np.log10(min(freq_all)), np.log10(max(freq_all)), 100) / 1e6 # Convert to MHz
        fig, axs = plt.subplots(nrows, 1, figsize=(plot_size, plot_size * nrows))

    # loop over models and fit
    models = [
            [simple_power_law, "simple_power_law"],
            [broken_power_law, "broken_power_law"],
            [log_parabolic_spectrum, "log_parabolic_spectrum"],
            [high_frequency_cut_off_power_law, "high_frequency_cut_off_power_law"],
            [low_frequency_turn_over_power_law, "low_frequency_turn_over_power_law"],
            #[double_broken_power_law, "double_broken_power_law"],
            ]
    aics = []
    fit_results = []
    for i, model_pair in enumerate(models):
        model, label = model_pair
        #curve_fit_spectral_model(freq_all, flux_all, flux_err_all, model=model, plot=True, save_name=f"{pulsar}_{label}_fit.png")
        aic, iminuit_result, fit_info = iminuit_fit_spectral_model(freq_all, flux_all, flux_err_all,
                        model=model, plot=plot_all, plot_error=plot_error, save_name=f"{pulsar}_{label}_fit.png", data_dict=data_dict)
        logger.debug(f"{label} model fit gave AIC {aic}.")
        if iminuit_result is not None:
            aics.append(aic)
            fit_results.append([iminuit_result, fit_info])
        marker_scale = 0.7
        capsize = 1.5
        errorbar_linewidth = 0.7
        marker_border_thickness = 0.5
        custom_cycler = (cycler(color = ["#006ddb","#24ff24",'r',"#920000","#6db6ff","#ff6db6",'m',"#b6dbff","#db6d00","#b66dff","#009292","#490092","#ffb6db","#004949",'k']) 
                       + cycler(marker = [            'o', '^', 'D', 's', 'p', '*', 'v', 'd', 'P','h', '>', 'H', 'X', '<', 'x'])
                       + cycler(markersize = np.array([6,   7,   5,   5.5, 6.5, 9,   7,   7,   7.5,  7,   7,   7,   7.5,   7,   7])*marker_scale))
        axs[i].set_prop_cycle(custom_cycler)
        # Add to comparison plot
        if plot_compare and iminuit_result is not None:
            if data_dict:
                for ref in data_dict.keys():
                    freq_ref = np.array(data_dict[ref]['Frequency MHz'])
                    flux_ref = np.array(data_dict[ref]['Flux Density mJy'])
                    flux_err_ref = np.array(data_dict[ref]['Flux Density error mJy'])
                    (_, caps, _) = axs[i].errorbar(freq_ref, flux_ref, yerr=flux_err_ref, linestyle='None', mec='k', markeredgewidth=marker_border_thickness, elinewidth=errorbar_linewidth, capsize=capsize, label=ref)
                    for cap in caps:
                        cap.set_markeredgewidth(errorbar_linewidth)
            else:
                axs[i].errorbar(np.array(freq), flux, yerr=flux_err, fmt='o', label="Input data", color="orange")
            if iminuit_result.valid:
                fitted_flux, fitted_flux_cov = propagate(lambda p: model(fitted_freq * 1e6, *p) * 1e3, iminuit_result.values, iminuit_result.covariance)
            else:
                # No convariance values so use old method
                fitted_flux = model(fitted_freq * 1e6, *iminuit_result.values) * 1e3
            axs[i].plot(fitted_freq, fitted_flux, 'k--', label=fit_info + f"\nAIC: {aic}") # Modelled line
            if plot_error and iminuit_result.valid:
                # draw 1 sigma error band
                fitted_flux_prop = np.diag(fitted_flux_cov) ** 0.5
                axs[i].fill_between(fitted_freq, fitted_flux - fitted_flux_prop, fitted_flux + fitted_flux_prop, facecolor="C1", alpha=0.5)
            axs[i].set_xscale('log')
            axs[i].set_yscale('log')
            axs[i].get_xaxis().set_major_formatter(ScalarFormatter())
            axs[i].get_yaxis().set_major_formatter(ScalarFormatter())
            axs[i].tick_params(which='both', direction='in', top=1, right=1)
            axs[i].set_xlabel('Frequency (MHz)')
            axs[i].set_ylabel('Flux (mJy)')
            axs[i].legend(loc='center left', bbox_to_anchor=(1.1, 0.5), fontsize=6)

    # Return best result
    if len(aics) == 0:
        logger.info(f"No model found for {pulsar}")
        return ["no_fit", "no_fit"], [None, None, None]
    else:
        aici = aics.index(min(aics))
        logger.info(f"Best model for {pulsar} is {models[aici][1]}")
        if plot_compare:
            # highlight best fit
            rect = plt.Rectangle(
                # (lower-left corner), width, height
                (-0.4, -0.13), 2.4, 1.2, fill=False, color="k", lw=2, 
                zorder=1000, transform=axs[aici].transAxes, figure=fig
            )
            fig.patches.extend([rect])
            plt.savefig(f"{pulsar}_comparison_fit.png", bbox_inches='tight', dpi=300)
            plt.clf()
        elif plot_best:
            plot_fit(freq_all, flux_all, flux_err_all, models[aici][0], fit_results[aici][0], fit_results[aici][1],
                     save_name=f"{pulsar}_{models[aici][1]}_fit.png", plot_error=plot_error, data_dict=data_dict)
        return models[aici], fit_results[aici]