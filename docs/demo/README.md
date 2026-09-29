# MEACompass static demo

`index.html` is the no-server fallback for the Streamlit application. It embeds a
deterministic cohort-balanced subset of precomputed outer-test predictions: the
first 50 complete sample identifiers in lexical order from each cohort. Selection
does not use targets, errors, uncertainty, verdicts, or visual appeal.

Rebuild it with:

```bash
python scripts/build_static_demo.py
```

The file has no external JavaScript, font, image, analytics, API, or model-training
dependency. It can be hosted unchanged on any static service. Publication remains
a human action because the project repository must first be made public.
