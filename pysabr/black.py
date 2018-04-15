import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize


def lognormal_call(k, f, t, v, r, cp='call'):
    """
    Computes the premium for a call or put option using a lognormal vol
    """
    d1 = (np.log(f/k) + v**2 * t/2) / (v * t**0.5)
    d2 = d1 - v * t**0.5
    if cp == 'call':
        pv = np.exp(-r*t) * (f * norm.cdf(d1) - k * norm.cdf(d2))
    elif cp == 'put':
        pv = np.exp(-r*t) * (-f * norm.cdf(-d1) + k * norm.cdf(-d2))
    else:
        pv = 0
    return pv


def shifted_lognormal_call(k, f, s, t, v, r, cp='call'):
    """
    Computes the premium for a call or put option using a shifted-lognormal vol
    """
    return lognormal_call(k+s, f+s, t, v, r, cp)


def normal_call(k, f, t, v, r, cp='call'):
    """
    Computes the premium for a call or put option using a normal vol
    """
    d1 = (f - k) / (v * t**0.5)
    cp_sign = {'call': 1., 'put': -1.}[cp]
    pv = np.exp(-r*t) * (
        cp_sign * (f - k) * norm.cdf(cp_sign * d1) +
        v * (t / (2 * np.pi))**0.5 * np.exp(-d1**2 / 2))
    return pv


def normal_to_shifted_lognormal(k, f, s, t, v_n):
    """
    Converts a normal vol for a given strike to a shited-lognormal vol.
    """
    target_premium = normal_call(k, f, t, v_n, 0.)
    v_sln_0 = v_n / (f + s)

    def premium_square_error(v_sln):
        premium = shifted_lognormal_call(k, f, s, t, v_sln, 0.)
        return 1e5 * (premium - target_premium) ** 2

    res = minimize(fun=premium_square_error, x0=v_sln_0, method='BFGS')
    return res.x[0]
