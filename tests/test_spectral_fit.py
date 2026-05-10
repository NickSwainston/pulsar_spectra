#! /usr/bin/env python
"""
Tests the spectral_fit.py script
"""

import numpy as np
import numpy.testing as npt
import pytest
from scipy.special import huber
from scipy.stats import norm
from scipy.stats import t as t_dist

from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.likelihoods import tobit_log_likelihood
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
    freq_all, band_all, flux_all, flux_err_all, limit_signs, ref_all = cat_list[pulsar]
    for freq, band, flux, flux_err, ref in zip(freq_all, band_all, flux_all, flux_err_all, ref_all):
        print(f"{float(freq):8.1f}{float(band):8.1f}{float(flux):12.4f}{float(flux_err):12.4f} {str(ref):20s}")
    best_fit_model_name, _, fit_results, _, _ = find_best_spectral_fit(
        pulsar,
        freq_all,
        band_all,
        flux_all,
        flux_err_all,
        limit_signs,
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
        cat_list[pulsar][5],
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
        cat_list[pulsar][5],
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
        cat_list[pulsar][5],
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
        cat_list[pulsar][5],
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
        cat_list[pulsar][5],
        method="maximum-likelihood",
        likelihood="Huber",
        plot_best=True,
        legend_style="typeset",
        plot_kwargs={"plot_bands": False},
    )


@pytest.mark.parametrize(
    "fit_method, loss",
    [
        pytest.param("bayesian-nested-sampling", "Huber", marks=pytest.mark.long),
        ("maximum-likelihood", "Gaussian"),
        ("maximum-likelihood", "Huber"),
        ("maximum-likelihood", "t"),
    ],
)
def test_iminuit_upper_limits(fit_method, loss):
    """Upper limits above the true flux must not bias the spectral fit;
    treating the same point as a detection must bias it.

    Setup:
      True model: simple power law, alpha=-1.6, c=1000 mJy at 1000 MHz.
      4 exact (noiseless) detections at [100, 300, 3000, 10000] MHz, 10% errors.
      Extra point at 30000 MHz: observed = 5x the true power-law flux (8-sigma outlier).

    As a detection the outlier biases alpha shallower by ~0.02.
    As an upper limit: true flux << limit → Tobit CDF ≈ 0 → alpha matches the baseline exactly.
    """
    alpha_true = -1.6
    v_pivot_MHz = 1000.0
    c_true_mJy = 1000.0

    # 4 exact detections — data lies exactly on the power law
    freqs_det = np.array([100.0, 300.0, 3000.0, 10000.0])
    bands_det = freqs_det / 10.0
    fluxes_det = c_true_mJy * (freqs_det / v_pivot_MHz) ** alpha_true
    flux_errs_det = 0.1 * fluxes_det

    # Extra point: 5x the true power-law flux, 10% proportional error
    freq_extra = 30000.0
    band_extra = freq_extra / 10.0
    true_flux_extra = c_true_mJy * (freq_extra / v_pivot_MHz) ** alpha_true
    obs_flux_extra = 5.0 * true_flux_extra
    obs_err_extra = 0.1 * obs_flux_extra

    freqs_all = np.append(freqs_det, freq_extra)
    bands_all = np.append(bands_det, band_extra)
    fluxes_all = np.append(fluxes_det, obs_flux_extra)
    flux_errs_all = np.append(flux_errs_det, obs_err_extra)

    # Fit 1: baseline — 4 exact detections only
    _, _, fit_results_base, _, _ = find_best_spectral_fit(
        "baseline_no_upper_limits",
        freqs_det,
        bands_det,
        fluxes_det,
        flux_errs_det,
        [0] * 4,
        ["Fake data"] * 4,
        method=fit_method,
        likelihood=loss,
        plot_compare=True,
    )

    # Fit 2: 5 detections including the outlier
    _, _, fit_results_detect, _, _ = find_best_spectral_fit(
        "no_upper_limits",
        freqs_all,
        bands_all,
        fluxes_all,
        flux_errs_all,
        [0] * 5,
        ["Fake data"] * 5,
        method=fit_method,
        likelihood=loss,
        plot_compare=True,
    )

    # Fit 3: outlier treated as an upper limit
    _, _, fit_results_upper, _, _ = find_best_spectral_fit(
        "upper_limits",
        freqs_all,
        bands_all,
        fluxes_all,
        flux_errs_all,
        [0, 0, 0, 0, -1],
        ["Fake data"] * 4 + ["Fake upper limit"],
        method=fit_method,
        likelihood=loss,
        plot_compare=True,
    )

    alpha_base = fit_results_base["simple_power_law"].values["a"]
    alpha_detect = fit_results_detect["simple_power_law"].values["a"]
    alpha_upper = fit_results_upper["simple_power_law"].values["a"]

    print(f"alpha_base   = {alpha_base:.4f}")
    print(f"alpha_detect = {alpha_detect:.4f}  shift={alpha_detect - alpha_base:+.4f}")
    print(f"alpha_upper  = {alpha_upper:.4f}  shift={alpha_upper - alpha_base:+.4f}")

    # 1. Baseline exactly recovers the true alpha (noiseless data, MLE is exact)
    npt.assert_allclose(
        alpha_base,
        alpha_true,
        atol=1e-3,
        err_msg=f"Baseline should recover alpha_true={alpha_true}, got {alpha_base:.4f}",
    )

    # 2. Outlier treated as detection measurably biases alpha shallower
    assert alpha_detect > alpha_base + 0.002, (
        f"Detection outlier should bias alpha shallower: alpha_detect={alpha_detect:.4f}, alpha_base={alpha_base:.4f}"
    )

    # 3. Outlier treated as upper limit gives the exact baseline result
    npt.assert_allclose(
        alpha_upper,
        alpha_base,
        atol=1e-3,
        err_msg=f"Upper limit fit should match baseline; got alpha_upper={alpha_upper:.4f}",
    )

    # 4. Upper limit is at least 5x closer to ground truth than the biased detection
    assert abs(alpha_upper - alpha_true) < abs(alpha_detect - alpha_true) / 5, (
        f"Upper limit (alpha={alpha_upper:.4f}) should be much closer to alpha_true={alpha_true} "
        f"than detection (alpha={alpha_detect:.4f})"
    )


