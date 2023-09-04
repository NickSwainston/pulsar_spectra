#!/usr/bin/env python

import argparse
import logging
import sys

from pulsar_spectra.spectral_fit import find_best_spectral_fit
from pulsar_spectra.catalogue import collect_catalogue_fluxes


logger = logging.getLogger(__name__)


def quick_fit(pulsars):
    cat_list = collect_catalogue_fluxes()
    for pulsar in pulsars:
        logger.info(f"\nFitting {pulsar}")
        freq_all, band_all, flux_all, flux_err_all, ref_all = cat_list[pulsar]

        for freq, band, flux, flux_err, ref in zip(freq_all, band_all, flux_all, flux_err_all, ref_all):
            if band is None:
                logger.debug(f"{float(freq):8.1f}    None{float(flux):12.4f}{float(flux_err):12.4f} {str(ref):20s}")
            else:
                logger.debug(f"{float(freq):8.1f}{float(band):8.1f}{float(flux):12.4f}{float(flux_err):12.4f} {str(ref):20s}")
        logger.debug(f"len(freq_all): {len(freq_all)}")
        logger.debug(f"len(band_all): {len(band_all)}")
        logger.debug(f"len(flux_all): {len(flux_all)}")
        logger.debug(f"len(flux_err_all): {len(flux_err_all)}")
        logger.debug(ref_all)
        model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(
            pulsar, freq_all, band_all, flux_all, flux_err_all, ref_all,
            plot_best=True
        )
        logger.info(f"\n{pulsar} fit: {model_name}")
        if iminuit_result is None:
            continue
        for p, v, e in zip(iminuit_result.parameters, iminuit_result.values, iminuit_result.errors):
            if p.startswith("v"):
                logger.info(f"{p} = {v/1e6:8.1f} +/- {e/1e6:8.1} MHz")
            else:
                logger.info(f"{p} = {v:.5f} +/- {e:.5}")

if __name__ == '__main__':
    # Dictionary for choosing log-levels
    loglevels = dict(DEBUG=logging.DEBUG,
                     INFO=logging.INFO,
                     WARNING=logging.WARNING)

    parser = argparse.ArgumentParser(description='Perform a spectral fit on the input pulsars.')
    parser.add_argument('-p', '--pulsars', type=str, nargs='*',
                        help='Space seperated list of pulsar J names.')

    parser.add_argument("-L", "--loglvl", type=str, default="INFO",
                        help="Logger verbosity level. Default: INFO")
    args = parser.parse_args()

    formatter = logging.Formatter('%(asctime)s  %(name)s  %(lineno)-4d  %(levelname)-9s :: %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    # Set up local logger
    logger.setLevel(loglevels[args.loglvl])
    logger.addHandler(ch)
    logger.propagate = False
    # Loop over imported vcstools modules and set up their loggers
    for imported_module in sys.modules.keys():
        if imported_module.startswith('pulsar_spectra'):
            logging.getLogger(imported_module).setLevel(loglevels[args.loglvl])
            logging.getLogger(imported_module).addHandler(ch)
            logging.getLogger(imported_module).propagate = False

    quick_fit(args.pulsars)