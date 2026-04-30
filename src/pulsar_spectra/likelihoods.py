"""
Likelihoods and related functions for model fitting.

Loss function = the negative log-likelihood
Cost function = the sum of the loss for all data points in a model fit
"""

import numpy as np
from scipy.special import huber
from scipy.stats import norm, t


def array_data_type_check(x):
    """Convert the input to a numpy array and check if it is a single value.

    Parameters
    ----------
    x : `float` or `int` or `list` or `np.ndarray`
        The single or array input.

    Returns
    -------
    x : `np.ndarray`
        The input x as a numpy array.
    single_value : `bool`
        Whether the input was a single value (`float` or `int`).
    """
    single_value = False
    if isinstance(x, float) or isinstance(x, int):
        x = np.array([x])
        single_value = True
    elif isinstance(x, list):
        x = np.array(x)
    return x, single_value


def huber_loss_function(sq_resi, k=1.345):
    """Compute the Huber loss function, i.e., quadratic loss when the deviation
    is less than k and linear loss otherwise.

    Parameters
    ----------
    sq_resi : `float` or `list` or `np.ndarray`
        A single or array of the squared residuals.
    k : `float`, optional
        A constant that defines at which distance the loss function starts to
        penalize outliers. |br| Default: 1.345.

    Returns
    -------
    rho : `float` or `np.ndarray`
        The modified squared residuals.
    """
    sq_resi, single_value = array_data_type_check(sq_resi)
    rho = np.empty_like(sq_resi)
    resi = np.sqrt(np.abs(sq_resi))

    # Evaluate the negative log likelihood
    for ii in range(len(sq_resi)):
        if resi[ii] < k:
            rho[ii] = 0.5 * sq_resi[ii]
        else:
            rho[ii] = k * resi[ii] - 0.5 * k**2

    if single_value:
        return rho[0]
    else:
        return rho


def t_loss_function(sq_resi, df=4):
    """Compute the t distribution loss function with df degrees of freedom.

    Parameters
    ----------
    sq_resi : `float` or `list` or `np.ndarray`
        A single or array of the squared residuals.
    df : `int`, optional
        The number of degrees of freedom. |br| Default: 4.

    Returns
    -------
    rho : `float` or `np.ndarray`
        The modified squared residuals.
    """
    sq_resi, single_value = array_data_type_check(sq_resi)
    resi = np.sqrt(np.abs(sq_resi))

    # Evaluate the negative log likelihood
    rho = -1.0 * t.logpdf(resi, df)

    if single_value:
        return rho[0]
    else:
        return rho


def gaussian_cost_function(f_y, y, sigma_y):
    """Compute the cost of a Gaussian normal PDF likelihood for a model f_y
    given data y with 1-sigma uncertainties sigma_y.

    Parameters
    ----------
    f_y : `list`
        A list of predicted values according to the model.
    y : `list`
        A list of measured values at the same frequencies as the model values.
    sigma_y : `list`
        A list of 1-sigma uncertainties corresponding to the measured values y.

    Returns
    -------
    beta : `float`
        The cost of the model fit.
    """
    f_y, _ = array_data_type_check(f_y)
    y, _ = array_data_type_check(y)
    sigma_y, _ = array_data_type_check(sigma_y)
    return -1.0 * np.sum(norm.logpdf(y, f_y, sigma_y))


def tobit_gaussian_cost_function(f_y, y_L, sigma_y_L, invert=False):
    """Compute the cost of a Gaussian normal CDF likelihood for a model f_y
    given limits y_L with 1-sigma uncertainties sigma_y_L.

    Parameters
    ----------
    f_y : `list`
        A list of predicted values according to the model.
    y_L : `list`
        A list of limits at the same frequecies as the model values.
    sigma_y_L : `list`
        A list of 1-sigma uncertainties corresponding to the measured limits y_L.
    invert : `bool`, optional
        False for lower limits, True for upper limits. |br| Default: False.

    Returns
    -------
    beta : `float`
        The cost of the model fit.
    """
    f_y, _ = array_data_type_check(f_y)
    y_L, _ = array_data_type_check(y_L)
    sigma_y_L, _ = array_data_type_check(sigma_y_L)
    if invert:
        # Upper limit
        sign = -1.0
    else:
        # Lower limit
        sign = 1.0
    resi = sign * (y_L - f_y) / sigma_y_L
    return -1.0 * np.sum(norm.logcdf(resi))


def huber_cost_function(f_y, y, sigma_y, k=1.345):
    """Compute the cost from the Huber loss function for a model f_y given data
    y with 1-sigma uncertainties sigma_y.

    Parameters
    ----------
    f_y : `list`
        A list of predicted values according to the model.
    y : `list`
        A list of measured values at the same frequency as the model values.
    sigma_y : `list`
        A list of uncertainties corresponding to the measured values y.
    k : `float`, optional
        A constant that defines at which distance the loss function starts to
        penalize outliers. |br| Default: 1.345.

    Returns
    -------
    beta : `float`
        The cost of the model fit.
    """
    f_y, _ = array_data_type_check(f_y)
    y, _ = array_data_type_check(y)
    sigma_y, _ = array_data_type_check(sigma_y)
    resi = (y - f_y) / sigma_y
    sq_resi = resi**2
    return np.sum(huber_loss_function(sq_resi, k=k))


