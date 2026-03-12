#! /usr/bin/env python
"""
Tests the spectral_fit.py script
"""

import numpy as np
import pytest

from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

spectral_fit_tests = [
    (
        "J0415+6954",
        "simple_power_law",
        [
            "Bilous_2016",
            "Lorimer_1995b",
            "Seiradakis_1995",
            "Sanidas_2019",
            "Dewey_1985",
            "McEwen_2020",
            "Malofeev_2000",
        ],
    ),
    (
        "J1327-6222",
        "broken_power_law",
        [
            "Jankowski_2018",
            "Johnston_1992",
            "Murphy_2017",
            "Jankowski_2019",
            "Bates_2011",
            "Mantovanini_2025",
            "Manchester_1978a",
            "Hobbs_2004a",
            "Johnston_2018",
            "Keith_2024",
            "van_Ommen_1997",
        ],
    ),
    (
        "J0955-5304",
        "high_frequency_cut_off_power_law",
        [
            "Keith_2024",
            "Mantovanini_2025",
            "Qiao_1995",
            "Manchester_1978a",
            "Jankowski_2019",
            "Bhat_2023",
            "Hobbs_2004a",
            "van_Ommen_1997",
        ],
    ),
    (
        "J0953+0755",
        "low_frequency_turn_over_power_law",
        [
            "Bartel_1978",
            "Bell_2016",
            "Bhat_2023",
            "Bondonneau_2020",
            "Frail_2016",
            "Han_1999",
            "Hoensbroech_1997",
            "Izvekova_1981",
            "Jankowski_2018",
            "Jankowski_2019",
            "Johnston_2006",
            "Johnston_2018",
            "Keith_2024",
            "Kumar_2025",
            "Lee_2022",
            "Lorimer_1995b",
            "Malofeev_2000",
            "Manchester_1978a",
            "Mikhailov_2016",
            "Murphy_2017",
            "Sanidas_2019",
            "Seiradakis_1995",
            "Shrauner_1998",
            "Slee_1986",
            "Weisberg_1999",
            "Xue_2017",
            "Zakharenko_2013",
            "Zhao_2017",
            "Zhao_2019",
            "van_Ommen_1997",
        ],
    ),
    (
        "J1543+0929",
        "double_turn_over_spectrum",
        [
            "Murphy_2017",
            "Izvekova_1981",
            "Kumar_2025",
            "Seiradakis_1995",
            "Manchester_1978a",
            "Bhat_2023",
            "Sanidas_2019",
            "Han_1999",
            "Kijak_1998",
            "Weisberg_1999",
            "Slee_1986",
            "Stovall_2015",
            "Lorimer_1995b",
            "Keith_2024",
            "Frail_2016",
            "Shrauner_1998",
            "Bilous_2016",
            "Bondonneau_2020",
            "Bilous_2020",
        ],
    ),
]

# Make copies for the bayesian-nested-sampling and maximum-likelihood methods
spectral_fit_tests_ns = [
    pytest.param("bayesian-nested-sampling", pulsar, model, refs, "Huber", marks=pytest.mark.long)
    for pulsar, model, refs in spectral_fit_tests
]
spectral_fit_tests_ml_gaussian = [
    ("maximum-likelihood", pulsar, model, refs, "Gaussian") for pulsar, model, refs in spectral_fit_tests
]
spectral_fit_tests_ml_huber = [
    ("maximum-likelihood", pulsar, model, refs, "Huber") for pulsar, model, refs in spectral_fit_tests
]
spectral_fit_tests_ml_t = [
    ("maximum-likelihood", pulsar, model, refs, "t") for pulsar, model, refs in spectral_fit_tests
]

# Combine them
combined_spectral_fit_tests = (
    spectral_fit_tests_ns + spectral_fit_tests_ml_gaussian + spectral_fit_tests_ml_huber + spectral_fit_tests_ml_t
)


