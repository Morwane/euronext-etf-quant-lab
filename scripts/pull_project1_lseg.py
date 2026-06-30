from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data import ETF_UNIVERSE
from src.lseg_pull import fetch_market_quality_panel


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Pull ETF market-quality fields from LSEG Workspace.")
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default="2026-06-30")
    parser.add_argument("--out", default=str(ROOT / "data" / "raw_lseg_project1"))
    parser.add_argument("--rics", default=",".join(ETF_UNIVERSE), help="Comma-separated ETF RICs.")
    parser.add_argument("--with-nav", action="store_true", help="Also request dated TR.FundNAV. Can be slower on Workspace.")
    args = parser.parse_args()
    rics = [x.strip() for x in args.rics.split(",") if x.strip()]
    log = fetch_market_quality_panel(rics, args.start, args.end, Path(args.out), include_nav=args.with_nav)
    print(log.to_string(index=False))
    print(f"\nSaved raw LSEG files under: {args.out}")


if __name__ == "__main__":
    main()
