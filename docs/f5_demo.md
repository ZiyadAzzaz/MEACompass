# Gate F5: public-demo readiness

## Gate report

**Status: PASS — public static demo verified anonymously**

### Objective

Provide a no-secret demo based only on precomputed outer-test predictions. The
preferred target is Streamlit Community Cloud or Hugging Face Spaces; the
required fallback is a self-contained static page.

### Completed evidence

- The local Streamlit app passed the F2 smoke test with HTTP 200.
- `scripts/build_static_demo.py` deterministically generates
  `docs/demo/index.html` from `results/demo_predictions.csv`.
- The static page embeds 306 endpoint rows from 102 held-out wells: the first 50
  complete sample identifiers in lexical order from each cohort plus three
  preregistered cases (two cases overlap neither lexical subset).
- Selection never uses targets, prediction errors, uncertainty, verdicts, or
  visual appeal; it is not a showcase-chemical selection.
- The page implements chemical, dose, and held-out-well selectors; DIV9 scenario
  toggle; DIV12 reveal; interval display; BT++ comparison; and reliability badge.
- `OBSERVED`, `PREDICTED`, and `HYPOTHESIS` are explicit interface sections.
- The generated page is 160,901 bytes, returns HTTP 200 locally,
  and contains no external network request, analytics, secret, or training code.
- Automated tests verify deterministic cohort-balanced selection, three-endpoint
  completeness, scope wording, and self-contained delivery.
- Registered case navigation is present and defaults to the neutral sample:
  - neutral: `NTP|MW1139-19|A1`;
  - ordinary correct: `ToxCast|MW1147-5|E4` (Fluorene);
  - disclosed failure: `ToxCast|MW1160-23|B5` (tributyltin chloride).

### Public deployment

The static demo is published from `main/docs` at
<https://ziyadazzaz.github.io/MEACompass/demo/>. GitHub Pages reported a
successful build from commit `4754fce`. An unauthenticated HTTPS request returned
HTTP 200 and confirmed all three registered case labels, the
`OBSERVED`/`PREDICTED`/`HYPOTHESIS` sections, and zero external URL requests.
Automated interface tests cover selector behavior and deterministic case loading.

### Remaining human visual check

Capture the required real logged-out neutral-case screenshot for slide 10. This
is a deck-finalization step, not a blocker to the public demo gate.
