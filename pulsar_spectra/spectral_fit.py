"""
Function used to fit different spectral models to the fluxs_mJy densities of pulsars
"""

import numpy as np
from iminuit import Minuit
from iminuit.cost import LeastSquares
from iminuit.util import propagate

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from cycler import cycler

from pulsar_spectra.models import simple_power_law, broken_power_law, log_parabolic_spectrum, \
                                  high_frequency_cut_off_power_law, low_frequency_turn_over_power_law, \
                                  double_broken_power_law
from pulsar_spectra.catalogues import convert_cat_list_to_dict

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

def huber_loss_function(sq_resi, k=1.345):
    single_value = False
    if isinstance(sq_resi, float) or isinstance(sq_resi, int) or isinstance(sq_resi, np.float128): 
        sq_resi = np.array([sq_resi])
        single_value = True
    elif isinstance(sq_resi, list):
        sq_resi = np.array(sq_resi)
    rho = []
    residual = np.sqrt(abs(sq_resi))
    for j in range(len(residual)):
        if residual[j] < k:
            rho.append( sq_resi[j]/2 )
        else:
            rho.append( k * residual[j] - 1./2. * k**2 )
    if single_value:
        return rho[0]
    else:
        return rho

def plot_fit(freqs_MHz, fluxs_mJy, flux_errs_mJy, ref, model, iminuit_result, fit_info,
             plot_error=True, save_name="fit.png", alternate_style=False, axis=None,
             secondary_fit=False, fit_range=None):
    """Create a plot of the pulsar spectral fit.

    Parameters
    ----------
    freqs_MHz : `list`
        A list of the frequencies in MHz.
    fluxs_mJy : `list`
        A list of the flux density in mJy.
    flux_errs_mJy : `list`
        A list of the uncertainty of the flux density in mJy.
    ref : `list`
        A list of the reference label (in the format 'Author_year').
    model : `function`
        One of the model functions from :py:meth:`pulsar_spectra.models`.
    iminuit_result : `iminuit.Minuit`
        The Minuit class after being fit in :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.
    fit_info : `str`
        The string to label the fit with from :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.
    plot_error : `boolean`, optional
        If you want to include the fit error in the plot. |br| Default: True.
    save_name : `str`, optional
        The name of the saved plot. |br| Default: "fit.png".
    alternate_style : `boolean`, optional
        Plot with the alternate plot style based on Jankowski 2018. |br| Default: False.
    axis : `Axes`, optional
        The axes with which the spectrum will be plotted. |br| None.
    secondary_fit : `boolean`, optional
        Plot model with an alternate style and without markers. |br| Default: False.
    fit_range : `tuple`, optional
        Frequency range to plot the second model over. |br| Default: None.
    """
    # Set up plot
    plotsize = 3.2

    if axis==None:
        make_plot=True
        fig, ax = plt.subplots(figsize=(plotsize*4/3, plotsize))
    else:
        make_plot=False
        ax = axis
    marker_scale = 0.7
    capsize = 1.5
    errorbar_linewidth = 0.7
    marker_border_thickness = 0.5
    custom_cycler = (cycler(color = ["#006ddb", "#24ff24",'r',"#920000","#6db6ff","#ff6db6",'m',"#b6dbff","#009292","#b66dff","#db6d00", 'c',"#ffb6db","#004949",'k','y','#009292', 'k'])
                    + cycler(marker = [            'o', '^', 'D', 's', 'p', '*', 'v', 'd', 'P',  'h', '>', 'H', 'X', '<', 'x', 's', '^', 'd'])
                    + cycler(markersize = np.array([6,   7,   5,   5.5, 6.5, 9,   7,   7,   7.5,  7,   7,   7,   7.5,   7,   7, 5.5, 7,   7])*marker_scale))
    ax.set_prop_cycle(custom_cycler)

    # Add data
    data_dict = convert_cat_list_to_dict({"dummy_pulsar":[freqs_MHz, fluxs_mJy, flux_errs_mJy, ref]})["dummy_pulsar"]
    if not secondary_fit:
        for ref in data_dict.keys():
            freqs_ref = np.array(data_dict[ref]['Frequency MHz'])
            fluxs_ref = np.array(data_dict[ref]['Flux Density mJy'])
            flux_errs_ref = np.array(data_dict[ref]['Flux Density error mJy'])
            (_, caps, _) = ax.errorbar(freqs_ref, fluxs_ref, yerr=flux_errs_ref, linestyle='None', mec='k', markeredgewidth=marker_border_thickness, elinewidth=errorbar_linewidth, capsize=capsize, label=ref.replace('_',' '))
            for cap in caps:
                cap.set_markeredgewidth(errorbar_linewidth)

    # Create fit line
    if secondary_fit:
        if fit_range==None:
            fitted_freq = np.logspace(np.log10(min(freqs_MHz)), np.log10(max(freqs_MHz)), 100)
        else:
            fitted_freq = np.logspace(*fit_range, 100)
    else:
        fitted_freq = np.logspace(np.log10(min(freqs_MHz)), np.log10(max(freqs_MHz)), 100)
    if iminuit_result.valid:
        fitted_flux, fitted_flux_cov = propagate(lambda p: model(fitted_freq * 1e6, *p) * 1e3, iminuit_result.values, iminuit_result.covariance)
    else:
        # No convariance values so use old method
        fitted_flux = model(fitted_freq * 1e6, *iminuit_result.values) * 1e3
    # Plot fit line
    if alternate_style:
        if fit_info.split()[0]=="simple_power_law":
            model_label="simple pl"
        elif fit_info.split()[0]=="broken_power_law":
            model_label="broken pl"
        elif fit_info.split()[0]=="log_parabolic_spectrum":
            model_label="lps"
        elif fit_info.split()[0]=="high_frequency_cut_off_power_law":
            model_label="pl high cut-off"
        elif fit_info.split()[0]=="low_frequency_turn_over_power_law":
            model_label="pl low turn-over"
        else:
            model_label=fit_info.split()[0]
        if secondary_fit:
            ax.plot(fitted_freq, fitted_flux, 'k', marker="None", ls=(0, (0.7, 1)), lw=2, alpha=0.5, label=model_label)
        else:
            ax.plot(fitted_freq, fitted_flux, 'k--', label=model_label)
    else:
        if secondary_fit:
            ax.plot(fitted_freq, fitted_flux, 'k', marker="None", ls=(0, (0.7, 1)), lw=2, alpha=0.5, label=fit_info)
        else:
            ax.plot(fitted_freq, fitted_flux, 'k--', label=fit_info)

    if plot_error and iminuit_result.valid:
        # draw 1 sigma error band
        fitted_flux_prop = np.diag(fitted_flux_cov) ** 0.5
        if secondary_fit:
            ax.fill_between(fitted_freq, fitted_flux - fitted_flux_prop, fitted_flux + fitted_flux_prop, facecolor="r", alpha=0)
        else:
            ax.fill_between(fitted_freq, fitted_flux - fitted_flux_prop, fitted_flux + fitted_flux_prop, facecolor="C1", alpha=0.5)

    # Format plot and save
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.get_xaxis().set_major_formatter(FormatStrFormatter('%g'))
    ax.get_yaxis().set_major_formatter(FormatStrFormatter('%g'))
    ax.tick_params(which='both', direction='in', top=1, right=1)
    ax.set_xlabel('Frequency (MHz)')
    ax.set_ylabel('Flux Density (mJy)')
    if alternate_style:
        ax.legend(loc='lower left', ncol=2, fontsize=6)
    else:
        ax.legend(loc='center left', bbox_to_anchor=(1.1, 0.5))
    ax.grid(visible=True, ls=':', lw=0.6)
    if make_plot:
        plt.savefig(save_name, bbox_inches='tight', dpi=300)
        plt.clf()


