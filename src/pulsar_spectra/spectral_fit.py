"""
Functions used to fit different spectral models to the fluxs_mJy densities of pulsars
"""

import os
import yaml
import numpy as np
from iminuit import Minuit
from iminuit.cost import LeastSquares
from jacobi import propagate

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from cycler import cycler

from pulsar_spectra.models import model_settings
from pulsar_spectra.catalogue import convert_cat_list_to_dict
from pulsar_spectra.load_data import DEFAULT_PLOTTING_CONFIG

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
    # logger.debug(f"f_y: {f_y}")
    # logger.debug(f"y: {y}")
    # logger.debug(f"sigma_y: {sigma_y}")
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
    residual = np.sqrt(np.abs(sq_resi))
    for j in range(len(residual)):
        if residual[j] < k:
            rho.append( 1./2. * sq_resi[j] )
        else:
            rho.append( k * residual[j] - 1./2. * k**2 )
    if single_value:
        return rho[0]
    else:
        return rho


def propagate_flux_n_err(freqs, model, iminuit_result):
    """Propagate the flux based on an input model and use the iminuit to calculate errors if possible.

    Parameters
    ----------
    freqs : `list`
        List of frequencies in MHz.
    model : `function`
        The spectral model function from :py:meth:`pulsar_spectra.models`.
    iminuit_result : `iminuit.Minuit`
        The Minuit class after being fit in :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.

    Returns
    -------
    fitted_flux : `list`
        A list of the fluxes (in mJy) based on the input model and fit results.
    fitted_flux_err : `list`
        A list of flux errors (in mJy)  if possible or Nones if not possible.
    """
    if iminuit_result.valid:
        try:
            fitted_flux, fitted_flux_cov = propagate(lambda p: model(freqs * 1e6, *p) * 1e3, iminuit_result.values, iminuit_result.covariance)
        except ValueError:
            fitted_flux = model(freqs * 1e6, *iminuit_result.values) * 1e3
            fitted_flux_err = [None]*len(fitted_flux)
        else:
            fitted_flux_err = np.diag(fitted_flux_cov) ** 0.5
    else:
        # No convariance values so use old method
        fitted_flux = model(freqs * 1e6, *iminuit_result.values) * 1e3
        fitted_flux_err = [None]*len(fitted_flux)
    return fitted_flux, fitted_flux_err


def compute_log_lims(vals, val_errs=None, margin=0.1):
    """Compute the plot limits based on data and data error bars.

    Parameters
    ----------
    vals : `list`
        List of data values.
    val_errs : `list`, optional
        List of data value errors. |br| Default: None.
    margin : `float`, optional
        Margin of space beyond min and max data points, in range (0, 1). |br| Default: 0.1.

    Returns
    -------
    plot_lims : `list`
        The plot limits in the form [lower_lim, upper_lim].
    """
    if margin <= 0 or margin >= 1:
        # Margin cannot be greater than the figure size
        print('Invald plot margin. Defaulting to 30%.')
        margin = 0.1

    vals = np.array(vals)

    if val_errs is None:
        val_errs = 0.0
    else:
        val_errs = [x if x != None else 0 for x in val_errs]
        val_errs = np.array(val_errs)

    # Max and min values including error bars
    lower_vals = vals - val_errs / 2
    upper_vals = vals + val_errs / 2
    
    # Transform to log space
    log_vals = np.log10(vals, where=vals>0)
    lower_log_vals = np.log10(lower_vals, where=lower_vals>0)
    upper_log_vals = np.log10(upper_vals, where=upper_vals>0)
    
    # Log limits
    min_log_val = np.min(np.concatenate([lower_log_vals, log_vals]))
    max_log_val = np.max(np.concatenate([upper_log_vals, log_vals]))
    log_range = max_log_val - min_log_val
    log_centre = 0.5*(max_log_val + min_log_val)
    
    # Log limits with margins
    expanded_log_range = log_range*(1+margin)
    expanded_min_log_val = log_centre - 0.5*expanded_log_range
    expanded_max_log_val = log_centre + 0.5*expanded_log_range
    
    # Compute limits in linear space
    lim_lower = 10**expanded_min_log_val
    lim_upper = 10**expanded_max_log_val
    return [lim_lower, lim_upper]


