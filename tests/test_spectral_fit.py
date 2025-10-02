#! /usr/bin/env python
"""
Tests the spectral_fit.py script
"""

import numpy as np
import pytest

from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

spectral_fit_tests = [
    ("J0415+6954", "simple_power_law", ['Bilous_2016', 'Lorimer_1995b', 'Seiradakis_1995', 'Sanidas_2019', 'Dewey_1985', 'McEwen_2020', 'Malofeev_2000']),
    ("J1327-6222", "broken_power_law", ['Jankowski_2018', 'Johnston_1992', 'Murphy_2017', 'Jankowski_2019', 'Bates_2011', 'Mantovanini_2025', 'Manchester_1978a', 'Hobbs_2004a', 'Johnston_2018', 'Keith_2024', 'van_Ommen_1997']),
    ("J0125-2327", "high_frequency_cut_off_power_law", ['McEwen_2020', 'Lee_2025', 'Gitika_2023']),
    ("J0024-7204C", "low_frequency_turn_over_power_law", ['Zhang_2019', 'Robinson_1995']),
    ("J0304+1932", "double_turn_over_spectrum", ['Kumar_2025', 'Frail_2016', 'Han_1999', 'Seiradakis_1995', 'Bilous_2020', 'Slee_1986', 'Stovall_2015', 'Deneva_2024', 'Keith_2024', 'Kravtsov_2022', 'Kijak_1998', 'Bhat_2023', 'Malofeev_2000', 'Izvekova_1981', 'Hoensbroech_1997', 'Manchester_1978a', 'Johnston_2018', 'Weisberg_1999', 'Bilous_2016', 'Lorimer_1995b']),
]
@pytest.mark.parametrize("pulsar, exp_model_name, frozen_refs", spectral_fit_tests)
def test_find_best_spectral_fit(pulsar, exp_model_name, frozen_refs):
    """Tests the find_best_spectral_fit funtion."""
    # limit the input publications to prevent future additions making the tests fail
    cat_list = collect_catalogue_fluxes(only_use=frozen_refs)
    # Use some ref markers to test they can be altered
    ref_markers = {
        "Jankowski_2018": ("k", "d", 7),  # black thin diamond
        "Jankowski_2019": ("#b6dbff", "*", 9),  # light blue star
        "Xue_2017": ("y", "P", 7.5),  # yellow thick plus)
    }

    print(f"\nFitting {pulsar}")
    freq_all, band_all, flux_all, flux_err_all, ref_all = cat_list[pulsar]
    for freq, band, flux, flux_err, ref in zip(freq_all, band_all, flux_all, flux_err_all, ref_all):
        print(f"{float(freq):8.1f}{float(band):8.1f}{float(flux):12.4f}{float(flux_err):12.4f} {str(ref):20s}")
    model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(
        pulsar,
        freq_all,
        band_all,
        flux_all,
        flux_err_all,
        ref_all,
        plot_compare=True,
        ref_markers=ref_markers,
    )
    for p, v, e in zip(iminuit_result.parameters, iminuit_result.values, iminuit_result.errors):
        if p.startswith("v"):
            print(f"{p} = {v / 1e6:8.1f} +/- {e / 1e6:8.1} MHz")
        else:
            print(f"{p} = {v:.5f} +/- {e:.5}")
    np.testing.assert_string_equal(model_name, exp_model_name)


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
        plot_best=True,
    )
    print("Plotting Best alternate style and fit range")
    find_best_spectral_fit(
        pulsar,
        cat_list[pulsar][0],
        cat_list[pulsar][1],
        cat_list[pulsar][2],
        cat_list[pulsar][3],
        cat_list[pulsar][4],
        plot_best=True,
        alternate_style=True,
        fit_range=(10, 1100),
    )


if __name__ == "__main__":
    """
    Tests the relevant functions in spectral_fit.py
    """
    # introspect and run all the functions starting with 'test'
    for f in dir():
        if f.startswith("test"):
            print(f)
            globals()[f]()
