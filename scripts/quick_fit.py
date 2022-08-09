#!/usr/bin/env python

import argparse

from pulsar_spectra.spectral_fit import find_best_spectral_fit
from pulsar_spectra.catalogue import collect_catalogue_fluxes


def quick_fit(pulsars):
    cat_list = collect_catalogue_fluxes()
    for pulsar in pulsars:
        print(f"\nFitting {pulsar}")
        freq_all, flux_all, flux_err_all, ref_all = cat_list[pulsar]

        for freq, flux, flux_err, ref in zip(freq_all, flux_all, flux_err_all, ref_all):
            print(f"{float(freq):8.1f}{float(flux):12.4f}{float(flux_err):12.4f} {str(ref):20s}")

        model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(
            pulsar, freq_all, flux_all, flux_err_all, ref_all,
            plot_compare=True,
        )
        print(f"\n{pulsar} fit: {model_name}")
        for p, v, e in zip(iminuit_result.parameters, iminuit_result.values, iminuit_result.errors):
            if p.startswith("v"):
                print(f"{p} = {v/1e6:8.1f} +/- {e/1e6:8.1} MHz")
            else:
                print(f"{p} = {v:.5f} +/- {e:.5}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Perform a spectral fit on the input pulsars.')
    parser.add_argument('-p', '--pulsars', type=str, nargs='*',
                        help='Space seperated list of pulsar J names.')
    args = parser.parse_args()

    quick_fit(args.pulsars)