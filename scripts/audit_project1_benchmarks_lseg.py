from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))


ROOT = Path(__file__).resolve().parents[1]

FIELDS = ("TRDPRC_1", "CLOSE", "CF_CLOSE", "TR.PriceClose")

BENCHMARK_CANDIDATES = {
    "SPY": [("_SPX", ".SPX", "S&P 500 Index")],
    "DIA": [("_DJI", ".DJI", "Dow Jones Industrial Average")],
    "IWM": [("_RUT", ".RUT", "Russell 2000 Index")],
    "EFA": [
        ("_STOXX", ".STOXX", "STOXX 600 proxy"),
        ("_STOXX50E", ".STOXX50E", "Euro STOXX 50 proxy"),
        ("_MIEA00000PUS", ".MIEA00000PUS", "MSCI EAFE candidate"),
        ("_dMIEA00000PUS", ".dMIEA00000PUS", "MSCI EAFE candidate"),
    ],
    "EEM": [
        ("_MSCIEF", ".MSCIEF", "MSCI Emerging Markets candidate"),
        ("_dMIEM00000PUS", ".dMIEM00000PUS", "MSCI EM candidate"),
        ("_MIEM00000PUS", ".MIEM00000PUS", "MSCI EM candidate"),
        ("_NSEI", ".NSEI", "Nifty 50 proxy"),
        ("_HSI", ".HSI", "Hang Seng proxy"),
    ],
    "VGK": [("_STOXX", ".STOXX", "STOXX 600 Europe"), ("_STOXX50E", ".STOXX50E", "Euro STOXX 50")],
    "EWG": [("_GDAXI", ".GDAXI", "DAX Germany")],
    "EWJ": [("_N225", ".N225", "Nikkei 225 Japan")],
    "EWU": [("_FTSE", ".FTSE", "FTSE 100 UK")],
    "EWZ": [("_BVSP", ".BVSP", "Bovespa Brazil")],
    "FXI": [("_HSI", ".HSI", "Hang Seng proxy"), ("_SSEC", ".SSEC", "Shanghai Composite proxy")],
    "XLK": [("_SPLRCT", ".SPLRCT", "S&P 500 Information Technology")],
    "XLF": [("_SPSY", ".SPSY", "S&P 500 Financials candidate"), ("_SPLRCF", ".SPLRCF", "S&P Financials candidate")],
    "XLE": [("_SPNY", ".SPNY", "S&P 500 Energy candidate"), ("_SPLRCEN", ".SPLRCEN", "S&P Energy candidate")],
    "XLV": [("_SPXHC", ".SPXHC", "S&P 500 Health Care candidate"), ("_SPLRCHC", ".SPLRCHC", "S&P Health Care candidate")],
    "XLY": [("_SPLRCD", ".SPLRCD", "S&P 500 Consumer Discretionary")],
    "XLP": [("_SPLRCS", ".SPLRCS", "S&P 500 Consumer Staples")],
    "XLI": [("_SPLRCI", ".SPLRCI", "S&P 500 Industrials")],
    "XLU": [("_SPLRCU", ".SPLRCU", "S&P 500 Utilities")],
    "XLB": [("_SPLRCM", ".SPLRCM", "S&P 500 Materials")],
    "XLC": [("_SPLRCL", ".SPLRCL", "S&P 500 Communication Services")],
    "GLD": [("GCc1", "GCc1", "Gold front future proxy"), ("_GVZ", ".GVZ", "Gold vol index, not price benchmark")],
    "SLV": [("SIc1", "SIc1", "Silver front future proxy")],
    "HYG": [("JNK", "JNK", "High-yield ETF peer proxy")],
    "JNK": [("HYG", "HYG", "High-yield ETF peer proxy")],
    "LQD": [("AGG", "AGG", "US aggregate ETF proxy")],
    "AGG": [("AGG", "AGG", "Self placeholder")],
    "TIP": [("AGG", "AGG", "US aggregate ETF proxy")],
}


def fetch_history(ld, ric: str, start: str, end: str) -> tuple[pd.Series | None, str | None, str]:
    for field in FIELDS:
        try:
            if field.startswith("TR."):
                df = ld.get_data(
                    universe=ric,
                    fields=[field, f"{field}.date"],
                    parameters={"SDate": start, "EDate": end, "Frq": "D"},
                )
            else:
                df = ld.get_history(universe=ric, fields=[field], start=start, end=end, interval="daily")
            if df is None or df.empty:
                continue
            if "Date" in df.columns:
                df = df.set_index(pd.to_datetime(df["Date"]))
            elif isinstance(df.index, pd.RangeIndex):
                continue
            numeric = df.select_dtypes(include="number")
            if numeric.empty:
                continue
            series = numeric.iloc[:, 0].dropna()
            series.index = pd.to_datetime(series.index)
            series = series.sort_index()
            if len(series) > 20:
                return series, field, "ok"
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {str(exc)[:160]}"
    return None, None, locals().get("last_error", "empty")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit available LSEG ETF benchmark RICs.")
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--etfs", default=",".join(BENCHMARK_CANDIDATES))
    parser.add_argument("--save-history-dir", default=str(ROOT / "data" / "raw_lseg_project1_benchmarks"))
    args = parser.parse_args()

    import lseg.data as ld

    etfs = [x.strip() for x in args.etfs.split(",") if x.strip()]
    history_dir = Path(args.save_history_dir)
    history_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    ld.open_session()
    try:
        for etf in etfs:
            candidates = BENCHMARK_CANDIDATES.get(etf, [])
            print(f"\n[{etf}] {len(candidates)} candidates", flush=True)
            for label, ric, name in candidates:
                series, field, status = fetch_history(ld, ric, args.start, args.end)
                row = {
                    "etf": etf,
                    "candidate_label": label,
                    "ric": ric,
                    "name": name,
                    "status": "usable" if series is not None else "failed",
                    "field": field or "",
                    "n_obs": int(series.count()) if series is not None else 0,
                    "start": series.index.min().date().isoformat() if series is not None else "",
                    "end": series.index.max().date().isoformat() if series is not None else "",
                    "error": "" if series is not None else status,
                }
                rows.append(row)
                if series is not None:
                    series.rename("price").to_frame().to_csv(history_dir / f"{label}.csv", index_label="Date")
                print(f"  {ric:16} {row['status']:7} {row['n_obs']:4} {row['field']} {name}", flush=True)
    finally:
        try:
            ld.close_session()
        except Exception:
            pass

    audit = pd.DataFrame(rows)
    out = ROOT / "data" / "processed" / "project1_benchmark_availability.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(out, index=False)

    best = (
        audit[audit["status"].eq("usable")]
        .sort_values(["etf", "n_obs"], ascending=[True, False])
        .drop_duplicates("etf")
        .copy()
    )
    best_out = ROOT / "data" / "processed" / "project1_benchmark_suggestions.csv"
    best.to_csv(best_out, index=False)
    print(f"\nSaved audit: {out}")
    print(f"Saved suggestions: {best_out}")
    if not best.empty:
        print("\nSuggested benchmark per ETF:")
        print(best[["etf", "ric", "name", "field", "n_obs", "start", "end"]].to_string(index=False))


if __name__ == "__main__":
    main()
