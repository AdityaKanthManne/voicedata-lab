import pytest
from voicedata.risk import annualized_volatility, max_drawdown, historical_var_es, equal_weight_returns


def test_max_drawdown():
    assert max_drawdown([.1, -.2, .1]) == pytest.approx(.2)


def test_var_es_and_equal_weight():
    portfolio = equal_weight_returns([[.1, -.1], [0, -.3]])
    assert portfolio == pytest.approx([.05, -.2])
    var, es = historical_var_es([-.2, -.1, 0, .05], confidence=.75)
    assert var == pytest.approx(.2)
    assert es == pytest.approx(.2)


def test_bad_returns():
    with pytest.raises(ValueError):
        annualized_volatility([.01])
    with pytest.raises(ValueError):
        equal_weight_returns([[.1], [.2, .3]])
