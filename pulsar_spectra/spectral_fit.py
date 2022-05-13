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

from pulsar_spectra.models import model_settings
from pulsar_spectra.catalogue import convert_cat_list_to_dict

import logging
logger = logging.getLogger(__name__)

def robust_cost_function(f_y, y, sigma_y, k=1.345):
    """Robust cost function. The negative log-likelihood of a Gaussian likelihood with Huber loss.
    
    Parameters
    ----------
    f_y : `list`
        A list of predicted values according to the model.
    y : `list`
        A list of measured values at the same frequency as the model values.
    sigma_y : `list`
        A list of uncertainties corresponding to the measured values y.
    k : `float`, optional
        A constant that defines at which distance the loss function starts to penalize outliers. |br| Default: 1.345.

    Returns
    -------
    beta : `float`
        The cost of the model fit.
    """
    beta_array = []
    for fi, yi, sigma_i in zip(f_y, y, sigma_y):
        relative_error = (fi - yi)/sigma_i
        if abs(relative_error) < k:
            beta_array.append( 1./2. * relative_error**2 )
        else:
            beta_array.append( k * abs(relative_error) - 1./2. * k**2 )
    return sum(beta_array)

def huber_loss_function(sq_resi, k=1.345):
    """Robust loss function which penalises outliers, as detailed in Jankowski et al (2018).

    Parameters
    ----------
    sq_resi : `float` or `list`
        A single or list of the squared residuals.
    k : `float`, optional
        A constant that defines at which distance the loss function starts to penalize outliers. |br| Default: 1.345.

    Returns
    -------
    rho : `float` or `list`
       The modified squared residuals.
    """
    single_value = False
    if isinstance(sq_resi, float) or isinstance(sq_resi, int):
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
    fit_range : `tuple`, (`float`, `float`) optional
        Frequency range to plot the second model over in MHz, eg. (100, 3000). |br| Default: None, will use input frequency range.
    """
    # Set up plot
    plotsize = 3.2

    if axis is None:
        fig, ax = plt.subplots(figsize=(plotsize*4/3, plotsize))
    else:
        ax = axis
    capsize = 1.5
    errorbar_linewidth = 0.7
    marker_border_thickness = 0.5
    marker_scale = 0.7
    marker_types = [("#006ddb", "o", 6),    # blue circle
                    ("#24ff24", "^", 7),    # green triangle
                    ("r",       "D", 5),    # red diamond
                    ("#920000", "s", 5.5),  # maroon square
                    ("#6db6ff", "p", 6.5),  # sky blue pentagon
                    ("#ff6db6", "*", 9),    # pink star
                    ("m",       "v", 7),    # purple upside-down triangle
                    ("#b6dbff", "d", 7),    # light blue thin diamond
                    ("#009292", "P", 7.5),  # turqoise thick plus
                    ("#b66dff", "h", 7),    # lavender hexagon
                    ("#db6d00", ">", 7),    # orange right-pointing triangle
                    ("c",       "H", 7),    # cyan sideways hexagon
                    ("#ffb6db", "X", 7.5),  # light pink thick cross
                    ("#004949", "<", 7),    # dark green right-pointing triangle
                    ("k",       "x", 7),    # black thin cross
                    ("y",       "s", 5.5),  # yellow square
                    ("#009292", "^", 7),    # turquoise triangle
                    ("k",       "d", 7),    # black thin diamond
                    ("#b6dbff", "*", 9),    # light blue star
                    ("y",       "P", 7.5)]  # yellow thick plus
    custom_cycler = (cycler(color = [p[0] for p in marker_types])
                    + cycler(marker = [p[1] for p in marker_types])
                    + cycler(markersize = np.array([p[2] for p in marker_types])*marker_scale))
    ax.set_prop_cycle(custom_cycler)

    # Add data
    data_dict = convert_cat_list_to_dict({"dummy_pulsar":[freqs_MHz, fluxs_mJy, flux_errs_mJy, ref]})["dummy_pulsar"]
    if not secondary_fit:
        for ref in data_dict.keys():
            freqs_ref = np.array(data_dict[ref]['Frequency MHz'])
            fluxs_ref = np.array(data_dict[ref]['Flux Density mJy'])
            flux_errs_ref = np.array(data_dict[ref]['Flux Density error mJy'])
            (_, caps, _) = ax.errorbar(
                freqs_ref,
                fluxs_ref,
                yerr=flux_errs_ref,
                linestyle='None',
                mec='k',
                markeredgewidth=marker_border_thickness,
                elinewidth=errorbar_linewidth,
                capsize=capsize,
                label=ref.replace('_',' ')
            )
            for cap in caps:
                cap.set_markeredgewidth(errorbar_linewidth)

    # Create fit line
    if fit_range is None:
        # No fit range given so use full range
        fitted_freq = np.logspace(np.log10(min(freqs_MHz)), np.log10(max(freqs_MHz)), 100)
    else:
        # Use input fit range
        min_freq, max_freq = fit_range
        fitted_freq = np.logspace(np.log10(min_freq), np.log10(max_freq), 100)
    if iminuit_result.valid:
        fitted_flux, fitted_flux_cov = propagate(lambda p: model(fitted_freq * 1e6, *p) * 1e3, iminuit_result.values, iminuit_result.covariance)
    else:
        # No convariance values so use old method
        fitted_flux = model(fitted_freq * 1e6, *iminuit_result.values) * 1e3

    # Plot fit line
    if alternate_style:
        # Just use a simple label
        model_dict = model_settings()
        fit_info = model_dict[fit_info.split()[0]][1]
    if secondary_fit:
        ax.plot(fitted_freq, fitted_flux, 'k', marker="None", ls=(0, (0.7, 1)), lw=2, alpha=0.5, label=fit_info)
    else:
        ax.plot(fitted_freq, fitted_flux, 'k--', label=fit_info)

    if plot_error and iminuit_result.valid:
        # draw 1 sigma error band
        fitted_flux_prop = np.diag(fitted_flux_cov) ** 0.5
        if secondary_fit:
            facecolor = "r"
            alpha = 0
        else:
            facecolor = "C1"
            alpha = 0.5
        ax.fill_between(fitted_freq, fitted_flux - fitted_flux_prop, fitted_flux + fitted_flux_prop, facecolor=facecolor, alpha=alpha)

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
    if axis is None:
        # Not using axis mode so save figure
        plt.savefig(save_name, bbox_inches='tight', dpi=300)
        plt.clf()


def iminuit_fit_spectral_model(
        freqs_MHz,
        fluxs_mJy,
        flux_errs_mJy,
        ref,
        model_name="simple_power_law",
        start_params=None,
        mod_limits=None,
        plot=False,
        plot_error=True,
        save_name="fit.png",
        alternate_style=False,
        axis=None,
        secondary_fit=False,
        fit_range=None
    ):
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
    model_name : `function`, optional
        One of the model names from :py:meth:`pulsar_spectra.models.model_settings`.
        Default: :py:meth:`pulsar_spectra.models.simple_power_law`.
    start_params : `tuple`, optional
        A tuple of the starting paramaters for each input to the model that iminuit will use as an initial estimate.
        If none provided, will use the defaults from :py:meth:`pulsar_spectra.models.model_settings`.
    mod_limits : `list` of `tuple`s, optional
        A list of tuples where each tuples is the minimum and maximum limits that will be applied to the model by iminuit.
        If none provided, will use the defaults from :py:meth:`pulsar_spectra.models.model_settings`.
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
    v0_Hz        = 10**((np.log10(min(freqs_MHz))+np.log10(max(freqs_MHz)))/2) * 1e6 # reference frequency is the logarithmic centre frequency
    freqs_Hz     = np.array(freqs_MHz,     dtype=np.float128) * 1e6
    fluxs_Jy     = np.array(fluxs_mJy,     dtype=np.float128) / 1e3
    flux_errs_Jy = np.array(flux_errs_mJy, dtype=np.float128) / 1e3

    # Load model settings
    model_dict = model_settings()
    model_function = model_dict[model_name][0]

    # Check for model dependent defaults
    if start_params is None:
        start_params = model_dict[model_name][2]
    if mod_limits is None:
        mod_limits = model_dict[model_name][3]
    # Add the reference frequency
    start_params += (v0_Hz,)
    mod_limits += [None]

    # Check if enough inputs
    k = len(start_params)-1 # number of free model parameters
    if len(freqs_MHz) <= k + 1:
        logger.warn(f"Only {len(freqs_MHz)} supplied for {model_name} model fit. This is not enough so skipping")
        return 1e9, None, None

    # Fit model
    least_squares = LeastSquares(freqs_Hz, fluxs_Jy, flux_errs_Jy, model_function)
    least_squares.loss = huber_loss_function
    m = Minuit(least_squares, *start_params)
    m.fixed["v0"] = True # fix the reference frequency

    """Find the minimum of least_squares function using the in-built minimisation
    algorithms in iminuit. If migrad by itself fails, then run the simplex
    minimiser before migrad. If simplex fails, run a grid scan over parameter
    space before migrad. Systematically increase the number of calls until
    a valid minimum is found.
    """
    m.tol=0.000005 # low tolerace improves likelihood of a sensible fit
    m.limits = mod_limits # limits are primarily to assist the scan minimiser
    migrad_calls = 20000 # more calls, better fit
    ncall = 20000 # for simplex and scan
    m.migrad(ncall=migrad_calls)
    if m.valid:
        logger.debug(f"Found for fit with {model_name} using migrad and {migrad_calls} calls.")
    else:
        m.simplex(ncall=ncall)
        m.migrad(ncall=migrad_calls)
        if m.valid:
            logger.debug(f"Found for fit with {model_name} using simplex and {ncall} calls.")
        else:
            m.scan(ncall=ncall)
            m.migrad(ncall=migrad_calls)
            if m.valid:
                logger.debug(f"Found for fit with {model_name} using scan and {ncall} calls.")
    if not m.valid:
        logger.warning(f"No valid minimum found for model {model_name}.")

    m.hesse() # accurately computes uncertainties
    logger.debug(m)

    # display legend with some fit info
    fit_info = [model_name]
    for p, v, e in zip(m.parameters, m.values, m.errors):
        if p.startswith("v"):
            fit_info.append(f"{p} = ${v/1e6:8.1f} \\pm {e/1e6:8.1}$ MHz")
        else:
            fit_info.append(f"{p} = ${v:.5f} \\pm {e:.5}$")

    # Calculate AIC
    beta = robust_cost_function(model_function(freqs_Hz, *m.values), fluxs_Jy, flux_errs_Jy)
    aic = 2*beta + 2*k + (2*k*(k+1)) / (len(freqs_Hz) - k -1)
    fit_info.append(f"AIC: {aic:.1f}")

    fit_info = "\n".join(fit_info)

    if plot:
        plot_fit(freqs_MHz, fluxs_mJy, flux_errs_mJy, ref, model_function, m, fit_info,
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
    model_name : `str`
        The best fit model name from :py:meth:`pulsar_spectra.models`.
    m : `iminuit.Minuit`
        The Minuit class after being fit in :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.
    fit_info : `str`
        The string to label the fit with from :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.
    p_best : `float`
        The probability that the best-fit model is actually the best-fit model.
    p_category : `str`
        Category based on the quality of spectral fit, as defined in Jankowski et al. (2018).
    """
    # Prepare plots and fitting frequencies
    if plot_compare:
        # Set up plots
        nrows = 5
        plot_size = 4
        fitted_freqs_MHz = np.logspace(np.log10(min(freqs_MHz)), np.log10(max(freqs_MHz)), 100)
        fig, axs = plt.subplots(nrows, 1, figsize=(plot_size, plot_size * nrows))

    # Load model settings
    model_dict = model_settings()
    aics = []
    iminuit_results = []
    fit_infos = []
    model_i = []
    # loop over models and fit
    for i, model_name in enumerate(model_dict.keys()):
        model_function, short_name, start_params, mod_limits = model_dict[model_name]
        aic, iminuit_result, fit_info = iminuit_fit_spectral_model(freqs_MHz, fluxs_mJy, flux_errs_mJy, ref_all,
                        model_name=model_name, plot=plot_all, plot_error=plot_error, save_name=f"{pulsar}_{model_name}_fit.png",
                        alternate_style=alternate_style, axis=axis, secondary_fit=secondary_fit)
        logger.debug(f"{model_name} model fit gave AIC {aic}.")
        if iminuit_result is not None:
            aics.append(aic)
            iminuit_results.append(iminuit_result)
            fit_infos.append(fit_info)
            model_i.append(i)

            # Add to comparison plot
            if plot_compare:
                # plot data
                plot_fit(freqs_MHz, fluxs_mJy, flux_errs_mJy, ref_all, model_function, iminuit_result, fit_info,
                         plot_error=plot_error, alternate_style=alternate_style,
                         axis=axs[i], secondary_fit=secondary_fit, fit_range=fit_range)

    # Return best result
    if len(aics) == 0:
        logger.info(f"No model found for {pulsar}")
        #models[aici], iminuit_results[aici], fit_infos[aici], p_best, p_category
        return None, None, None, None, None
    else:
        aici = aics.index(min(aics))
        best_model_name = list(model_dict.keys())[model_i[aici]]

        logger.info(f"Best model for {pulsar} is {best_model_name}")

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
            plot_fit(freqs_MHz, fluxs_mJy, flux_errs_mJy, ref_all, model_dict[best_model_name][0], iminuit_results[aici], fit_infos[aici],
                    save_name=f"{pulsar}_{best_model_name}_fit.png", plot_error=plot_error, alternate_style=alternate_style,
                    axis=axis, secondary_fit=secondary_fit, fit_range=fit_range)
        return best_model_name, iminuit_results[aici], fit_infos[aici], p_best, p_category


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