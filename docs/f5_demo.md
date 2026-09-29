# Gate F5: public-demo readiness

## Gate report

**Status: BRANCH — deployment-ready static fallback; public URL pending human action**

### Objective

Provide a no-secret demo based only on precomputed outer-test predictions. The
preferred target is Streamlit Community Cloud or Hugging Face Spaces; the
required fallback is a self-contained static page.

### Completed evidence

- The local Streamlit app passed the F2 smoke test with HTTP 200.
- `scripts/build_static_demo.py` deterministically generates
  `docs/demo/index.html` from `results/demo_predictions.csv`.
- The static page embeds 300 endpoint rows from 100 held-out wells: the first 50
  complete sample identifiers in lexical order from each cohort.
- Selection never uses targets, prediction errors, uncertainty, verdicts, or
  visual appeal; it is not a showcase-chemical selection.
- The page implements chemical, dose, and held-out-well selectors; DIV9 scenario
  toggle; DIV12 reveal; interval display; BT++ comparison; and reliability badge.
- `OBSERVED`, `PREDICTED`, and `HYPOTHESIS` are explicit interface sections.
- The generated page is 152,510 bytes, returned HTTP 200 locally in 0.16 seconds,
  and contains no external network request, analytics, secret, or training code.
- Automated tests verify deterministic cohort-balanced selection, three-endpoint
  completeness, scope wording, and self-contained delivery.

### Public-hosting blocker

The project currently has no git remote, and the configured GitHub CLI token is
invalid. More importantly, the approved execution protocol designates making a
repository public as a human-only action. The agent therefore did not create a
public repository, change visibility, or claim a live URL.

### Human completion step

After the user creates or makes the repository public, host `docs/demo/` through
GitHub Pages or connect the repository to Streamlit Community Cloud. Then open
the resulting URL in a logged-out browser, test every control, confirm load time
under 15 seconds, and add the verified URL to the README and competition writeup.

Until that action is completed, the local Streamlit demo and static fallback are
valid submission assets, but Gate F5 is not reported as a public PASS.
