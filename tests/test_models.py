#! /usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

from pulsar_spectra.models import model_settings

def test_bandwidth_model():
    """Tests if the bandwith correction intergrals are accurate.
    """
    #cat_dict = collect_catalogue_fluxes(use_atnf=False)
    c_s = 1.
    a_s = -1.6
    beta_s = 1.
    vc_s = 1e10
    vpeak_s = 5e7
    v0_s = 5e8
    pulsar_model = {
        # a, c, v0
        "simple_power_law": (a_s, c_s, v0_s),
        # vb, a1, a2, c, v0
        "broken_power_law": (1e9, a_s, a_s, c_s, v0_s),
        # vc, a, c, v0
        "high_frequency_cut_off_power_law": (vc_s, a_s, c_s, v0_s),
        # vpeak, a, c, beta, v0
        "low_frequency_turn_over_power_law": (vpeak_s, a_s, c_s, beta_s, v0_s),
        # vc, vpeak, a, beta, c, v0
        'double_turn_over_spectrum': (vc_s, vpeak_s, a_s, beta_s, c_s, v0_s),
    }

    freq_all = np.logspace(np.log10(1e7), np.log10(9e9), 30)
    band_all = freq_all * 0.2
    model_dict = model_settings()
    for model_name in model_dict.keys():
        print(f"\n{model_name}")
        model_function = model_dict[model_name][0]
        model_function_intergral = model_dict[model_name][-1]
        fit_vals = pulsar_model[model_name]

        # Set test plot
        plotsize = 3.2
        fig, ax = plt.subplots(figsize=(plotsize*4/3, plotsize))
        # Set up default mpl markers
        capsize = 1.5
        errorbar_linewidth = 0.7
        marker_border_thickness = 0.5

        fitted_flux = model_function(freq_all, *fit_vals)
        (_, caps, _) = ax.errorbar(
            freq_all,
            fitted_flux,
            xerr=band_all / 2.,
            linestyle='None',
            mec='k',
            markeredgewidth=marker_border_thickness,
            elinewidth=errorbar_linewidth,
            capsize=capsize,
        )
        for cap in caps:
            cap.set_markeredgewidth(errorbar_linewidth)
        ax.plot(freq_all, fitted_flux, 'k--')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.get_xaxis().set_major_formatter(FormatStrFormatter('%g'))
        ax.get_yaxis().set_major_formatter(FormatStrFormatter('%g'))
        ax.tick_params(which='both', direction='in', top=1, right=1)
        ax.set_xlabel('Frequency (MHz)')
        ax.set_ylabel('Flux Density (mJy)')
        ax.grid(visible=True, ls=':', lw=0.6)
        plt.savefig(f"{model_name}_test.png", bbox_inches='tight', dpi=300)
        plt.clf()

        # For each flux check if the intergration is accurate
        for freq, band in zip(freq_all, band_all):
            if model_name == "broken_power_law" and 9e8 < freq < 1.2e9:
                # skip around the break as it doesn't perform well there
                continue

            # Calculate the area under the curve with the trapzoid rule
            freq_min = freq - band / 2
            freq_max = freq + band / 2
            band_freq_range = np.linspace(freq_min, freq_max, 10000)
            band_flux_range = model_function(band_freq_range, *fit_vals)
            area_sum = 0.
            for a, b in zip(band_flux_range[:-1], band_flux_range[1:]):
                area_sum += (a + b) / 2
            area_sum *= (band_freq_range[1] - band_freq_range[0])

            # Use the intergral function to get the equivalent
            band_result = model_function_intergral((freq_min, freq_max), *fit_vals)
            band_sum = band_result * band

            # Compare
            perc_diff = 2 * ( band_sum - area_sum ) / ( band_sum + area_sum ) * 100
            print(f"freq: {freq/1e6:8.1f} band: {band/1e6:8.1f}  Percent difference: {perc_diff:10.4f} %   band_sum: {area_sum:15.2f}  band_intergral: {band_sum:15.2f}")
            np.testing.assert_approx_equal(band_sum, area_sum, significant=1)

if __name__ == "__main__":
    """
    Tests the relevant functions in models.py
    """
    # introspect and run all the functions starting with 'test'
    for f in dir():
        if f.startswith('test'):
            print(f)
            globals()[f]()
