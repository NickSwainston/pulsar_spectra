#! /usr/bin/env python
"""
Tests the spectral_fit.py script
"""
import os
import numpy as np
from numpy.testing import assert_almost_equal
import csv

from pulsar_spectra import catalogues
from pulsar_spectra.spectral_fit import find_best_spectral_fit
from pulsar_spectra.catalogues import collect_catalogue_fluxes, convert_cat_list_to_dict

import logging
logger = logging.getLogger(__name__)


def test_find_best_spectral_fit():
    """Tests the find_best_spectral_fit funtion.
    """
    cat_list = collect_catalogue_fluxes()
    #print(cat_dict)
    #pulsars = ['J0034-0534','J0953+0755', 'J1645-0317']
    pulsars = ['J0820-1350', 'J0835-4510', 'J0837+0610', 'J0953+0755', 'J1453-6413', 'J1456-6843', 'J1645-0317', 'J1731-4744', "J0332+5434"]
    for pulsar in pulsars:
        print(f"\nFitting {pulsar}")
        #print(cat_dict[pulsar])
        #print(cat_list[pulsar])
        freq_all     = np.array(cat_list[pulsar][0])
        flux_all     = np.array(cat_list[pulsar][1])
        flux_err_all = np.array(cat_list[pulsar][2])
        ref_all      = np.array(cat_list[pulsar][3])
        #print(freq_all, flux_all, flux_err_all)
        model, iminuit_result, fit_info = find_best_spectral_fit(pulsar, freq_all, flux_all, flux_err_all, ref_all, plot_compare=True)
        print(model)


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



def test_Jankowski_fig_5():
    cat_list = collect_catalogue_fluxes(exclude=["Xue_2017", "Bondonneau_2020", "Johnston_2021"])
    # Jankowski figure 5
    # low frequency turn over, high-frequency cut off, broken power law, log-parabolic
    pulsars = ['J0837+0610', 'J0908-4913', 'J1359-6038', 'J1903-0632']
    for pulsar in pulsars:
        print(f"\nFitting {pulsar}")
        freq_all     = np.array(cat_list[pulsar][0])
        flux_all     = np.array(cat_list[pulsar][1])
        flux_err_all = np.array(cat_list[pulsar][2])
        ref_all      = np.array(cat_list[pulsar][3])
        #print(freq_all, flux_all, flux_err_all)
        models, iminuit_results, fit_infos, p_best, p_catagory = find_best_spectral_fit(pulsar, freq_all, flux_all, flux_err_all, ref_all, plot_compare=True)
        print(f"Best model {models[1]}, catagory {p_catagory}")


def test_compare_fits_to_Jankowski_2018():
    # Get the pulsars in the Jankowski paper
    jank_pulsar_dict = {}
    with open("{}/test_data/best_model_for_Jankowski_2018.tsv".format(os.path.dirname(os.path.realpath(__file__))), "r") as file:
        tsv_file = csv.reader(file, delimiter="\t")
        lines = []
        for li, line in enumerate(tsv_file):
            if li < 38:
                continue
            pulsar = line[0].strip().replace("–", "-")
            if line[1] == "":
                jank_pulsar_dict[pulsar] = "no_fit"
            elif line[1] == "pl":
                jank_pulsar_dict[pulsar] = "simple_power_law"
            elif line[1] == "broken pl":
                jank_pulsar_dict[pulsar] = "broken_power_law"
            elif line[1] == "lps":
                jank_pulsar_dict[pulsar] = "log_parabolic_spectrum "
            elif line[1] == "hard cut-off":
                jank_pulsar_dict[pulsar] = "high_frequency_cut_off_power_law"
            elif line[1] == "low turn-over":
                jank_pulsar_dict[pulsar] = "low_frequency_turn_over_power_law"
            else:
                print("Not found", line[1])
                exit()

    # Fit all the pulsars
    wrong_count = 0
    cat_dict, cat_list = collect_catalogue_fluxes()
    print(cat_list.keys())
    for pulsar in jank_pulsar_dict.keys():
        if pulsar in cat_list.keys():
            freq_all = np.array(cat_list[pulsar][0])*1e6
            flux_all = np.array(cat_list[pulsar][1])*1e-3
            flux_err_all = np.array(cat_list[pulsar][2])*1e-3
            #print(freq_all, flux_all, flux_err_all)
            models, fit_results = find_best_spectral_fit(pulsar, freq_all, flux_all, flux_err_all, plot=False, data_dict=cat_dict[pulsar])
        else:
            models = [None, "no_fit"]
        print(f"{pulsar} {models[1]} {jank_pulsar_dict[pulsar]}")
        if models[1] != jank_pulsar_dict[pulsar]:
            print(models[1], jank_pulsar_dict[pulsar])
            wrong_count += 1
            #raise AssertionError()
    print(f"wrong_count: {wrong_count}")

if __name__ == "__main__":
    """
    Tests the relevant functions in spectral_fit.py
    """
    # introspect and run all the functions starting with 'test'
    for f in dir():
        if f.startswith('test'):
            print(f)
            globals()[f]()