def iminuit_fit_spectral_model(freqs_MHz, fluxs_mJy, flux_errs_mJy, ref, model=simple_power_law,
                               plot=False, plot_error=True, save_name="fit.png",
                               alternate_style=False, axis=None, secondary_fit=False,
                               fit_range=None):
    """Fit pulsar spectra with iminuit.

    Parameters
    ----------
    freqs_MHz : `list`
        A list of the frequencies in MHz.
    fluxs_mJy : `list`
        A list of the flux density in mJy.
    flux_errs_mJy : `list`
        A list of the uncertainty of the flux density in mJy.
    ref : `list`
        A list of the reference label (in the format 'Author_year').
    model : `function`, optional
        One of the model functions from :py:meth:`pulsar_spectra.models`. Default: :py:meth:`pulsar_spectra.models.simple_power_law`.
    plot : `boolean`, optional
        If you want to plot the result of the fit. |br| Default: False.
    plot_error : `boolean`, optional
        If you want to include the fit error in the plot. |br| Default: True.
    save_name : `str`, optional
        The name of the saved plot. |br| Default: "fit.png".
    alternate_style : `boolean`, optional
        If you want to use the alternate plot style. |br| Default: False.
    axis : `Axes`, optional
        The axes with which the spectrum will be plotted. |br| None.
    secondary_fit : `boolean`, optional
        Plot model with an alternate style and without markers. |br| Default: False.
    fit_range : `tuple`, optional
        Frequency range to plot the second model over. |br| Default: None.

    Returns
    -------
    aic : `float`
        The Akaike information criterion of the fit.
    m : `iminuit.Minuit`
        The Minuit class after being fit in :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.
    fit_info : `str`
        The string to label the fit with from :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.
    """
    # Covert to SI (Hz and Jy)
    freqs_Hz     = np.array(freqs_MHz,     dtype=np.float128) * 1e6
    fluxs_Jy     = np.array(fluxs_mJy,     dtype=np.float128) / 1e3
    flux_errs_Jy = np.array(flux_errs_mJy, dtype=np.float128) / 1e3

    # Model dependent defaults
    if model == simple_power_law:
        # a, b
        start_params = (-1.6, 0.003)
        mod_limits = [(None, 0), (0, None)]
    elif model == broken_power_law:
        # vb, a1, a2, b
        start_params = (5e8, -1.6, -1.6, 0.1)
        mod_limits = [(min(freqs_Hz)+1e8, max(freqs_Hz)-1e8), (-10, 10), (-10, 0), (0, None)]
    elif model == double_broken_power_law:
        # vb1, vb2, a1, a2, a3, b
        start_params = (5e8, 5e8, -2.6, -2.6, -2.6, 0.1)
        mod_limits = [(1e3, 1e9), (1e3, 1e9), (None, 0), (None, 0), (None, 0), (0, None)]
    elif model == log_parabolic_spectrum:
        # a, b, c
        start_params = (-1.6, 1., 1.)
        mod_limits = [(-5, 2), (-5, 2), (None, None)]
    elif model == high_frequency_cut_off_power_law:
        # vc, a, b
        start_params = (4e9, -1.6, 1.)
        mod_limits = [(3e9, 1e12), (None, 0), (0, None)]
    elif model == low_frequency_turn_over_power_law:
        # vc, a, b, beta
        start_params = (100e6, -2.5, 1.e1, 1.)
        mod_limits = [(10e6, 500e6), (-5, -.5), (0, 100) , (.1, 2.1)]

    # Check if enough inputs
    model_str = str(model).split(" ")[1]
    k = len(start_params) # number of model parameters
    if len(freqs_MHz) <= k + 1:
        logger.warn(f"Only {len(freqs_MHz)} supplied for {model_str} model fit. This is not enough so skipping")
        return 1e9, None, None

    # Fit model
    least_squares = LeastSquares(freqs_Hz, fluxs_Jy, flux_errs_Jy, model)
    least_squares.loss = huber_loss_function
    m = Minuit(least_squares, *start_params)
    m.tol=0.01
    m.limits = mod_limits
    m.scan(ncall=500)
    m.migrad(ncall=300)  # finds minimum of least_squares function
    if not m.valid:
        # Failed so try simplix method
        m.simplex(ncall=300)
        m.migrad(ncall=300)
    if not m.valid:
        # Use scan
        m.migrad(ncall=500)
    m.hesse()   # accurately computes uncertainties
    logger.debug(m)

    # display legend with some fit info
    fit_info = [model_str]
    for p, v, e in zip(m.parameters, m.values, m.errors):
        if p.startswith("v"):
            fit_info.append(f"{p} = ${v/1e6:8.1f} \\pm {e/1e6:8.1}$ MHz")
        else:
            fit_info.append(f"{p} = ${v:.5f} \\pm {e:.5}$")
    fit_info = "\n".join(fit_info)

    # Calculate AIC
    beta = robust_cost_function(model(freqs_Hz, *m.values), fluxs_Jy, flux_errs_Jy)
    aic = 2*beta + 2*k + (2*k*(k+1)) / (len(freqs_Hz) - k -1)

    if plot:
        plot_fit(freqs_MHz, fluxs_mJy, flux_errs_mJy, ref, model, m, fit_info,
                save_name=save_name, plot_error=plot_error,
                alternate_style=alternate_style, axis=axis,
                secondary_fit=secondary_fit, fit_range=fit_range)

    return aic, m, fit_info