@pytest.mark.parametrize("loss", ["Gaussian", "Huber", "t"])
def test_tobit_log_likelihood_properties(loss):
    """Directly test the Tobit log-likelihood for correct mathematical properties.

    For an upper limit (limit_sign=-1), the residual is (flux_limit - model_flux)/err:
      - residual >> 0  model far below limit → non-constraining → likelihood ≈ 0
      - residual = 0   model exactly at limit → likelihood = log(0.5) exactly
      - residual << 0  model far above limit → penalised → likelihood negative

    The log(0.5) boundary is universal across all three loss types.  The argument
    is purely one of symmetry: all CDFs used (norm for Gaussian/Huber, t for t-loss)
    are symmetric distributions, so CDF(0) = 0.5 → logCDF(0) = log(0.5) always.

    Gaussian and Huber limits are identical — both use norm.logcdf.  Only detections
    differ between them (Huber uses the Huber pseudo-logpdf; Gaussian uses norm.logpdf).
    The t-loss uses t.logcdf for limits, which has heavier tails: violated limits are
    penalised less harshly and satisfied limits lose slightly more likelihood than
    Gaussian/Huber.

    For a lower limit (limit_sign=+1) the monotonicity is reversed.
    """
    residuals = np.array([-3.0, -1.0, 0.0, 1.0, 3.0])

    # --- Upper limits (limit_sign = -1) ---
    ll_upper = tobit_log_likelihood(residuals, np.full(5, -1), loss=loss)
    # Likelihood must be strictly monotonically increasing as model drops below the limit
    assert np.all(np.diff(ll_upper) > 0), (
        "Upper-limit log-likelihood must increase monotonically as model moves below the limit"
    )
    # logCDF(0) = log(0.5) for ALL loss types: all CDFs used are symmetric around 0,
    # so CDF(0) = 0.5 exactly regardless of whether the distribution is Gaussian or t.
    npt.assert_allclose(ll_upper[2], np.log(0.5), atol=1e-10)
    # Model far below limit: likelihood approaches 0 (non-constraining).
    # The t-distribution has heavier tails so this converges more slowly: use -0.05.
    assert ll_upper[-1] > -0.05, "Non-constraining upper limit should give likelihood near 0"
    # Model far above limit: penalised.
    # t-distribution penalises less harshly than Gaussian (heavier tails): use -3.0.
    assert ll_upper[0] < -3.0, "Violated upper limit should give negative likelihood"

    # --- Lower limits (limit_sign = +1) — exactly opposite monotonicity ---
    ll_lower = tobit_log_likelihood(residuals, np.full(5, 1), loss=loss)
    assert np.all(np.diff(ll_lower) < 0), (
        "Lower-limit log-likelihood must decrease monotonically as model moves above the limit"
    )
    npt.assert_allclose(ll_lower[2], np.log(0.5), atol=1e-10)

    # --- Symmetry: upper and lower limits are mirror images ---
    # Holds for all loss types because all CDFs used are symmetric around 0.
    npt.assert_allclose(ll_upper, ll_lower[::-1], atol=1e-10)

    # --- Detections (limit_sign = 0): must match the per-loss detection function ---
    ll_detect = tobit_log_likelihood(residuals, np.zeros(5, dtype=int), loss=loss)
    if loss == "Gaussian":
        expected = norm.logpdf(residuals)
    elif loss == "Huber":
        # Huber pseudo-logpdf with delta=df=4 (the default in tobit_log_likelihood)
        expected = -huber(4, np.abs(residuals))
    else:  # t
        expected = t_dist.logpdf(residuals, df=4)
    npt.assert_allclose(ll_detect, expected, atol=1e-12)
