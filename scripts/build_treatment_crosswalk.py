"""Generate candidate raw-treatment to canonical-CAS matches for human review."""

from __future__ import annotations

import argparse
from pathlib import Path

from neurochip.data import propose_treatment_crosswalk


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/raw/epa_nfa/extracted"))
    parser.add_argument(
        "--output", type=Path, default=Path("data/derived/treatment_crosswalk_candidates.csv")
    )
    args = parser.parse_args()

    crosswalk = propose_treatment_crosswalk(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    crosswalk.to_csv(args.output, index=False)

    review = crosswalk.loc[(crosswalk["score"] < 0.85) | (crosswalk["margin"] < 0.10)]
    print(f"labels={len(crosswalk)} review_required={len(review)}")
    if not review.empty:
        columns = [
            "cohort",
            "treatment",
            "casrn",
            "preferred_name",
            "score",
            "second_name",
            "second_score",
        ]
        print(review[columns].to_string(index=False))


if __name__ == "__main__":
    main()