def plot_fit(freqs_MHz, bands_MHz, fluxs_mJy, flux_errs_mJy, ref, model, iminuit_result, fit_info,
             plot_error=True, save_name="fit.png", alternate_style=False, axis=None,
             secondary_fit=False, fit_range=None, ref_markers=None, plot_bands=False,
             plotting_config=DEFAULT_PLOTTING_CONFIG):
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
    ref_markers : `dict` [`str`, `tuple`], optional
        Used to overwrite the data marker defaults. The key is the reference name and the tuple contains (color, marker, markersize). |br| Default: None.
    plot_bands : `boolean`, optional
        Plot bandwidths as error bars. |br| Default: False.
    plotting_config : `string`, optional
        File path of plotting config file. |br| Default: configs/plotting_config.yaml
    """
    if ref_markers is None:
        ref_markers = {}

    with open(plotting_config, 'r') as f:
        config = yaml.safe_load(f)

    # Set up plot
    if axis is None:
        fig, ax = plt.subplots(figsize=(config["Figure height"]*config["Aspect ratio"], config["Figure height"]))
    else:
        ax = axis

    # Set up default mpl markers
    custom_cycler = (cycler(color = [p[1] for p in config["Markers"]])
                    + cycler(marker = [p[2] for p in config["Markers"]])
                    + cycler(markersize = [p[3] for p in config["Markers"]]))
    ax.set_prop_cycle(custom_cycler)

    # Add data
    data_dict = convert_cat_list_to_dict({"dummy_pulsar":[freqs_MHz, bands_MHz, fluxs_mJy, flux_errs_mJy, ref]})["dummy_pulsar"]
    for ref in data_dict.keys():
        if ref in ref_markers.keys():
            # ref in user define marker so use theirs
            color, marker, markersize = ref_markers[ref]
        else:
            # Use our defaults
            color = None
            marker = None
            markersize = None
        freqs_ref = np.array(data_dict[ref]['Frequency MHz'])
        if plot_bands:
            bands_ref = np.array(data_dict[ref]['Bandwidth MHz']) / 2.
        else:
            bands_ref = None
        if secondary_fit:
            marker_alpha = 0.
            marker_label = None
        else:
            marker_alpha = 1.
            marker_label = ref.replace('_',' ')
        fluxs_ref = np.array(data_dict[ref]['Flux Density mJy'])
        flux_errs_ref = np.array(data_dict[ref]['Flux Density error mJy']) / 2.
        (_, caps, _) = ax.errorbar(
            freqs_ref,
            fluxs_ref,
            xerr=bands_ref,
            yerr=flux_errs_ref,
            linestyle='None',
            mec='k',
            markeredgewidth=config["Marker border"],
            elinewidth=config["Errorbar linewidth"],
            capsize=config["Capsize"],
            label=marker_label,
            color=color,
            marker=marker,
            markersize=markersize,
            alpha=marker_alpha,
        )
        for cap in caps:
            cap.set_markeredgewidth(config["Errorbar linewidth"])

    # Create fit line
    if fit_range is None:
        # No fit range given so use full range
        if plot_bands:
            min_freqs_MHz = np.min(np.array(freqs_MHz) - np.array(bands_MHz) / 2)
            max_freqs_MHz = np.max(np.array(freqs_MHz) + np.array(bands_MHz) / 2)
        else:
            min_freqs_MHz = min(freqs_MHz)
            max_freqs_MHz = max(freqs_MHz)
        fitted_freq = np.logspace(np.log10(min_freqs_MHz), np.log10(max_freqs_MHz), 100)
    else:
        # Use input fit range
        min_freq, max_freq = fit_range
        fitted_freq = np.logspace(np.log10(min_freq), np.log10(max_freq), 100)

    fitted_flux, fitted_flux_prop = propagate_flux_n_err(fitted_freq, model, iminuit_result)

    # Plot fit line
    if alternate_style:
        # Just use a simple label
        model_dict = model_settings()
        fit_info = model_dict[fit_info.split()[0]][1]
    if secondary_fit:
        ax.plot(fitted_freq, fitted_flux, config["Model colour"], marker="None", ls=config["Secondary linestyle"], lw=2, alpha=0.5, label=fit_info)
    else:
        ax.plot(fitted_freq, fitted_flux, config["Model colour"], marker="None", ls=config["Primary linestyle"], label=fit_info)

    if plot_error and iminuit_result.valid and fitted_flux_prop[0] is not None:
        # draw 1 sigma error band
        if secondary_fit:
            alpha = 0
        else:
            alpha = 0.5
        ax.fill_between(fitted_freq, fitted_flux - fitted_flux_prop, fitted_flux + fitted_flux_prop, facecolor=config["Model error colour"], alpha=alpha)

    # Format plot and save
    ax.set_xscale('log')
    ax.set_yscale('log')
    if plot_bands:
        if fit_range is None:
            ax.set_xlim(compute_log_lims(freqs_MHz, bands_MHz))
        else:
            ax.set_xlim(compute_log_lims(freqs_MHz + [*fit_range], bands_MHz + [0]*2))
    else:
        ax.set_xlim(compute_log_lims(freqs_MHz))
    ax.set_ylim(compute_log_lims(fluxs_mJy, flux_errs_mJy))
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
        plt.savefig(save_name, bbox_inches='tight', dpi=config["Resolution"])
        plt.close()


def migrad_simplex_scan(m, mod_limits, model_name):
    """Find the minimum of least_squares function using the in-built minimisation
    algorithms in iminuit. If migrad by itself fails, then run the simplex
    minimiser before migrad. If simplex fails, run a grid scan over parameter
    space before migrad. Systematically increase the number of calls until
    a valid minimum is found.
    """
    m.tol=0.00001 # low tolerace improves likelihood of a sensible fit
    m.limits = mod_limits # limits are primarily to assist the scan minimiser
    ncall = 10000  # Calls until we abandon the fit
    m.migrad(ncall=ncall)
    if m.valid:
        logger.debug(f"Found for fit with {model_name} using migrad and {m.nfcn} calls.")
    else:
        m.simplex(ncall=ncall)
        m.migrad(ncall=ncall)
        if m.valid:
            logger.debug(f"Found for fit with {model_name} using simplex and {m.nfcn} calls.")
        else:
            m.scan(ncall=ncall)
            m.migrad(ncall=ncall)
            if m.valid:
                logger.debug(f"Found for fit with {model_name} using scan and {m.nfcn} calls.")
    if not m.valid:
        logger.warning(f"No valid minimum found for model {model_name} after {m.nfcn} calls.")

    m.hesse() # accurately computes uncertainties
    logger.debug(model_name)
    logger.debug(m)
    return m


def iminuit_fit_spectral_model(
        freqs_MHz,
        bands_MHz,
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
        fit_range=None,
        ref_markers=None,
        plotting_config=DEFAULT_PLOTTING_CONFIG
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
    ref_markers : `dict` [`str`, `tuple`], optional
        Used to overwrite the data marker defaults. The key is the reference name and the tuple contains (color, marker, markersize). |br| Default: None.
    plotting_config : `string`, optional
        File path of plotting config file. |br| Default: configs/plotting_config.yaml

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
    bands_Hz     = np.array(bands_MHz,     dtype=np.float128) * 1e6
    fluxs_Jy     = np.array(fluxs_mJy,     dtype=np.float128) / 1e3
    flux_errs_Jy = np.array(flux_errs_mJy, dtype=np.float128) / 1e3

    # Load model settings
    model_dict = model_settings()
    model_function = model_dict[model_name][0]
    model_function_integrate = model_dict[model_name][4]

    # Check for model dependent defaults
    if start_params is None:
        start_params = model_dict[model_name][2]
    if mod_limits is None:
        mod_limits = model_dict[model_name][3]
    # Add the reference frequency
    start_params += (v0_Hz,)
    mod_limits += [None]

    if (model_name == "high_frequency_cut_off_power_law" or model_name == "double_turn_over_spectrum") and mod_limits[0] is None:
        # will set the cut off frequency based on the data set's frequency range
        mod_limits[0] = (max(freqs_Hz), 10 * max(freqs_Hz))
        logger.debug(f"HFCO cut off frequency limits (Hz): {mod_limits[0]}")
        # Replace vc start param with max frequency
        temp_params = list(start_params)
        temp_params[0] = max(freqs_Hz)
        start_params = tuple(temp_params)

    # Check if enough inputs
    k = len(start_params)-1 # number of free model parameters
    if len(freqs_MHz) <= k + 1:
        logger.warn(f"Only {len(freqs_MHz)} supplied for {model_name} model fit. This is not enough so skipping")
        return 1e9, None, None, False

    # Fit model
    least_squares = LeastSquares(freqs_Hz, fluxs_Jy, flux_errs_Jy, model_function)
    least_squares.loss = huber_loss_function
    m = Minuit(least_squares, *start_params)
    m.fixed["v0"] = True # fix the reference frequency
    m = migrad_simplex_scan(m, mod_limits, model_name)

    if m.valid and (not None in bands_MHz):
        # Fit model with bandwidth intergration correction
        try:
            min_freqs_Hz = freqs_Hz - bands_Hz / 2
        except ValueError:
            print(save_name)
            for freq, band, flux, flux_err, ref in zip(freqs_MHz, bands_MHz, fluxs_mJy, fluxs_mJy, ref):
                print(f"{float(freq):8.1f}{float(band):8.1f}{float(flux):12.4f}{float(flux_err):12.4f} {str(ref):20s}")
            return 1e9, None, None, False
        max_freqs_Hz = freqs_Hz + bands_Hz / 2
        least_squares = LeastSquares((min_freqs_Hz, max_freqs_Hz), fluxs_Jy, flux_errs_Jy, model_function_integrate)
        least_squares.loss = huber_loss_function
        # Set start params as results from first fit
        past_params = ()
        for param in m.values:
            past_params += (param,)

        logger.debug(f"bandwidth fit params: {past_params}")
        m_band = Minuit(least_squares, *past_params)
        m_band.fixed["v0"] = True # fix the reference frequency
        try:
            m_band = migrad_simplex_scan(m_band, mod_limits, model_name + "_log")
        except ValueError as verr:
            logger.warning(f"{model_name}_log Value Error: {verr}")
            m_band = m
            band_bool = False
        else:
            band_bool = True
        m = m_band
    else:
        band_bool = False
    logger.debug(f"Band bool: {band_bool}")

    # display legend with some fit info
    fit_info = [model_name]
    if band_bool:
        fit_info.append(u'Bandwidth: \u2713')
    else:
        fit_info.append(u'Bandwidth: \u2718')
    for p, v, e in zip(m.parameters, m.values, m.errors):
        if p.startswith("v"):
            fit_info.append(f"{p} = ${v/1e6:8.1f} \\pm {e/1e6:8.1}$ MHz")
        else:
            fit_info.append(f"{p} = ${v:.5f} \\pm {e:.5}$")

    # Calculate AIC
    if band_bool:
        beta = robust_cost_function(model_function_integrate((min_freqs_Hz, max_freqs_Hz), *m.values), fluxs_Jy, flux_errs_Jy)
    else:
        beta = robust_cost_function(model_function(freqs_Hz, *m.values), fluxs_Jy, flux_errs_Jy)
    aic = 2*beta + 2*k + (2*k*(k+1)) / (len(freqs_Hz) - k -1)
    fit_info.append(f"AIC: {aic:.1f}")

    fit_info = "\n".join(fit_info)

    if plot:
        plot_fit(freqs_MHz, bands_MHz, fluxs_mJy, flux_errs_mJy, ref, model_function, m, fit_info,
                save_name=save_name, plot_error=plot_error,
                alternate_style=alternate_style, axis=axis,
                secondary_fit=secondary_fit, fit_range=fit_range,
                ref_markers=ref_markers, plot_bands=band_bool,
                plotting_config=plotting_config)

    return aic, m, fit_info, band_bool


def find_best_spectral_fit(pulsar, freqs_MHz, bands_MHz, fluxs_mJy, flux_errs_mJy, ref_all,
                           plot_all=False, plot_best=False, plot_compare=False,
                           plot_error=True, alternate_style=False, axis=None,
                           secondary_fit=False, fit_range=None, ref_markers=None,
                           plotting_config=DEFAULT_PLOTTING_CONFIG):
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
    ref_markers : `dict` [`str`, `tuple`], optional
        Used to overwrite the data marker defaults. The key is the reference name and the tuple contains (color, marker, markersize). |br| Default: None.
    plotting_config : `string`, optional
        File path of plotting config file. |br| Default: configs/plotting_config.yaml

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
    # Load model settings
    model_dict = model_settings()

    # Prepare plots and fitting frequencies
    if plot_compare:
        # Set up plots
        nrows = len(model_dict)
        plot_size = 4
        fitted_freqs_MHz = np.logspace(np.log10(min(freqs_MHz)), np.log10(max(freqs_MHz)), 100)
        fig, axs = plt.subplots(nrows, 1, figsize=(plot_size, plot_size * nrows))

    aics = []
    iminuit_results = []
    fit_infos = []
    model_i = []
    band_bools = []
    # loop over models and fit
    for i, model_name in enumerate(model_dict.keys()):
        model_function = model_dict[model_name][0]
        model_function_intergral = model_dict[model_name][-1]
        aic, iminuit_result, fit_info, band_bool = iminuit_fit_spectral_model(freqs_MHz, bands_MHz, fluxs_mJy, flux_errs_mJy, ref_all,
                        model_name=model_name, plot=plot_all, plot_error=plot_error, save_name=f"{pulsar}_{model_name}_fit.png",
                        alternate_style=alternate_style, axis=axis, secondary_fit=secondary_fit, ref_markers=ref_markers,
                        plotting_config=plotting_config)
        logger.debug(f"{model_name} model fit gave AIC {aic}.")
        if iminuit_result is not None:
            aics.append(aic)
            iminuit_results.append(iminuit_result)
            fit_infos.append(fit_info)
            model_i.append(i)
            band_bools.append(band_bool)

            # Add to comparison plot
            if plot_compare:
                # plot data
                plot_fit(freqs_MHz, bands_MHz, fluxs_mJy, flux_errs_mJy, ref_all, model_function, iminuit_result, fit_info,
                         plot_error=plot_error, alternate_style=alternate_style,
                         axis=axs[i], secondary_fit=secondary_fit, fit_range=fit_range,
                         ref_markers=ref_markers, plot_bands=band_bool, plotting_config=plotting_config)

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
            plt.close()
        if plot_best:
            plot_fit(freqs_MHz, bands_MHz, fluxs_mJy, flux_errs_mJy, ref_all, model_dict[best_model_name][0], iminuit_results[aici], fit_infos[aici],
                    save_name=f"{pulsar}_{best_model_name}_fit.png", plot_error=plot_error, alternate_style=alternate_style,
                    axis=axis, secondary_fit=secondary_fit, fit_range=fit_range, ref_markers=ref_markers, plot_bands=band_bools[aici],
                    plotting_config=plotting_config)
        return best_model_name, iminuit_results[aici], fit_infos[aici], p_best, band_bools[aici]


def estimate_flux_density(
    est_freq,
    model_name,
    iminuit_result,
):
    """Estimate a pulsar's flux density using a previous spectra fit.

    Parameters
    ----------
    est_freq : `float` or `list`
        A single or list of frequencies to estimate flux at (in MHz).
    model_name : `function`
        The pulsar spectra model name from :py:meth:`pulsar_spectra.models`.
    m : `iminuit.Minuit`
        The Minuit class after being fit in :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.

    Returns
    -------
    fitted_flux : `float` or `list`
        The estimated flux density  (in mJy) of the pulsar at the input frequencies.
    fitted_flux_err : `float` or `list`
        The estimated flux density (in mJy)  errors of the pulsar at the input frequencies.
    """
    # make sure est_freq is a numpy array
    single_value = False
    if isinstance(est_freq, float) or isinstance(est_freq, int):
        est_freq = np.array([est_freq])
        single_value = True
    elif isinstance(est_freq, list):
        est_freq = np.array(est_freq)

    model_dict = model_settings()
    model = model_dict[model_name][0]

    fitted_flux, fitted_flux_err = propagate_flux_n_err(est_freq, model, iminuit_result)

    if single_value:
        return fitted_flux[0], fitted_flux_err[0]
    else:
        return fitted_flux, fitted_flux_err