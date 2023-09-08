Examples
========

Simple example
--------------

The following code can be run to fit PSR J0332+5434:

.. script location: example_scripts/simple_example.py
.. code-block:: python

    from pulsar_spectra.catalogue import collect_catalogue_fluxes
    from pulsar_spectra.spectral_fit import find_best_spectral_fit

    cat_dict = collect_catalogue_fluxes()
    pulsar = 'J0332+5434'
    freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]
    best_model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True)

This will produce `J0332+5434_low_frequency_turn_over_power_law_fit.png`

.. image:: figures/J0332+5434_low_frequency_turn_over_power_law_fit.png
  :width: 800

If you would like to see the result of the best fit you can print them like so

.. code-block:: python

    print(f"Best fit model: {best_model_name}")
    for p, v, e in zip(iminuit_result.parameters, iminuit_result.values, iminuit_result.errors):
        if p.startswith("v"):
            print(f"{p} = {v/1e6:8.1f} +/- {e/1e6:8.1} MHz")
        else:
            print(f"{p} = {v:.5f} +/- {e:.5}")

which will output

.. code-block::

    Best fit model: low_frequency_turn_over_power_law
    vpeak =    142.7 +/-    2e+01 MHz
    a = -2.97665 +/- 0.62124
    c = 3.04974 +/- 3.8789
    beta = 0.47638 +/- 0.19826
    v0 =   1036.8 +/-    1e+01 MHz

Adding your data
----------------

Expanding on the previous example you add your own example like so

.. script location: example_scripts/adding_your_data.py
.. code-block:: python

    from pulsar_spectra.catalogue import collect_catalogue_fluxes
    from pulsar_spectra.spectral_fit import find_best_spectral_fit

    cat_list = collect_catalogue_fluxes()
    pulsar = 'J0040+5716'
    freqs, bands, fluxs, flux_errs, refs = cat_list[pulsar]
    freqs = [300.] + freqs
    bands = [30.] + bands
    fluxs = [10.] + fluxs
    flux_errs = [2.] + flux_errs
    refs = ["Your Work"] + refs
    find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True)

This will produce `J0040+5716_simple_power_law_fit.png` with your data included in the fit and plot.

.. image:: figures/J0040+5716_simple_power_law_fit.png
  :width: 800

.. _multi_plot:

Making a multi pulsar plot
--------------------------

You can create a plot containing multiple pulsars by handing ``find_best_spectral_fit()`` a matplotlib axis like so:

.. script location: example_scripts/creating_a_multi_pulsar_plot.py
.. code-block:: python

    import matplotlib.pyplot as plt
    from pulsar_spectra.spectral_fit import find_best_spectral_fit
    from pulsar_spectra.catalogue import collect_catalogue_fluxes

    # Pulsar, flux, flux_err
    pulsar_flux = [
        ('J0820-1350', 200, 9,  0),
        ('J0837+0610', 430, 10, 1),
        ('J1453-6413', 630, 20, 2),
        ('J1456-6843', 930, 25, 3),
        ('J1645-0317', 883, 80, 4),
        ('J2018+2839', 100, 10, 5),
    ]
    cols = 2
    rows = 3
    fig, axs = plt.subplots(nrows=rows, ncols=cols, figsize=(5*cols, 3.5*rows))

    cat_dict = collect_catalogue_fluxes()
    for pulsar, flux, flux_err, ax_i in pulsar_flux:
        freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]
        freqs = [150.] + freqs
        bands = [10.] + bands
        fluxs = [flux] + fluxs
        flux_errs = [flux_err] + flux_errs
        refs = ["Your Work"] + refs

        model, m, fit_info, p_best, p_category = find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True, alternate_style=True, axis=axs[ax_i//cols, ax_i%cols])
        axs[ax_i//cols, ax_i%cols].set_title('PSR '+pulsar)

    plt.tight_layout(pad=2.5)
    plt.savefig("multi_pulsar_spectra.png", bbox_inches='tight', dpi=300)

This will produce the following plot.

.. image:: figures/multi_pulsar_spectra.png
  :width: 800

To make the marker types consistent across all subplots, see :ref:`Generating a consistent marker set for a multi-pulsar plot <consistent_markers>`.

Estimate flux density
---------------------

You can use the pulsar's fit to estimate a pulsar's flux density at a certain frequency like so:

.. script location: example_scripts/estimate_flux.py
.. code-block:: python

    from pulsar_spectra.spectral_fit import find_best_spectral_fit, estimate_flux_density
    from pulsar_spectra.catalogue import collect_catalogue_fluxes

    cat_dict = collect_catalogue_fluxes()
    pulsar = 'J0820-1350'
    freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]
    model, m, _, _, _ = find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True)
    fitted_flux, fitted_flux_err = estimate_flux_density(150., model, m)
    print(f"{pulsar} estimated flux: {fitted_flux:.1f} ± {fitted_flux_err:.1f} mJy")

