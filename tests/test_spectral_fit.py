#! /usr/bin/env python
"""
Tests the spectral_fit.py script
"""

import numpy as np

from pulsar_spectra.spectral_fit import find_best_spectral_fit
from pulsar_spectra.catalogue import collect_catalogue_fluxes


def test_find_best_spectral_fit():
    """Tests the find_best_spectral_fit funtion.
    """
    # limit the input publications to prevent future additions making the tests fail
    cat_list = collect_catalogue_fluxes(
        only_use=[
            'Jankowski_2018',
            'Keith_2011',
            'Johnston_1993',
            'Jankowski_2019',
            'Bondonneau_2020',
            'Dai_2015',
            'Manchester_1996',
            'Bell_2016',
            'Fake data',
            'Toscano_1998',
            'Dewey_1985',
            'Bilous_2016',
            'Malofeev_2000',
            'Hobbs_2004a',
            'Murphy_2017',
            'Lee_2022',
            'Bilous_2020',
            'Kramer_1998',
            'Manchester_1978a',
            'Spiewak_2022',
            'Zhang_2019',
            'Lorimer_1995b',
            'Izvekova_1981',
            'Zhao_2019',
            'Johnston_2018',
            'Bhat_2022',
            'Bartel_1978',
            'van_Ommen_1997',
            'Xue_2017',
            'Zakharenko_2013',
            'Sanidas_2019',
            'Robinson_1995',
            'McEwen_2020',
            'Frail_2016'
        ]
    )
    ref_markers = {
        "Jankowski_2018": ("k",       "d", 7),    # black thin diamond
        "Jankowski_2019": ("#b6dbff", "*", 9),    # light blue star
        "Xue_2017":       ("y",       "P", 7.5),  # yellow thick plus)
    }
    pulsars = [
        ('J0415+6954', "simple_power_law"),
        ('J0437-4715', "broken_power_law"),
        ('J1703-1846', "high_frequency_cut_off_power_law"),
        ('J0024-7204C', "low_frequency_turn_over_power_law"),
        ('J1932+1059', "double_turn_over_spectrum"),
    ]
    refs_needed = []
    for pulsar, exp_model_name in pulsars:
        print(f"\nFitting {pulsar}")
        freq_all, band_all, flux_all, flux_err_all, ref_all = cat_list[pulsar]
        if pulsar == 'J1932+1059':
            # Add an extra point to encourage a high frequency cut off
            freq_all.append(25000)
            band_all.append(1000)
            flux_all.append(0.01)
            flux_err_all.append(0.001)
            ref_all.append("Fake data")
        for freq, band, flux, flux_err, ref in zip(freq_all, band_all, flux_all, flux_err_all, ref_all):
            print(f"{float(freq):8.1f}{float(band):8.1f}{float(flux):12.4f}{float(flux_err):12.4f} {str(ref):20s}")
            refs_needed.append(ref)
        model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(
            pulsar, freq_all, band_all, flux_all, flux_err_all, ref_all,
            plot_compare=True, ref_markers=ref_markers,
        )
        for p, v, e in zip(iminuit_result.parameters, iminuit_result.values, iminuit_result.errors):
            if p.startswith("v"):
                print(f"{p} = {v/1e6:8.1f} +/- {e/1e6:8.1} MHz")
            else:
                print(f"{p} = {v:.5f} +/- {e:.5}")
        np.testing.assert_string_equal(model_name, exp_model_name)
    print(f"Refs needed:{list(set(refs_needed))}")


def test_plot_methods():
    """Tests the find_best_spectral_fit plotting methods.
    """
    cat_list = collect_catalogue_fluxes()
    pulsar = 'J0820-1350'
    print(f"Fitting {pulsar}")
    print("Plotting Compare")
    find_best_spectral_fit(pulsar, cat_list[pulsar][0], cat_list[pulsar][1], cat_list[pulsar][2], cat_list[pulsar][3], cat_list[pulsar][4], plot_compare=True)
    print("Plotting All")
    find_best_spectral_fit(pulsar, cat_list[pulsar][0], cat_list[pulsar][1], cat_list[pulsar][2], cat_list[pulsar][3], cat_list[pulsar][4], plot_all=True)
    print("Plotting Best")
    find_best_spectral_fit(pulsar, cat_list[pulsar][0], cat_list[pulsar][1], cat_list[pulsar][2], cat_list[pulsar][3], cat_list[pulsar][4], plot_best=True)
    print("Plotting Best alternate style and fit range")
    find_best_spectral_fit(pulsar, cat_list[pulsar][0], cat_list[pulsar][1], cat_list[pulsar][2], cat_list[pulsar][3], cat_list[pulsar][4],
                           plot_best=True, alternate_style=True, fit_range=(10, 1100))


if __name__ == "__main__":
    """
    Tests the relevant functions in spectral_fit.py
    """
    # introspect and run all the functions starting with 'test'
    for f in dir():
        if f.startswith('test'):
            print(f)
            globals()[f]()
