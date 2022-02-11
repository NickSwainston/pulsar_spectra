Examples
========

Simple example
--------------

The following can be run to fit J1453-6413

.. code-block:: python

    from pulsar_spectra.catalogues import collect_catalogue_fluxes
    from pulsar_spectra.spectral_fit import find_best_spectral_fit

    cat_list = collect_catalogue_fluxes()
    pulsar = 'J1453-6413'
    freqs, fluxs, flux_errs, refs = cat_list[pulsar]
    find_best_spectral_fit(pulsar, freqs, fluxs, flux_errs, refs, plot_best=True)

This will produce J1453-6413_simple_power_law_fit.png

.. image:: figures/J1453-6413_simple_power_law_fit.png
  :width: 800


Adding your data
----------------

Expanding on the previous example you add your own example like so

.. code-block:: python

    from pulsar_spectra.catalogues import collect_catalogue_fluxes
    from pulsar_spectra.spectral_fit import find_best_spectral_fit

    cat_list = collect_catalogue_fluxes()
    pulsar = 'J1453-6413'
    freqs, fluxs, flux_errs, refs = cat_list[pulsar]
    freqs += [150.]
    fluxs += [1000.]
    flux_errs += [100.]
    refs += ["Your Work"]
    find_best_spectral_fit(pulsar, freqs, fluxs, flux_errs, refs, plot_best=True)

This will also produce J1453-6413_simple_power_law_fit.png with your data included in the fit and plot.

.. image:: figures/J1453-6413_your_work.png
  :width: 800

