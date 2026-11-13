"""Deterministic portfolio risk metrics with explicit return conventions.

Decimal simple returns; VaR/ES are positive loss thresholds. Historical risk
estimates are descriptive and do not constitute reliable future guarantees.
"""
from __future__ import annotations
from math import sqrt
from statistics import stdev


def _check(returns: list[float]) -> None:
    if not returns or any(r <= -1 for r in returns):
        raise ValueError("Require nonempty decimal simple returns greater than -100%")


def annualized_volatility(returns: list[float], *, periods_per_year: int = 252) -> float:
    _check(returns)
    if len(returns) < 2 or periods_per_year <= 0:
        raise ValueError("At least 2 returns and a positive annualization factor required")
    return stdev(returns) * sqrt(periods_per_year)


def max_drawdown(returns: list[float]) -> float:
    _check(returns)
    wealth, peak, worst = 1.0, 1.0, 0.0
    for ret in returns:
        wealth *= 1 + ret
        peak = max(peak, wealth)
        worst = max(worst, 1 - wealth / peak)
    return worst


def historical_var_es(returns: list[float], *, confidence: float = .95) -> tuple[float, float]:
    """Nearest-rank empirical VaR and average loss in the worst tail.

    Small samples are unstable; in production report sample counts and backtests.
    """
    _check(returns)
    if not 0 < confidence < 1:
        raise ValueError("confidence must be in (0,1)")
    from math import ceil
    losses = sorted((-r for r in returns), reverse=True)
    n_tail = max(1, ceil((1 - confidence) * len(losses)))
    var = max(0.0, losses[n_tail - 1])
    es = max(0.0, sum(losses[:n_tail]) / n_tail)
    return var, es


def equal_weight_returns(asset_period_returns: list[list[float]]) -> list[float]:
    if not asset_period_returns or not asset_period_returns[0]:
        raise ValueError("Nonempty asset return matrix required")
    n = len(asset_period_returns[0])
    if any(len(series) != n for series in asset_period_returns):
        raise ValueError("Assets must share aligned observation periods")
    for series in asset_period_returns:
        _check(series)
    return [sum(series[t] for series in asset_period_returns) / len(asset_period_returns) for t in range(n)]
