"""
Functions for selecting the best-fit model.
"""

import numpy as np

from .models import model_settings


def compute_aicc(beta: float, k: int, n: int) -> float:
    """Compute the Akaike Information Criterion corrected for small samples (AICc).

    Parameters
    ----------
    beta : `float`
        The minimised negative log-likelihood.
    k : `int`
        The number of free and varying model parameters.
    n : `int`
        The sample size.

    Returns
    -------
    """
    assert n > (k - 1)
    return 2 * beta + 2 * k + (2 * k * (k + 1)) / (n - k - 1)


def select_best_fit_model(beta_dict: dict, n: int) -> tuple[dict, str, float]:
    """Select the best-fit model based on the AICc.

    Parameters
    ----------
    beta_dict : `dict`
        A dictionary of beta values organised by model name.
    n : `int`
        The sample size.

    Returns
    -------
    aic_dict : `dict`
        A dictionary of AICc values organised by model name.
    best_fit_model_name : `str`
        The name of the best-fit model from :py:meth:`pulsar_spectra.models`.
    p_best : `float`
        The probability that the selected model is the best-fitting model out
        of the models compared.
    """
    model_dict = model_settings()

    model_idx_list = []
    aic_list = []
    aic_dict = {}
    for model_idx, model_name in enumerate(beta_dict.keys()):
        beta = beta_dict[model_name]

        # Compute the AICc for the data and model
        k = len(model_dict[model_name][2])
        aic = compute_aicc(beta, k, n)

        # Store the results
        model_idx_list.append(model_idx)
        aic_list.append(aic)
        aic_dict[model_name] = aic

    # Determing the name of the model with the lowest AICc
    best_aic_idx = aic_list.index(min(aic_list))
    best_fit_model_name = list(beta_dict.keys())[model_idx_list[best_aic_idx]]

    # Compute Akaike weights
    aic_arr = np.array(aic_list)
    aic_min = np.min(aic_arr)
    weights = np.exp(-0.5 * np.abs(aic_arr - aic_min))

    # Compute p_best
    p_best = 1 / np.sum(weights)

    return aic_dict, best_fit_model_name, p_best
