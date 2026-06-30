from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class FieldGroup:
    name: str
    candidates: tuple[str, ...]


FIELD_GROUPS = (
    FieldGroup("price", ("TRDPRC_1", "CLOSE", "CF_CLOSE", "TR.PriceClose")),
    FieldGroup("bid", ("BID",)),
    FieldGroup("ask", ("ASK",)),
    FieldGroup("volume", ("VOLUME", "ACVOL_UNS")),
)


def open_lseg_session():
    import lseg.data as ld

    ld.open_session()
    return ld


def fetch_first_available_field(ld, ric: str, fields: tuple[str, ...], start: str, end: str) -> tuple[pd.Series | None, str | None]:
    for field in fields:
        try:
            if field.startswith("TR."):
                df = ld.get_data(
                    universe=ric,
                    fields=[field],
                    parameters={"SDate": start, "EDate": end, "Frq": "D"},
                )
            else:
                df = ld.get_history(universe=ric, fields=[field], start=start, end=end, interval="daily")
            if df is None or df.empty:
                continue
            if "Date" in df.columns:
                df = df.set_index(pd.to_datetime(df["Date"]))
            numeric = df.select_dtypes(include="number")
            if numeric.empty:
                continue
            series = numeric.iloc[:, 0].dropna()
            series.index = pd.to_datetime(series.index)
            series = series.sort_index()
            if not series.empty:
                return series, field
        except Exception:
            continue
    return None, None


def fetch_fund_nav(ld, ric: str, start: str, end: str) -> tuple[pd.Series | None, str | None]:
    """Fetch dated ETF NAV. TR.FundNAV needs TR.FundNAV.date to avoid RangeIndex dates."""
    try:
        df = ld.get_data(
            universe=ric,
            fields=["TR.FundNAV", "TR.FundNAV.date"],
            parameters={"SDate": start, "EDate": end, "Frq": "D"},
        )
        if df is None or df.empty or "Date" not in df.columns:
            return None, None
        nav_col = "NAV" if "NAV" in df.columns else None
        if nav_col is None:
            numeric = [c for c in df.select_dtypes(include="number").columns if c != "Date"]
            if not numeric:
                return None, None
            nav_col = numeric[0]
        series = pd.to_numeric(df[nav_col], errors="coerce")
        series.index = pd.to_datetime(df["Date"])
        series = series.dropna().sort_index()
        if series.empty:
            return None, None
        return series, "TR.FundNAV + TR.FundNAV.date"
    except Exception:
        return None, None


def fetch_market_quality_panel(
    rics: list[str],
    start: str,
    end: str,
    out_dir: Path,
    include_nav: bool = False,
) -> pd.DataFrame:
    """Pull ETF market-quality fields from LSEG and cache one CSV per RIC."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ld = open_lseg_session()
    log_rows = []
    try:
        for i, ric in enumerate(rics, start=1):
            print(f"[{i}/{len(rics)}] Pulling {ric}...", flush=True)
            columns = {}
            field_used = {}
            for group in FIELD_GROUPS:
                series, used = fetch_first_available_field(ld, ric, group.candidates, start, end)
                if series is not None:
                    columns[group.name] = series
                    field_used[group.name] = used
            if include_nav:
                nav, nav_used = fetch_fund_nav(ld, ric, start, end)
                if nav is not None:
                    columns["nav"] = nav
                    field_used["nav"] = nav_used
            if columns:
                panel = pd.concat(columns, axis=1).sort_index()
                panel.index.name = "Date"
                panel.to_csv(out_dir / f"{ric}.csv")
                n_rows = len(panel)
            else:
                n_rows = 0
            log_rows.append(
                {
                    "ric": ric,
                    "status": "ok" if columns else "empty",
                    "fields_found": ", ".join(sorted(columns)),
                    "lseg_fields_used": "; ".join(f"{k}={v}" for k, v in field_used.items()),
                    "rows": n_rows,
                }
            )
            pd.DataFrame(log_rows).to_csv(out_dir / "lseg_pull_log.csv", index=False)
    finally:
        try:
            ld.close_session()
        except Exception:
            pass
    log = pd.DataFrame(log_rows)
    log.to_csv(out_dir / "lseg_pull_log.csv", index=False)
    return log