def t_cost_function(f_y, y, sigma_y, df=4):
    """Compute the cost of a t-distribution PDF likelihood with df degrees of
    freedom for a model f_y given data y with 1-sigma uncertainties sigma_y.

    Parameters
    ----------
    f_y : `list`
        A list of predicted values according to the model.
    y : `list`
        A list of measured values at the same frequencies as the model values.
    sigma_y : `list`
        A list of 1-sigma uncertainties corresponding to the measured values y.
    df : `int`, optional
        The number of degrees of freedom. |br| Default: 4.

    Returns
    -------
    beta : `float`
        The cost of the model fit.
    """
    f_y, _ = array_data_type_check(f_y)
    y, _ = array_data_type_check(y)
    sigma_y, _ = array_data_type_check(sigma_y)
    return -1.0 * np.sum(t.logpdf(y, df, f_y, sigma_y))


def tobit_t_cost_function(f_y, y_L, sigma_y_L, df=4, invert=False):
    """Compute the cost of a t-distribution CDF likelihood with df degrees of
    freedom for a model f_y given limits y_L with 1-sigma uncertainties sigma_y_L.

    Parameters
    ----------
    f_y : `list`
        A list of predicted values according to the model.
    y_L : `list`
        A list of limits at the same frequecies as the model values.
    sigma_y_L : `list`
        A list of 1-sigma uncertainties corresponding to the measured limits y_L.
    df : `int`, optional
        The number of degrees of freedom. |br| Default: 4.
    invert : `bool`, optional
        False for lower limits, True for upper limits. |br| Default: False.

    Returns
    -------
    beta : `float`
        The cost of the model fit.
    """
    f_y, _ = array_data_type_check(f_y)
    y_L, _ = array_data_type_check(y_L)
    sigma_y_L, _ = array_data_type_check(sigma_y_L)
    if invert:
        # Upper limit
        sign = -1.0
    else:
        # Lower limit
        sign = 1.0
    resi = sign * (y_L - f_y) / sigma_y_L
    return -1.0 * np.sum(t.logcdf(resi, df))


def tobit_log_likelihood(residuals, limit_signs, loss="Gaussian", df=4):
    """Compute per-point log-likelihoods using the Tobit model to handle upper
    and lower limits. For detected points the standard PDF is used; for limit
    points the CDF is used instead.

    Parameters
    ----------
    residuals : `array_like`
        Per-point standardised residuals (y - f(x)) / sigma.
    limit_signs : `array_like`
        Per-point limit flags: +1 lower limit, -1 upper limit, 0 detection.
    loss : `str`, optional
        Distribution to use ('Gaussian', 'Huber', 't'). |br| Default: 'Gaussian'.
    df : `float`, optional
        Degrees of freedom for 't', or Huber delta cutoff for 'Huber'.
        |br| Default: 4.

    Returns
    -------
    log_likelihood : `np.ndarray`
        Per-point log-likelihoods, shape (N,).
    """
    residuals = np.asarray(residuals)
    limit_signs = np.asarray(limit_signs)
    is_limit = limit_signs.astype(bool)

    if loss == "Gaussian":
        return np.where(
            is_limit,
            norm.logcdf(-limit_signs * residuals),  # CDF for limits
            norm.logpdf(residuals),  # PDF for detections
        )
    elif loss == "Huber":
        return np.where(
            is_limit,
            norm.logcdf(-limit_signs * residuals),  # Gaussian CDF for limits
            -1.0 * huber(df, np.abs(residuals)),  # Huber pseudo-logpdf for detections
        )
    elif loss == "t":
        return np.where(
            is_limit,
            t.logcdf(-limit_signs * residuals, df),  # CDF for limits
            t.logpdf(residuals, df),  # PDF for detections
        )
    else:
        raise ValueError(f"Unknown loss function: {loss}")


def loss_function_gaussian(sq_resi):
    """Compute the loss of a Gaussian normal PDF likelihood for a model given
    the squared residuals.

    Parameters
    ----------
    sq_resi : `float` or `list` or `np.ndarray`
        A single or array of the squared residuals.

    Returns
    -------
    beta : `float` or `np.ndarray`
        The cost of the model fit.
    """
    residuals = np.sqrt(np.abs(np.asarray(sq_resi)))
    return -1.0 * tobit_log_likelihood(residuals, np.zeros_like(residuals), loss="Gaussian")


def loss_function_huber(sq_resi, k=1.345):
    """Compute the loss of a Huber loss function for a model given the squared
    residuals.

    Parameters
    ----------
    sq_resi : `float` or `list` or `np.ndarray`
        A single or array of the squared residuals.
    k : `float`, optional
        A constant that defines at which distance the loss function starts to
        penalize outliers. |br| Default: 1.345.

    Returns
    -------
    beta : `float` or `np.ndarray`
        The cost of the model fit.
    """
    residuals = np.sqrt(np.abs(np.asarray(sq_resi)))
    return -1.0 * tobit_log_likelihood(residuals, np.zeros_like(residuals), loss="Huber", df=k)


def loss_function_t(sq_resi, df=4):
    """Compute the loss of a t-distribution PDF likelihood with df degrees of
    freedom for a model given the squared residuals.

    Parameters
    ----------
    sq_resi : `float` or `list` or `np.ndarray`
        A single or array of the squared residuals.
    df : `int`, optional
        The number of degrees of freedom. |br| Default: 4.

    Returns
    -------
    beta : `float` or `np.ndarray`
        The cost of the model fit.
    """
    residuals = np.sqrt(np.abs(np.asarray(sq_resi)))
    return -1.0 * tobit_log_likelihood(residuals, np.zeros_like(residuals), loss="t", df=df)
