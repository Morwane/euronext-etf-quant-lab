import pandas as pd

from src.simulation import (
    block_bootstrap_paths,
    distribution_summary,
    parametric_monte_carlo_paths,
    terminal_distribution,
)


def test_simulation_paths_have_expected_shape():
    returns = pd.Series([0.001, -0.002, 0.003, 0.0, 0.002] * 80)
    mc = parametric_monte_carlo_paths(returns, horizon_days=21, n_paths=50, seed=1)
    boot = block_bootstrap_paths(returns, horizon_days=21, n_paths=50, block_size=5, seed=1)
    assert mc.shape == (21, 50)
    assert boot.shape == (21, 50)


def test_distribution_summary_contains_tail_metrics():
    returns = pd.Series([0.001, -0.002, 0.003, 0.0, 0.002] * 80)
    paths = block_bootstrap_paths(returns, horizon_days=21, n_paths=50, block_size=5, seed=1)
    summary = distribution_summary(terminal_distribution(paths), "test")
    assert "test_p05" in summary
    assert "test_expected_shortfall_5" in summary

