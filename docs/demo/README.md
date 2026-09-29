# MEACompass static demo

`index.html` is the no-server fallback for the Streamlit application. It embeds a
deterministic cohort-balanced subset of precomputed outer-test predictions plus
the three cases registered before the rebuild in `docs/decisions.md`. The neutral
case is independent of outcomes; the correct and failure examples reuse the
already-locked descriptive case table. No new case was chosen by browsing the
rendered demo.

Rebuild it with:

```bash
python scripts/build_static_demo.py
```

The file has no external JavaScript, font, image, analytics, API, or model-training
dependency. It can be hosted unchanged on GitHub Pages from `/docs`.
