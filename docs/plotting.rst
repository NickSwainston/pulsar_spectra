Plotting
========

Below we describe additional features available for customising spectral plots.


Creating publication-quality plots
----------------------------------

By default, the legend will be positioned to the right of the figure box with the best-fit parameter values and the
full model name. The automated plotting includes an alternative, more compact figure style with the legend included
within the figure box and with an abbreviated model name and no fit info. This is done using the following code:

.. code-block:: python

    from pulsar_spectra.catalogue import collect_catalogue_fluxes
    from pulsar_spectra.spectral_fit import find_best_spectral_fit

    cat_dict = collect_catalogue_fluxes()
    pulsar = 'J1909-3744'
    freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]
    best_model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True)

This will produce the following plot:

.. image:: figures/example_alternate_style.png
  :width: 800


Using custom marker types
-------------------------

By default, the code will cycle through a set list of marker types. When creating figures for multiple pulsars, the 
default marker assignment can lead to inconsistency in the marker types. This can be solved by assigning a custom
marker to each reference. You can specify custom marker types using the following code:

.. code-block:: python

    from pulsar_spectra.catalogue import collect_catalogue_fluxes
    from pulsar_spectra.spectral_fit import find_best_spectral_fit

    custom_markers = {
    #   reference           :   (marker colour, marker type, marker size)
        "Jankowski_2018"    :   ('magenta', 'h', 5), # orange circle
        "Jankowski_2019"    :   ('cyan', 'H', 5)  # green diamond
    }

    cat_dict = collect_catalogue_fluxes()
    pulsar = 'J1909-3744'
    freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]
    best_model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True, ref_markers=custom_markers)

This will produce the following plot:

.. image:: figures/example_custom_markers.png
  :width: 800

In `Lee et al. (2022) <https://ui.adsabs.harvard.edu/abs/2022PASA...39...42L/abstract>`, 32 custom marker types were created to ensure unique and consistent markers were
used throughout the figures. These custom marker types are proved below:

.. code-block:: python

    msc = 0.8 # marker scale
    ref_markers = {
    #   Reference               : (colour, type, size),           # marker description
        'This work'             : ("#006ddb",   "o", 7*msc),      # blue circle
        'Bartel_1978'           : ("#009292",   "^", 7*msc),      # turquoise triangle
        'Bell_2016'             : ("m",         "v", 7*msc),      # purple upside-down triangle
        'Bilous_2016'           : ("m",         "X", 7.5*msc),    # purple thick cross
        'Bilous_2020'           : ("y",         "*", 10*msc),     # yellow star
        'Bondonneau_2020'       : ("#db6d00",   ">", 7*msc),      # orange right-pointing triangle
        'Dai_2015'              : ("#920000",   "X", 7*msc),      # maroon thick cross
        'Hobbs_2004'            : ("tab:orange","s", 5.5*msc),    # orange square
        'Izvekova_1981'         : ("#ffb6db",   "X", 7.5*msc),    # light pink thick cross
        'Jankowski_2018'        : ("c",         "H", 7*msc),      # cyan sideways hexagon
        'Jankowski_2019'        : ("#009292",   "P", 7.5*msc),    # turqoise thick plus
        'Johnston_1993'         : ("tab:green", "p", 6.5*msc),    # dark green pentagon
        'Johnston_2006'         : ("y",         "P", 7.5*msc),    # yellow thick plus
        'Johnston_2018'         : ("#b6dbff",   "d", 7*msc),      # light blue thin diamond
        'Johnston_2021'         : ("y",         "s", 5.5*msc),    # yellow square
        'Keith_2011'            : ("#ff6db6",   "d", 7*msc),      # pink thin diamond
        'Lorimer_1995'          : ("tab:orange","X", 7*msc),      # orange thick cross
        'Malofeev_2000'         : ("r",         "P", 7.5*msc),    # red thick plus
        'Mignani_2017'          : ("g",         "D", 5*msc),      # green diamond
        'Murphy_2017'           : ("#ff6db6",   "*", 10*msc),     # pink star
        'Sanidas_2019'          : ("k",         "d", 7*msc),      # black thin diamond
        'Sieber_1973'           : ("#6db6ff",   "p", 6*msc),      # sky blue pentagon
        'Stovall_2015'          : ("#920000",   "s", 5*msc),      # maroon small square
        'van_Ommen_1997'        : ("#24ff24",   "^", 7*msc),      # green triangle
        'Xue_2017'              : ("r",         "D", 6*msc),      # red diamond
        'Zakharenko_2013'       : ("#b66dff",   "h", 7*msc),      # lavender hexagon
        'Zhao_2019'             : ("#004949",   "<", 7*msc),      # dark green left-pointing triangle
        'Manchester_1978_ATNF'  : ("tab:purple","s", 5*msc),      # purple small square
        'Toscano_1998_ATNF'     : ("tab:orange","d", 7*msc),      # orange thin diamond
        'Kramer_1999_ATNF'      : ("y",         "o", 5*msc),      # yellow small circle
        'Qiao_1995_ATNF'        : ("tab:olive", "<", 6*msc),      # olive small left-pointing triangle
        'Tyul\'bashev_2016_ATNF': ("k",         "o", 5*msc),      # black small circle
    }

Plotting a secondary model
--------------------------

Sometimes you may want to plot more than one best-fit model on the same figure with different subsets of data included
in the fit. To differentiate between the two models, we have included an alternate model style which is light grey
and does not show the uncertainty envelope. For example, the following code can be used to show the model fit
before and after the addition of your data:

.. code-block:: python

    import matplotlib.pyplot as plt
    from pulsar_spectra.catalogue import collect_catalogue_fluxes
    from pulsar_spectra.spectral_fit import find_best_spectral_fit

    cat_dict = collect_catalogue_fluxes()
    pulsar = 'J1909-3744'
    freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]

    fig, ax = plt.subplots(figsize=(5,4))
    find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True, secondary_fit=True, axis=ax)

    freqs = [150.] + freqs
    bands = [30.] + bands
    fluxs = [6.] + fluxs
    flux_errs = [1.] + flux_errs
    refs = ['Your Work'] + refs
    best_model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True, axis=ax)

    plt.savefig(pulsar+'_'+best_model_name+'_fit.png', bbox_inches='tight', dpi=300)

This will produce the following plot:

.. image:: figures/example_secondary_fit.png
  :width: 800