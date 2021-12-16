#! /usr/bin/env python
"""
Tests the spectral_fit.py script
"""
import os
import numpy as np
from numpy.testing import assert_almost_equal
import psrqpy
import pandas as pd

from pulsar_spectra import catalogues
from pulsar_spectra.spectral_fit import find_best_spectral_fit
from pulsar_spectra.catalogues import flux_from_atnf, collect_catalogue_fluxes

import logging
logger = logging.getLogger(__name__)


def test_find_best_spectral_fit():
    """Tests the find_best_spectral_fit funtion.
    """
    cat_dict, cat_list = collect_catalogue_fluxes()
    print(cat_dict)
    pulsars = ['J0034-0534','J0953+0755', 'J1645-0317']
    for pulsar in pulsars:
        print(f"\nFitting {pulsar}")
        print(cat_dict[pulsar])
        print(cat_list[pulsar])
        freq_all = np.array(cat_list[pulsar][0])*1e6
        flux_all = np.array(cat_list[pulsar][1])*1e-3
        flux_err_all = np.array(cat_list[pulsar][2])*1e-3
        print(freq_all, flux_all, flux_err_all)
        models, fit_results = find_best_spectral_fit(pulsar, freq_all, flux_all, flux_err_all, plot=True)
        print(models)

if __name__ == "__main__":
    """
    Tests the relevant functions in spectral_fit.py
    """
    # introspect and run all the functions starting with 'test'
    for f in dir():
        if f.startswith('test'):
            print(f)
            globals()[f]()