@pytest.mark.parametrize("fit_method, pulsar, exp_model_name, frozen_refs, likelihood", combined_spectral_fit_tests)
def test_find_best_spectral_fit(fit_method, pulsar, exp_model_name, frozen_refs, likelihood):
    """Tests the find_best_spectral_fit funtion."""
    # limit the input publications to prevent future additions making the tests fail
    cat_list = collect_catalogue_fluxes(only_use=frozen_refs)
    # Use some ref markers to test they can be altered
    ref_markers = {
        "Jankowski_2018": ("k", "d", 7),  # black thin diamond
        "Jankowski_2019": ("#b6dbff", "*", 9),  # light blue star
        "Murphy_2017": ("y", "P", 7.5),  # yellow thick plus
    }

    print(f"\nFitting {pulsar}")
    freq_all, band_all, flux_all, flux_err_all, ref_all = cat_list[pulsar]
    for freq, band, flux, flux_err, ref in zip(freq_all, band_all, flux_all, flux_err_all, ref_all):
        print(f"{float(freq):8.1f}{float(band):8.1f}{float(flux):12.4f}{float(flux_err):12.4f} {str(ref):20s}")
    best_fit_model_name, _, fit_results, _, _ = find_best_spectral_fit(
        pulsar,
        freq_all,
        band_all,
        flux_all,
        flux_err_all,
        ref_all,
        method=fit_method,
        likelihood=likelihood,
        plot_compare=True,
        plot_kwargs={"ref_markers": ref_markers},
    )
    iminuit_result = fit_results[best_fit_model_name]
    if fit_method == "maximum-likelihood":
        for p, v, e in zip(iminuit_result.parameters, iminuit_result.values, iminuit_result.errors):
            if p.startswith("v"):
                print(f"{p} = {v / 1e6:8.1f} +/- {e / 1e6:8.1} MHz")
            else:
                print(f"{p} = {v:.5f} +/- {e:.5}")
    np.testing.assert_string_equal(best_fit_model_name, exp_model_name)


def test_plot_methods():
    """Tests the find_best_spectral_fit plotting methods."""
    cat_list = collect_catalogue_fluxes()
    pulsar = "J0820-1350"
    print(f"Fitting {pulsar}")
    print("Plotting Compare")
    find_best_spectral_fit(
        pulsar,
        cat_list[pulsar][0],
        cat_list[pulsar][1],
        cat_list[pulsar][2],
        cat_list[pulsar][3],
        cat_list[pulsar][4],
        method="maximum-likelihood",
        likelihood="Huber",
        plot_compare=True,
    )
    print("Plotting All")
    find_best_spectral_fit(
        pulsar,
        cat_list[pulsar][0],
        cat_list[pulsar][1],
        cat_list[pulsar][2],
        cat_list[pulsar][3],
        cat_list[pulsar][4],
        method="maximum-likelihood",
        likelihood="Huber",
        plot_all=True,
    )
    print("Plotting Best")
    find_best_spectral_fit(
        pulsar,
        cat_list[pulsar][0],
        cat_list[pulsar][1],
        cat_list[pulsar][2],
        cat_list[pulsar][3],
        cat_list[pulsar][4],
        method="maximum-likelihood",
        likelihood="Huber",
        plot_best=True,
    )
    print("Plotting Best with compact legend style and custom fit range")
    find_best_spectral_fit(
        pulsar,
        cat_list[pulsar][0],
        cat_list[pulsar][1],
        cat_list[pulsar][2],
        cat_list[pulsar][3],
        cat_list[pulsar][4],
        method="maximum-likelihood",
        likelihood="Huber",
        plot_best=True,
        fit_range=(10, 1100),
        legend_style="compact",
    )
    print("Plotting Best with typeset legend style and no bands")
    find_best_spectral_fit(
        pulsar,
        cat_list[pulsar][0],
        cat_list[pulsar][1],
        cat_list[pulsar][2],
        cat_list[pulsar][3],
        cat_list[pulsar][4],
        method="maximum-likelihood",
        likelihood="Huber",
        plot_best=True,
        legend_style="typeset",
        plot_kwargs={"plot_bands": False},
    )


