# Gate F5: public-demo readiness

## Gate report

**Status: BRANCH — publication-ready static demo; public URL pending GitHub authentication**

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

### Public-hosting blocker

The project currently has no git remote, and the configured GitHub CLI token is
invalid. Amendment B authorizes public repository creation and GitHub Pages, but
the expected `ZiyadAzzaz` account must be successfully reauthenticated first.
No live URL is claimed before logged-out verification.

### Human completion step

After authentication and a SAFE scrub, publish `/docs` through GitHub Pages.
Then open the resulting URL in a logged-out browser, test every control, confirm
load time under 15 seconds, and add the verified URL to the README and writeup.

Until that action is completed, the local Streamlit demo and static fallback are
valid submission assets, but Gate F5 is not reported as a public PASS.
