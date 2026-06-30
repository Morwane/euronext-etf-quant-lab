from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "figures" / "project1"
METRICS_CSV = ROOT / "data" / "processed" / "project1_market_quality.csv"
RAW_DIR = ROOT / "data" / "raw_lseg_project1_nav_core"

COLORS = {
    "SPY": "#2a9d8f",
    "EFA": "#457b9d",
    "EEM": "#e76f51",
}


def _style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.22,
            "font.size": 10.5,
            "axes.titleweight": "bold",
            "axes.titlepad": 10,
        }
    )


def _load_raw(ric: str) -> pd.DataFrame:
    path = RAW_DIR / f"{ric}.csv"
    df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date").sort_index()
    return df[~df.index.duplicated(keep="last")]


def _spread_bps(df: pd.DataFrame) -> pd.Series:
    mid = (df["bid"] + df["ask"]) / 2.0
    return ((df["ask"] - df["bid"]) / mid * 10_000.0).replace([np.inf, -np.inf], np.nan)


def _premium_bps(df: pd.DataFrame) -> pd.Series:
    aligned = df[["price", "nav"]].dropna()
    return ((aligned["price"] - aligned["nav"]) / aligned["nav"] * 10_000.0).replace([np.inf, -np.inf], np.nan)


def _annotate_hbars(ax, values: pd.Series, fmt: str) -> None:
    if values.empty:
        return
    right = max(values.max(), 0)
    left = min(values.min(), 0)
    span = max(right - left, 1e-9)
    for i, value in enumerate(values):
        if value >= 0:
            ax.text(value + span * 0.025, i, fmt.format(value), va="center", ha="left", fontsize=9)
        else:
            ax.text(span * 0.025, i, fmt.format(value), va="center", ha="left", fontsize=9)


def summary_dashboard(metrics: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(13, 8.5))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.05], hspace=0.45, wspace=0.38)
    fig.suptitle("ETF Market-Quality Dashboard - LSEG data", fontsize=16, fontweight="bold", y=0.98)

    cards = [
        ("quoted_spread_bps_20d_median", "Quoted spread\n20d median", "bps", "{:.2f}"),
        ("premium_discount_bps_20d_median", "Premium/discount\n20d median", "bps", "{:+.2f}"),
        ("tracking_error_63d", "Tracking error\n63d ann.", "%", "{:.1%}"),
        ("quality_risk_score", "Monitoring\npriority score", "", "{:.2f}"),
    ]
    axes = [fig.add_subplot(gs[0, i]) for i in range(3)] + [fig.add_subplot(gs[1, 0])]
    ordered = metrics.sort_values("quality_risk_score", ascending=True)
    for ax, (column, title, unit, fmt), _ in zip(axes, cards, axes):
        vals = ordered.set_index("ric")[column]
        colors = [COLORS.get(ric, "#6c757d") for ric in vals.index]
        ax.barh(vals.index, vals.values, color=colors)
        ax.axvline(0, color="#333333", linewidth=0.8)
        ax.set_title(title)
        ax.set_xlabel(unit)
        _annotate_hbars(ax, vals, fmt)

    ax = fig.add_subplot(gs[1, 1:])
    ax.axis("off")
    best = metrics.sort_values("quality_risk_score").iloc[0]
    watch = metrics.sort_values("quality_risk_score", ascending=False).iloc[0]
    text = (
        "Read this chart\n\n"
        f"- Most efficient in this sample: {best['ric']} "
        f"(spread {best['quoted_spread_bps_20d_median']:.2f} bps, "
        f"NAV gap {best['premium_discount_bps_20d_median']:+.2f} bps).\n"
        f"- Highest monitoring priority: {watch['ric']} "
        f"(tracking error {watch['tracking_error_63d']:.1%}, "
        f"spread {watch['quoted_spread_bps_20d_median']:.2f} bps).\n"
        "- Lower spread, lower NAV gap and lower tracking error indicate better ETF market quality.\n"
        "- This is an analytics monitor, not a PnL trading strategy."
    )
    ax.text(
        0.02,
        0.92,
        text,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=11,
        bbox={"boxstyle": "round,pad=0.6", "facecolor": "#f8f9fa", "edgecolor": "#ced4da"},
    )
    fig.savefig(OUT / "market_quality_dashboard.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def tracking_vs_spread(metrics: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 6))
    for _, row in metrics.iterrows():
        ric = row["ric"]
        ax.scatter(
            row["quoted_spread_bps_20d_median"],
            row["tracking_error_63d"],
            s=220 + row["ann_vol_63d"] * 850,
            color=COLORS.get(ric, "#6c757d"),
            edgecolor="white",
            linewidth=1.2,
            alpha=0.92,
        )
        ax.text(
            row["quoted_spread_bps_20d_median"] + 0.035,
            row["tracking_error_63d"],
            f"{ric}\n{row['benchmark_name']}",
            va="center",
            fontsize=9,
        )
    ax.set_title("Liquidity vs benchmark tracking")
    ax.set_xlabel("20d median quoted spread (bps) - lower is better")
    ax.set_ylabel("63d annualized tracking error - lower is better")
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    ax.text(
        0.02,
        0.96,
        "Bubble size = realized volatility",
        transform=ax.transAxes,
        va="top",
        fontsize=9,
        color="#495057",
    )
    fig.tight_layout()
    fig.savefig(OUT / "liquidity_vs_tracking.png", dpi=180)
    plt.close(fig)


def premium_discount_timeseries(rics: list[str]) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.8))
    for ric in rics:
        df = _load_raw(ric)
        premium = _premium_bps(df).rolling(5).mean().dropna()
        ax.plot(premium.index, premium.values, label=ric, color=COLORS.get(ric), linewidth=1.7)
    ax.axhline(0, color="#333333", linewidth=0.9)
    ax.axhspan(-10, 10, color="#2a9d8f", alpha=0.07, label="+/-10 bps band")
    ax.set_title("ETF price vs NAV: premium / discount through time")
    ax.set_ylabel("Premium / discount to NAV (bps), 5d average")
    ax.legend(frameon=False, ncol=4, loc="upper left")
    ax.text(
        0.01,
        0.02,
        "Positive = ETF trades above NAV; negative = below NAV.",
        transform=ax.transAxes,
        fontsize=9,
        color="#495057",
    )
    fig.tight_layout()
    fig.savefig(OUT / "premium_discount_timeseries.png", dpi=180)
    plt.close(fig)


