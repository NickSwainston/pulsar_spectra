#! /usr/bin/env python
"""
Tests the spectral_fit.py script
"""

import os
import numpy as np
from numpy.testing import assert_almost_equal
import csv
import sys

from pulsar_spectra.spectral_fit import find_best_spectral_fit
from pulsar_spectra.catalogue import collect_catalogue_fluxes

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# formatter = logging.Formatter('%(asctime)s  %(name)s  %(lineno)-4d  %(levelname)-9s :: %(message)s')
# ch = logging.StreamHandler()
# ch.setFormatter(formatter)
# # Set up local logger
# logger.setLevel(logging.DEBUG)
# logger.addHandler(ch)
# logger.propagate = False
# # Loop over imported vcstools modules and set up their loggers
# for imported_module in sys.modules.keys():
#     if imported_module.startswith('pulsar_spectra'):
#         logging.getLogger(imported_module).setLevel(logging.DEBUG)
#         logging.getLogger(imported_module).addHandler(ch)
#         logging.getLogger(imported_module).propagate = False



def test_find_best_spectral_fit():
    """Tests the find_best_spectral_fit funtion.
    """
    # limit the input publications to prevent future additions making the tests fail
    cat_list = collect_catalogue_fluxes(
        only_use=[
            "Murphy_2017",
            "McEwen_2022",
            "Xue_2017",
            "Taylor_1993",
            "Stappers_2008",
            "Jankowski_2018",
            "Jankowski_2019",
            "Bell_2016",
            "Johnston_2018",
            "Zhao_2019",
            "van_Ommen_1997",
            "Keith_2011",
            "Seiber_1973",
            "Keith_2011",
            "Sieber_1973",
            "Malofeev_2000",
            "Lorimer_1995b",
            "Bondonneau_2020",
            "Zakharenki_2013",
            "Sanidas_2019",
            "Izekova_1981",
            "Bartel_1978",
            "Johnston_2006",
            "Zakharenko_2013",
            "Izvekova_1981",
            "Kijak_2017",
            "Han_2016",
            "Hobbs_2004a",
            "Dembska_2014",
        ]
    )
    ref_markers = {
        "Jankowski_2018": ("k",       "d", 7),    # black thin diamond
        "Jankowski_2019": ("#b6dbff", "*", 9),    # light blue star
        "Xue_2017":       ("y",       "P", 7.5),  # yellow thick plus)
    }
    pulsars = [
        ('J0034-0534', "simple_power_law"),
        ('J0835-4510', "broken_power_law"),
        ('J1751-4657', "high_frequency_cut_off_power_law"),
        ('J0953+0755', "low_frequency_turn_over_power_law"),
        ('J1852-0635', "double_turn_over_spectrum"),
    ]
    for pulsar, exp_model_name in pulsars:
        print(f"\nFitting {pulsar}")
        freq_all, flux_all, flux_err_all, ref_all = cat_list[pulsar]
        if pulsar == 'J0034-0534':
            # Remove the Bondonneau_2020 data point
            freq_all = freq_all[:-1]
            flux_all = flux_all[:-1]
            flux_err_all = flux_err_all[:-1]
            ref_all = ref_all[:-1]
        for freq, flux, flux_err, ref in zip(freq_all, flux_all, flux_err_all, ref_all):
            print(f"{float(freq):8.1f}{float(flux):12.4f}{float(flux_err):12.4f} {str(ref):20s}")
        model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(
            pulsar, freq_all, flux_all, flux_err_all, ref_all,
            plot_compare=True, ref_markers=ref_markers,
        )
        for p, v, e in zip(iminuit_result.parameters, iminuit_result.values, iminuit_result.errors):
            if p.startswith("v"):
                print(f"{p} = {v/1e6:8.1f} +/- {e/1e6:8.1} MHz")
            else:
                print(f"{p} = {v:.5f} +/- {e:.5}")
        np.testing.assert_string_equal(model_name, exp_model_name)


def test_plot_methods():
    """Tests the find_best_spectral_fit plotting methods.
    """
    cat_list = collect_catalogue_fluxes()
    pulsar = 'J0820-1350'
    print(f"Fitting {pulsar}")
    print("Plotting Compare")
    find_best_spectral_fit(pulsar, cat_list[pulsar][0], cat_list[pulsar][1], cat_list[pulsar][2], cat_list[pulsar][3], plot_compare=True)
    print("Plotting All")
    find_best_spectral_fit(pulsar, cat_list[pulsar][0], cat_list[pulsar][1], cat_list[pulsar][2], cat_list[pulsar][3], plot_all=True)
    print("Plotting Best")
    find_best_spectral_fit(pulsar, cat_list[pulsar][0], cat_list[pulsar][1], cat_list[pulsar][2], cat_list[pulsar][3], plot_best=True)
    print("Plotting Best alternate style and fit range")
    find_best_spectral_fit(pulsar, cat_list[pulsar][0], cat_list[pulsar][1], cat_list[pulsar][2], cat_list[pulsar][3],
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
