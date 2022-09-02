#! /usr/bin/env python

from webbrowser import BackgroundBrowser
import numpy as np

from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.models import model_settings
from pulsar_spectra.spectral_fit import iminuit_fit_spectral_model

def test_bandwidth_model():
    """Tests if the bandwith correction intergrals are accurate.
    """
    cat_dict = collect_catalogue_fluxes(use_atnf=False)
    pulsar_model = {
        "simple_power_law": 'J0034-0534',
        "broken_power_law": 'J0835-4510',
        "high_frequency_cut_off_power_law": 'J1644-4559',
        "low_frequency_turn_over_power_law": 'J0953+0755',
        'double_turn_over_spectrum': 'J1932+1059',
    }

    model_dict = model_settings()
    for model_name in model_dict.keys():
        model_function = model_dict[model_name][0]
        model_function_intergral = model_dict[model_name][-1]

        # Find pulsar for the model
        pulsar = pulsar_model[model_name]
        freq_all, band_all, flux_all, flux_err_all, ref_all = cat_dict[pulsar]
        # get a fit for the model
        _, iminuit_result, _, _ = iminuit_fit_spectral_model(
            freq_all,
            band_all,
            flux_all,
            flux_err_all,
            ref_all,
            model_name=model_name,
            plot=True,
            save_name=f"{pulsar}_fit.png"
        )
        print(f"\n{model_name}")

        # For each flux check if the intergration is accurate
        for freq, band in zip(freq_all, band_all):
            # covert to hz
            freq *=  1e6
            band *= 1e6

            # Calculate the area under the curve with the trapzoid rule
            freq_min = freq - band / 2
            freq_max = freq + band / 2
            band_freq_range = np.linspace(freq_min, freq_max, 10000)
            band_flux_range = model_function(band_freq_range, *iminuit_result.values)
            area_sum = 0.
            for a, b in zip(band_flux_range[:-1], band_flux_range[1:]):
                area_sum += (a + b) / 2
            area_sum *= (band_freq_range[1] - band_freq_range[0])

            # Use the intergral function to get the equivalent
            band_result = model_function_intergral((freq_min, freq_max), *iminuit_result.values)
            band_sum = band_result * band

            # Compare
            perc_diff = 2 * ( band_sum - area_sum ) / ( band_sum + area_sum ) * 100
            print(f"freq: {freq/1e6:8.1f} band: {band/1e6:8.1f}  Percent difference: {perc_diff:10.4f} %   band_sum: {area_sum:20.2f}  band_intergral: {band_sum:20.2f}")

if __name__ == "__main__":
    """
    Tests the relevant functions in models.py
    """
    # introspect and run all the functions starting with 'test'
    for f in dir():
        if f.startswith('test'):
            print(f)
            globals()[f]()