def test_spl_iminuit_upper_limits():

    # Make fake data
    freqs = [1, 10, 100, 1000]
    bands = [0.1, 1, 10, 100]
    fluxes = [1000, 100, 10, 1]
    flux_errs = [500, 50, 5, 0.5]
    refs = ["Fake data"] * 4
    limit_signs = [0] * 4
    min_freqs_MHz = 0.09 # np.min(np.array(freqs) - np.array(bands) / 2)
    max_freqs_MHz = np.max(np.array(freqs) + np.array(bands) / 2)
    fitted_freq = np.logspace(np.log10(min_freqs_MHz), np.log10(max_freqs_MHz), 100)

    # Do a simple fit with normal data to assert fitting without upper limits still works
    best_fit_model_name, _, fit_results, _, _ = find_best_spectral_fit(
        "test_pulsar",
        freqs,
        bands,
        fluxes,
        flux_errs,
        limit_signs,
        refs,
        method="maximum-likelihood",
        likelihood="Huber",
        plot_best=True,
    )
    npt.assert_almost_equal(fit_result.values["a"], -1.00, decimal=2)

    # And a lower data point
    freqs.append(0.1)
    bands.append(0.01)
    fluxes.append(1000)
    flux_errs.append(500)
    refs.append("Fake data")
    limit_signs.append(0)
    print(refs, limit_signs)
    best_fit_model_name, _, fit_results, _, _ = find_best_spectral_fit(
        "test_pulsar",
        freqs,
        bands,
        fluxes,
        flux_errs,
        limit_signs,
        refs,
        method="maximum-likelihood",
        likelihood="Huber",
        plot_best=True,
    )

    plot_dict = iminuit_interpolate_model(
        fit_result,
        "simple_power_law",
        fitted_freq,
        band_bool,
    )

    plot_fit(
        freqs,
        bands,
        fluxes,
        flux_errs,
        limit_signs,
        refs,
        "simple_power_law",
        plot_dict,
        {"simple_power_law": {"AIC":1}},
        save_name="spl_iminuit_no_upper_limits.png",
    )

    # Add upper limits to the data and check spectral index is shallower
    refs.append("Fake upper limit")
    refs = ["Fake data"] * 4 + ["Fake upper limit"]
    limit_signs = [0] * 4 + [1]
    print(refs, limit_signs)
    ul_fit_result, band_bool = iminuit_fit_spectral_model(
        freqs,
        bands,
        fluxes,
        flux_errs,
        limit_signs,
        model_name="simple_power_law",
        likelihood="Huber",
    )
    assert fit_result.values["a"] > -1.00

    plot_dict = iminuit_interpolate_model(
        ul_fit_result,
        "simple_power_law",
        fitted_freq,
        band_bool,
    )

    plot_fit(
        freqs,
        bands,
        fluxes,
        flux_errs,
        limit_signs,
        refs,
        "simple_power_law",
        plot_dict,
        {"simple_power_law": {"AIC":1}},
        save_name="spl_iminuit_upper_limits.png",
    )
    # Assert there is a flatter spectrum with an upper limit
    assert ul_fit_result.values["a"] > fit_result.values["a"]




def test_lfto_iminuit_upper_limits():

    # Make fake data
    freqs = [10, 10, 100, 500, 1000, 10000]
    bands = [1, 1, 10, 50, 100, 1000]
    fluxes = [100, 100, 10, 5, 1, 0.1]
    flux_errs = [50, 50, 5, 0.5, 0.5, 0.05]
    refs = ["Fake data"] * 6
    limit_signs = [0] * 6
    min_freqs_MHz = 0.09 # np.min(np.array(freqs) - np.array(bands) / 2)
    max_freqs_MHz = np.max(np.array(freqs) + np.array(bands) / 2)
    fitted_freq = np.logspace(np.log10(min_freqs_MHz), np.log10(max_freqs_MHz), 100)

    # And a lower data point
    fit_result, band_bool = iminuit_fit_spectral_model(
        freqs,
        bands,
        fluxes,
        flux_errs,
        limit_signs,
        model_name="low_frequency_turn_over_power_law",
        likelihood="Huber",
    )

    plot_dict = iminuit_interpolate_model(
        fit_result,
        "low_frequency_turn_over_power_law",
        fitted_freq,
        band_bool,
    )

    plot_fit(
        freqs,
        bands,
        fluxes,
        flux_errs,
        limit_signs,
        refs,
        "low_frequency_turn_over_power_law",
        plot_dict,
        {"low_frequency_turn_over_power_law": {"AIC":1}},
        save_name="lfto_iminuit_no_upper_limits.png",
    )

    # Add upper limits to the data and check spectral index is shallower
    refs.append("Fake upper limit")
    refs = ["Fake data"] * 5 + ["Fake upper limit"]
    limit_signs = [0] * 5 + [-1]
    print(refs, limit_signs)
    ul_fit_result, band_bool = iminuit_fit_spectral_model(
        freqs,
        bands,
        fluxes,
        flux_errs,
        limit_signs,
        model_name="low_frequency_turn_over_power_law",
        likelihood="Huber",
    )
    # assert fit_result.values["a"] < -1.00

    plot_dict = iminuit_interpolate_model(
        ul_fit_result,
        "low_frequency_turn_over_power_law",
        fitted_freq,
        band_bool,
    )

    plot_fit(
        freqs,
        bands,
        fluxes,
        flux_errs,
        limit_signs,
        refs,
        "low_frequency_turn_over_power_law",
        plot_dict,
        {"low_frequency_turn_over_power_law": {"AIC":1}},
        save_name="lfto_iminuit_upper_limits.png",
    )
    # assert ul_fit_result.values["a"] < fit_result.values["a"]
    print(ul_fit_result.values)
    print(fit_result.values)
    exit(1)


if __name__ == "__main__":
    """
    Tests the relevant functions in spectral_fit.py
    """
    # introspect and run all the functions starting with 'test'
    for f in dir():
        if f.startswith("test"):
            print(f)
            globals()[f]()