def find_best_spectral_fit(pulsar, freqs_MHz, fluxs_mJy, flux_errs_mJy, ref_all,
                           plot_all=False, plot_best=False, plot_compare=False,
                           plot_error=True, alternate_style=False, axis=None,
                           secondary_fit=False, fit_range=None):
    """Fit pulsar spectra with iminuit.

    Parameters
    ----------
    pulsar : `str`
        The Jname of the pulsar to be fit.
    freqs_MHz : `list`
        A list of the frequencies in MHz.
    fluxs_mJy : `list`
        A list of the flux density in mJy.
    flux_errs_mJy : `list`
        A list of the uncertainty of the flux density in mJy.
    ref_all : `list`
        A list of the reference label (in the format 'Author_year').
    plot_all : `boolean`, optional
        If you want to plot the result of all fits. |br| Default: False.
    plot_best : `boolean`, optional
        If you want to only plot the best fit. |br| Default: False.
    plot_compare : `boolean`, optional
        If you want to make a single plot with the result of all fits. |br| Default: False.
    plot_error : `boolean`, optional
        If you want to include the fit error in the plot. |br| Default: True.
    alternate_style : `boolean`, optional
        Plot with the alternate plot style based on Jankowski 2018. |br| Default: False.
    axis : `Axes`, optional
        The axes with which the spectrum will be plotted. |br| Default: None.
    secondary_fit : `boolean`, optional
        Plot model with an alternate style and without markers. Does not work for comparison plots. |br| Default: False.
    fit_range : `tuple`, optional
        Frequency range to plot the second model over. |br| Default: None.

    Returns
    -------
    model : `function`
        The best model functions from :py:meth:`pulsar_spectra.models`. Default: :py:meth:`pulsar_spectra.models.simple_power_law`.
    m : `iminuit.Minuit`
        The Minuit class after being fit in :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.
    fit_info : `str`
        The string to label the fit with from :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.
    """
    # Prepare plots and fitting frequencies
    if plot_compare:
        # Set up plots
        nrows = 5
        plot_size = 3
        fitted_freqs_MHz = np.logspace(np.log10(min(freqs_MHz)), np.log10(max(freqs_MHz)), 100)
        fig, axs = plt.subplots(nrows, 1, figsize=(plot_size, plot_size * nrows))
        marker_scale = 0.6
        capsize = 1.5
        errorbar_linewidth = 0.7
        marker_border_thickness = 0.5
        for i in range(nrows):
            # Create cycler
            custom_cycler = (cycler(color = ["#006ddb", "#24ff24",'r',"#920000","#6db6ff","#ff6db6",'m',"#b6dbff","#009292","#b66dff","#db6d00", 'c',"#ffb6db","#004949",'k','y','#009292', 'k'])
                            + cycler(marker = [            'o', '^', 'D', 's', 'p', '*', 'v', 'd', 'P',  'h', '>', 'H', 'X', '<', 'x', 's', '^', 'd'])
                            + cycler(markersize = np.array([6,   7,   5,   5.5, 6.5, 9,   7,   7,   7.5,  7,   7,   7,   7.5,   7,   7, 5.5, 7,   7])*marker_scale))
            axs[i].set_prop_cycle(custom_cycler)

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
    iminuit_results = []
    fit_infos = []
    model_i = []
    for i, model_pair in enumerate(models):
        model, label = model_pair
        aic, iminuit_result, fit_info = iminuit_fit_spectral_model(freqs_MHz, fluxs_mJy, flux_errs_mJy, ref_all,
                        model=model, plot=plot_all, plot_error=plot_error, save_name=f"{pulsar}_{label}_fit.png",
                        alternate_style=alternate_style, axis=axis, secondary_fit=secondary_fit)
        logger.debug(f"{label} model fit gave AIC {aic}.")
        if iminuit_result is not None:
            aics.append(aic)
            iminuit_results.append(iminuit_result)
            fit_infos.append(fit_info)
            model_i.append(i)

        # Add to comparison plot
        if plot_compare and iminuit_result is not None:
            # plot data
            data_dict = convert_cat_list_to_dict({"dummy_pulsar":[freqs_MHz, fluxs_mJy, flux_errs_mJy, ref_all]})["dummy_pulsar"]
            for ref in data_dict.keys():
                freq_ref = np.array(data_dict[ref]['Frequency MHz'])
                flux_ref = np.array(data_dict[ref]['Flux Density mJy'])
                flux_err_ref = np.array(data_dict[ref]['Flux Density error mJy'])
                (_, caps, _) = axs[i].errorbar(freq_ref, flux_ref, yerr=flux_err_ref, linestyle='None', mec='k', markeredgewidth=marker_border_thickness, elinewidth=errorbar_linewidth, capsize=capsize, label=ref.replace('_', ' '))
                for cap in caps:
                    cap.set_markeredgewidth(errorbar_linewidth)
            # plot fit
            if iminuit_result.valid:
                fitted_flux, fitted_flux_cov = propagate(lambda p: model(fitted_freqs_MHz * 1e6, *p) * 1e3, iminuit_result.values, iminuit_result.covariance)
            else:
                # No convariance values so use old method
                fitted_flux = model(fitted_freqs_MHz * 1e6, *iminuit_result.values) * 1e3
            axs[i].plot(fitted_freqs_MHz, fitted_flux, 'k--', label=fit_info + f"\nAIC: {aic}") # Modelled line
            if plot_error and iminuit_result.valid:
                # draw 1 sigma error band
                fitted_flux_prop = np.diag(fitted_flux_cov) ** 0.5
                axs[i].fill_between(fitted_freqs_MHz, fitted_flux - fitted_flux_prop, fitted_flux + fitted_flux_prop, facecolor="C1", alpha=0.5)

            axs[i].set_xscale('log')
            axs[i].set_yscale('log')
            axs[i].get_xaxis().set_major_formatter(FormatStrFormatter('%g'))
            axs[i].get_yaxis().set_major_formatter(FormatStrFormatter('%g'))
            axs[i].tick_params(which='both', direction='in', top=1, right=1)
            axs[i].set_xlabel('Frequency (MHz)')
            axs[i].set_ylabel('Flux Density (mJy)')
            axs[i].legend(loc='center left', bbox_to_anchor=(1.1, 0.5), fontsize=6)


    # Return best result
    if len(aics) == 0:
        logger.info(f"No model found for {pulsar}")
        #models[aici], iminuit_results[aici], fit_infos[aici], p_best, p_category
        return None, None, None, None, None
    else:
        aici = aics.index(min(aics))

        logger.info(f"Best model for {pulsar} is {models[aici][1]}")

        # Calc probability of best fit
        li = []
        for i, _ in enumerate(aics):
            li.append(np.exp(-1/2 * np.abs(aics[i] - aics[aici])))
        p_best = 1 / np.sum(li)
        # Work out the catagory
        #TODO work out what the curvature paramter is and implimented it
        if p_best > 0.8:
            p_category = 'clear'
        elif p_best > 0.7:
            p_category = 'strong'
        elif p_best > 0.5:
            p_category = 'candidate'
        else:
            p_category = 'weak'

        # Perform plots
        if plot_compare:
            # highlight best fit
            rect = plt.Rectangle(
                # (lower-left corner), width, height
                (-0.4, -0.13), 2.4, 1.2, fill=False, color="k", lw=2,
                zorder=1000, transform=axs[model_i[aici]].transAxes, figure=fig
            )
            fig.patches.extend([rect])
            plt.savefig(f"{pulsar}_comparison_fit.png", bbox_inches='tight', dpi=300)
            plt.clf()
        if plot_best:
            plot_fit(freqs_MHz, fluxs_mJy, flux_errs_mJy, ref_all, models[model_i[aici]][0], iminuit_results[aici], fit_infos[aici],
                    save_name=f"{pulsar}_{models[model_i[aici]][1]}_fit.png", plot_error=plot_error, alternate_style=alternate_style,
                    axis=axis, secondary_fit=secondary_fit, fit_range=fit_range)
        return models[model_i[aici]], iminuit_results[aici], fit_infos[aici], p_best, p_category


