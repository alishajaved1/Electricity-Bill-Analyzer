"""Generate output/level1.csv and output/level2.csv from a folder of bills and the two CSV templates.

  python run_competition.py --bills test/bills --templates test/csv --out output
"""
import argparse
import sys

from competition.pipeline import run


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bills", required=True, help="folder with bill images (<bill_id>.png/.jpg)")
    ap.add_argument("--templates", required=True, help="folder containing level1.csv and level2.csv templates")
    ap.add_argument("--out", default="output", help="where to write the completed CSV files")
    ap.add_argument("--delay", type=float, default=3.0, help="seconds between API calls (free tier: 15 requests/min)")
    a = ap.parse_args()
    summary = run(a.bills, a.templates, a.out, a.delay)
    if summary["errors"]:
        print("\nProblems (review before submitting):")
        for e in summary["errors"]:
            print(" -", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