Which will output

.. code-block::

    J0820-1350 estimated flux: 220.7 ± 11.0 mJy

Calculate the peak frequency for a log parabolic spectrum fit
-------------------------------------------------------------

Log parabolic spectrum is no longer used by default.
If you turn it back on, you can use the pulsar's fit to calculate the peak frequency like so:

.. script location: example_scripts/peak_frequency_lps.py
.. code-block:: python

    from pulsar_spectra.spectral_fit import find_best_spectral_fit
    from pulsar_spectra.catalogue import collect_catalogue_fluxes
    from pulsar_spectra.analysis import calc_log_parabolic_spectrum_max_freq

    cat_dict = collect_catalogue_fluxes()
    pulsar = 'J1136+1551'
    freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]
    model_name, m, _, _, _ = find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs)
    if model_name == "log_parabolic_spectrum":
        v_peak, u_v_peak = calc_log_parabolic_spectrum_max_freq(
            m.values["a"],
            m.values["b"],
            m.values["v0"],
            m.errors["a"],
            m.errors["b"],
            m.covariance[0][1],
        )
        print(f"v_peak (MHz): {v_peak/1e6:6.2f} +/- {u_v_peak/1e6:6.2f}")
    else:
        print("Not a log parabolic spectrum fit")

Which will output

.. code-block::

    v_peak (MHz):  99.77 +/-   6.51

Estimate emission height from a high-frequency cut-off power-law fit
--------------------------------------------------------------------

As demonstrated in Jankowski et al. (2018), we can use the high-frequency cut-off power-law model
from Kontorovich & Flanchick (2013) to estimate the location of the centre of the magnetic polar cap,
assuming a canonical neutron star (radius of 12+/-2 km; Steiner et al., 2018) and a dipole magnetic field.
To perform this calculation, use the in-built function as follows:

.. script location: example_scripts/estimate_emission_height.py
.. code-block:: python

    from pulsar_spectra.spectral_fit import find_best_spectral_fit
    from pulsar_spectra.catalogue import collect_catalogue_fluxes
    from pulsar_spectra.analysis import calc_high_frequency_cutoff_emission_height

    cat_dict = collect_catalogue_fluxes()
    pulsar = 'J1116-4122'
    freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]
    model_name, m, _, _, _ = find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs)
    if model_name == "high_frequency_cut_off_power_law":
        B_pc, u_B_pc, B_surf, B_lc, r_lc, z_e, u_z_e, z_percent, u_z_percent = calc_high_frequency_cutoff_emission_height(
            pulsar,
            m.values[0],
            m.errors[0],
        )
        print(f"B_pc:    ({B_pc/1e11:.2f} +/- {u_B_pc/1e11:.2f})x10^11 G")
        print(f"B_surf:  {B_surf/1e12:.2f}x10^12 G")
        print(f"B_LC:    {B_lc:.2f} G")
        print(f"R_LC:    {r_lc:.0f} km")
        print(f"z_e:     {z_e:.1f} +/- {u_z_e:.1f} km")
        print(f"z/R_LC:  {z_percent:.2f} +/- {u_z_percent:.2f} %")
    else:
        print("Not a power-law with high-frequency cut-off fit")

Which will output

.. code-block::

    B_pc:    (2.05 +/- 0.26)x10^11 G
    B_surf:  2.77x10^12 G
    B_LC:    30.97 G
    R_LC:    44989 km
    z_e:     28.6 +/- 4.9 km
    z/R_LC:  0.06 +/- 0.01 %