def estimate_flux_density(
    est_freq,
    model,
    iminuit_result,
):
    """Estimate a pulsar's flux density using a previous spectra fit.

    Parameters
    ----------
    est_freq : `float` or `list`
        A single or list of frequencies to estimate flux at (in MHz).
    model : `function`
        The pulsar spectra model function from :py:meth:`pulsar_spectra.models`.
    m : `iminuit.Minuit`
        The Minuit class after being fit in :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.

    Returns
    -------
    fitted_flux : `float` or `list`
        The estimated flux density of the pulsar at the input frequencies.
    fitted_flux_err : `float` or `list`
        The estimated flux density errors of the pulsar at the input frequencies.
    """
    # make sure est_freq is a numpy array
    single_value = False
    if isinstance(est_freq, float) or isinstance(est_freq, int):
        est_freq = np.array([est_freq])
        single_value = True
    elif isinstance(est_freq, list):
        est_freq = np.array(est_freq)

    if iminuit_result.valid:
        fitted_flux, fitted_flux_cov = propagate(lambda p: model(est_freq * 1e6, *p) * 1e3, iminuit_result.values, iminuit_result.covariance)
        fitted_flux_err = np.diag(fitted_flux_cov) ** 0.5
    else:
        # No convariance values so use old method
        fitted_flux = model(est_freq * 1e6, *iminuit_result.values) * 1e3
        fitted_flux_err = [None]*len(fitted_flux)

    if single_value:
        return fitted_flux[0], fitted_flux_err[0]
    else:
        return fitted_flux, fitted_flux_err