def spread_timeseries(rics: list[str]) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.8))
    for ric in rics:
        df = _load_raw(ric)
        spread = _spread_bps(df).rolling(20).median().dropna()
        ax.plot(spread.index, spread.values, label=ric, color=COLORS.get(ric), linewidth=1.7)
    ax.set_title("Quoted spread through time")
    ax.set_ylabel("Quoted spread (bps), 20d rolling median")
    ax.legend(frameon=False, ncol=3, loc="upper left")
    ax.text(
        0.01,
        0.02,
        "Lower spread means cheaper execution and better displayed liquidity.",
        transform=ax.transAxes,
        fontsize=9,
        color="#495057",
    )
    fig.tight_layout()
    fig.savefig(OUT / "spread_timeseries.png", dpi=180)
    plt.close(fig)


def normalized_price_vs_nav(rics: list[str]) -> None:
    fig = plt.figure(figsize=(12, 11), constrained_layout=True)
    gs = fig.add_gridspec(len(rics), 2, width_ratios=[2.2, 1.0], hspace=0.45, wspace=0.22)
    for row, ric in enumerate(rics):
        ax_level = fig.add_subplot(gs[row, 0])
        ax_gap = fig.add_subplot(gs[row, 1])
        df = _load_raw(ric)[["price", "nav"]].dropna()
        base = df.iloc[0]
        norm = df / base * 100.0
        gap = _premium_bps(df).rolling(5).mean()

        ax_level.plot(norm.index, norm["price"], label="ETF price", color=COLORS.get(ric), linewidth=1.4, alpha=0.9)
        ax_level.plot(norm.index, norm["nav"], label="NAV", color="#111111", linewidth=2.0, linestyle=(0, (4, 2)))
        ax_level.fill_between(
            norm.index,
            norm["price"].to_numpy(),
            norm["nav"].to_numpy(),
            color=COLORS.get(ric),
            alpha=0.10,
            label="price-NAV gap",
        )
        ax_level.set_title(f"{ric}: ETF price and NAV, normalized")
        ax_level.set_ylabel("Start = 100")
        ax_level.legend(frameon=False, loc="upper left", ncol=3)
        last_date = norm.dropna().index[-1]
        ax_level.scatter([last_date], [norm.loc[last_date, "price"]], color=COLORS.get(ric), s=24, zorder=5)
        ax_level.scatter([last_date], [norm.loc[last_date, "nav"]], color="#111111", s=24, zorder=5)

        ax_gap.plot(gap.index, gap.values, color=COLORS.get(ric), linewidth=1.5)
        ax_gap.axhline(0, color="#111111", linewidth=0.9)
        ax_gap.axhspan(-10, 10, color="#2a9d8f", alpha=0.08)
        ax_gap.set_title(f"{ric}: premium/discount")
        ax_gap.set_ylabel("bps, 5d avg.")
        ax_gap.text(
            0.03,
            0.06,
            "above NAV" if gap.dropna().iloc[-1] > 0 else "below NAV",
            transform=ax_gap.transAxes,
            fontsize=9,
            color="#495057",
        )
        for ax in (ax_level, ax_gap):
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
            ax.tick_params(axis="x", labelbottom=row == len(rics) - 1)
    ax_level.set_xlabel("Date")
    ax_gap.set_xlabel("Date")
    fig.savefig(OUT / "normalized_price_vs_nav.png", dpi=180)
    fig.savefig(OUT / "nav_alignment_detail.png", dpi=180)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _style()
    metrics = pd.read_csv(METRICS_CSV)
    metrics = metrics.sort_values("quality_risk_score", ascending=False)
    rics = [ric for ric in ["SPY", "EFA", "EEM"] if (RAW_DIR / f"{ric}.csv").exists()]

    summary_dashboard(metrics)
    tracking_vs_spread(metrics)
    premium_discount_timeseries(rics)
    spread_timeseries(rics)
    normalized_price_vs_nav(rics)

    print(f"Saved clearer Project 1 figures under: {OUT}")


if __name__ == "__main__":
    main()
