#!/usr/bin/env python

import argparse
import logging

from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

logger = logging.getLogger(__name__)

LOG_LEVELS = dict(
    DEBUG=logging.DEBUG, INFO=logging.INFO, WARNING=logging.WARNING, ERROR=logging.ERROR, CRITICAL=logging.CRITICAL
)


def setup_logger(name: str | None = None, log_level: str | int = "INFO") -> None:
    """Clear all previous handlers and add a new custom stream handler.

    Parameters
    ----------
    name : `str`, optional
        The name of the logger. Note that `None` returns the root logger.
        |br| Default: `None`.
    log_level : `str` or `int`, optional
        The name of the logging level or the effective logging level.
        |br| Default: 'INFO'.
    """
    # If a string was provided, map it to the effective level
    if isinstance(log_level, str):
        log_level = LOG_LEVELS[log_level.upper()]

    # Get the logger
    logger = logging.getLogger(name)

    # Remove any previous handlers
    logger.handlers.clear()

    # Set the verbosity level of the logger
    logger.setLevel(log_level)

    # Get channel handler
    ch = logging.StreamHandler()

    # Set the verbosity level of ch
    ch.setLevel(log_level)

    # Set the formatter of ch
    formatter = logging.Formatter(
        fmt="[%(asctime)s %(name)s %(lineno)-4d %(levelname)-8s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(formatter)

    # Add ch to logger
    logger.addHandler(ch)

    # Do not propagate to other packages
    logger.propagate = False


def quick_fit(
    pulsars,
    method="maximum-likelihood",
    plot_type="best",
    legend_style="raw",
    point_estimate="max-std",
    likelihood="Huber",
    sampler_kwargs=None,
):
    cat_list = collect_catalogue_fluxes()
    for pulsar in pulsars:
        logger.info(f"Fitting {pulsar}")
        freq_all, band_all, flux_all, flux_err_all, ref_all = cat_list[pulsar]

        if len(freq_all) < 1:
            logger.error(f"No spectral data available for PSR {pulsar}")
            continue

        for freq, band, flux, flux_err, ref in zip(freq_all, band_all, flux_all, flux_err_all, ref_all):
            if band is None:
                logger.debug(f"{float(freq):8.1f}    None{float(flux):12.4f}{float(flux_err):12.4f} {str(ref):20s}")
            else:
                logger.debug(
                    f"{float(freq):8.1f}{float(band):8.1f}{float(flux):12.4f}{float(flux_err):12.4f} {str(ref):20s}"
                )  # noqa: E501
        logger.debug(f"len(freq_all): {len(freq_all)}")
        logger.debug(f"len(band_all): {len(band_all)}")
        logger.debug(f"len(flux_all): {len(flux_all)}")
        logger.debug(f"len(flux_err_all): {len(flux_err_all)}")
        logger.debug(ref_all)

        plot_opt = dict()
        if plot_type == "all":
            plot_opt["plot_all"] = True
        elif plot_type == "best":
            plot_opt["plot_best"] = True
        elif plot_type == "compare":
            plot_opt["plot_compare"] = True
        else:
            logger.warning("No plotting action selected.")

        best_fit_model_name, p_best, fit_results, aic_dict, plot_dicts = find_best_spectral_fit(
            pulsar,
            freq_all,
            band_all,
            flux_all,
            flux_err_all,
            ref_all,
            method=method,
            likelihood=likelihood,
            legend_style=legend_style,
            legend_point_estimate=point_estimate,
            sampler_kwargs=sampler_kwargs,
            **plot_opt,
        )

        logger.info(f"{pulsar} fit: {best_fit_model_name} (p_best={p_best:.3f})")

        # TODO: implement a package-agnostic method for printing results
        if method == "maximum-likelihood" and fit_results is not None:
            result = fit_results[best_fit_model_name]
            for p, v, e in zip(result.parameters, result.values, result.errors):
                if p.startswith("v"):
                    logger.info(f"{p} = {v / 1e6:8.1f} +/- {e / 1e6:8.1} MHz")
                else:
                    logger.info(f"{p} = {v:.5f} +/- {e:.5}")


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Perform a spectral fit on the input pulsars.",
    )
    parser.add_argument(
        "-p",
        "--pulsars",
        type=str,
        nargs="*",
        help="Space seperated list of pulsar J names.",
        required=True,
    )
    parser.add_argument(
        "-L",
        "--loglvl",
        type=str,
        choices=LOG_LEVELS,
        default="INFO",
        help="Logger verbosity level.",
    )
    parser.add_argument(
        "-m",
        "--method",
        type=str,
        choices=["maximum-likelihood", "bayesian-nested-sampling"],
        default="maximum-likelihood",
        help=(
            "Fitting method. 'maximum-likelihood' for maximum-likelihood fitting using iminuit; "
            "'bayesian-nested-sampling' for Bayesian nested sampling using Bilby/Dynesty."
        ),
    )
    parser.add_argument(
        "-t",
        "--plot_type",
        type=str,
        choices=["best", "all", "compare"],
        default="best",
        help=(
            "Type of output plot(s). "
            "'best' for just the best-fit model; "
            "'all' for all fitted models; "
            "'compare' for all fitted models in one plot."
        ),
    )
    parser.add_argument(
        "-s",
        "--legend_style",
        type=str,
        choices=["raw", "typeset", "compact"],
        default="raw",
        help=(
            "Legend style. "
            "'raw' for code-like formatting; "
            "'typeset' for LaTeX typeset formatting; "
            "'compact' for a simpler legend inside the bbox."
        ),
    )
    parser.add_argument(
        "-e",
        "--point_estimate",
        type=str,
        choices=["max-std", "med-ci"],
        default="max-std",
        help=(
            "The point estimate reported in the legend (only applies to the "
            "nested sampling method). "
            "'max-std' for the maximum +/- 1 standard deviation; "
            "'med-ci' for the median and the 68%% credible interval."
        ),
    )
    parser.add_argument(
        "-l",
        "--likelihood",
        type=str,
        choices=["Gaussian", "Huber", "t"],
        default="Huber",
        help=(
            "Likelihood distribution to use. 'Gaussian' for ordinary least squares; "
            "'Huber' or 't' for robust least squares."
        ),
    )
    parser.add_argument(
        "-n",
        "--npool",
        type=int,
        default=1,
        help=(
            "The number of available CPUs to create pool objects for parallelisation. "
            "This options is only applicable to the nested sampling method."
        ),
    )
    args = parser.parse_args()

    setup_logger("pulsar_spectra", log_level=args.loglvl)
    if args.method == "bayesian-nested-sampling":
        # bilby needs to be imported to initialise the logger
        from pulsar_spectra.fitters import bayesian  # noqa: F401

        setup_logger("bilby", log_level=args.loglvl)

    quick_fit(
        args.pulsars,
        method=args.method,
        plot_type=args.plot_type,
        legend_style=args.legend_style,
        point_estimate=args.point_estimate,
        likelihood=args.likelihood,
        sampler_kwargs={"npool": args.npool},
    )


if __name__ == "__main__":
    main()
