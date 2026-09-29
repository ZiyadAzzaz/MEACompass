from pathlib import Path

import pandas as pd
import streamlit as st

from app.data import load_demo_table


DISPLAY_ENDPOINTS = ["meanfiringrate", "nAE", "r"]
ENDPOINT_LABELS = {
    "meanfiringrate": "Mean firing rate",
    "nAE": "Active electrodes",
    "r": "Coordinated activity (r)",
}

st.set_page_config(page_title="MEACompass", page_icon="🧠", layout="wide")
st.title("MEACompass")
st.subheader(
    "Reliability-Aware Early Prediction of Neural Network Development "
    "from Microelectrode-Array Assays"
)
st.caption("Toward Functional Digital Twins for Neural Organ-on-Chip Screening")

try:
    predictions = load_demo_table(Path("results/demo_predictions.csv"))
except (FileNotFoundError, ValueError) as error:
    st.error(f"Precomputed demo artifact is unavailable: {error}")
    st.stop()
eligible_samples = (
    predictions.loc[predictions["endpoint"].isin(DISPLAY_ENDPOINTS)]
    .groupby("sample_id")["endpoint"]
    .nunique()
)
predictions = predictions.loc[
    predictions["sample_id"].isin(eligible_samples[eligible_samples.eq(3)].index)
]

st.sidebar.header("Held-out assay example")
chemicals = (
    predictions[["casrn", "trt"]]
    .drop_duplicates()
    .assign(label=lambda frame: frame["trt"] + " · " + frame["casrn"])
    .sort_values("label")
)
chemical_label = st.sidebar.selectbox("Chemical", chemicals["label"].tolist())
chemical = chemicals.loc[chemicals["label"].eq(chemical_label), "casrn"].iloc[0]
chemical_rows = predictions.loc[predictions["casrn"].eq(chemical)]
dose = st.sidebar.selectbox(
    "Dose", sorted(chemical_rows["dose"].dropna().unique().tolist())
)
dose_rows = chemical_rows.loc[chemical_rows["dose"].eq(dose)]
sample_id = st.sidebar.selectbox(
    "Held-out well", sorted(dose_rows["sample_id"].unique().tolist())
)
include_div9 = st.sidebar.toggle("What if we wait until DIV9?", value=False)
reveal = st.sidebar.checkbox("Reveal observed DIV12", value=False)

selected = predictions.loc[
    predictions["sample_id"].eq(sample_id)
    & predictions["endpoint"].isin(DISPLAY_ENDPOINTS)
].copy()
selected["label"] = selected["endpoint"].map(ENDPOINT_LABELS)
selected = (
    selected.set_index("label")
    .loc[[ENDPOINT_LABELS[name] for name in DISPLAY_ENDPOINTS]]
    .reset_index()
)

st.info(
    f"Unseen during training · {selected['cohort'].iloc[0]} cohort · dose {dose:g} · "
    "all values are precomputed outer-fold predictions"
)

observed, predicted, hypothesis = st.columns(3)
with observed:
    st.subheader("OBSERVED")
    observed_table = selected[
        ["label", "observed_div5", "observed_div7"]
    ].rename(
        columns={
            "label": "Endpoint",
            "observed_div5": "DIV5",
            "observed_div7": "DIV7",
        }
    )
    if include_div9:
        observed_table["DIV9"] = selected["observed_div9"]
    st.dataframe(observed_table, hide_index=True, width="stretch")
    st.caption("Measurements available by the selected decision day.")

with predicted:
    st.subheader("PREDICTED")
    if include_div9:
        table = selected[
            ["label", "day9_prediction", "day9_lower", "day9_upper"]
        ].rename(
            columns={
                "label": "Endpoint",
                "day9_prediction": "DIV12 forecast",
                "day9_lower": "90% low",
                "day9_upper": "90% high",
            }
        )
        verdict = "DIV9 RETROSPECTIVE FORECAST"
    else:
        table = selected[
            ["label", "prediction", "uncertainty_lower", "uncertainty_upper"]
        ].rename(
            columns={
                "label": "Endpoint",
                "prediction": "DIV12 forecast",
                "uncertainty_lower": "90% low",
                "uncertainty_upper": "90% high",
            }
        )
        verdict = (
            "EARLY DECISION POSSIBLE"
            if selected["verdict"].eq("EARLY DECISION POSSIBLE").all()
            else "CONTINUE TO DIV12"
        )
    st.dataframe(table, hide_index=True, width="stretch")
    (st.success if verdict == "EARLY DECISION POSSIBLE" else st.warning)(verdict)

with hypothesis:
    st.subheader("HYPOTHESIS")
    if include_div9:
        comparison = pd.DataFrame(
            {
                "Endpoint": selected["label"],
                "DIV7 width": selected["uncertainty_upper"]
                - selected["uncertainty_lower"],
                "DIV9 width": selected["day9_upper"] - selected["day9_lower"],
            }
        )
        st.dataframe(comparison, hide_index=True, width="stretch")
        st.caption(
            "Retrospective scenario: added DIV9 evidence, not a prospective deployment claim."
        )
    else:
        comparator = selected[["label", "bt_plus_plus_prediction"]].rename(
            columns={
                "label": "Endpoint",
                "bt_plus_plus_prediction": "BT++ forecast",
            }
        )
        st.dataframe(comparator, hide_index=True, width="stretch")
        st.caption(
            "Strongest dose-informed comparator chosen without outer-test labels."
        )

if reveal:
    st.subheader("OBSERVED · DIV12 reveal")
    revealed = selected[["label", "target12"]].rename(
        columns={"label": "Endpoint", "target12": "Observed DIV12"}
    )
    st.dataframe(revealed, hide_index=True, width="stretch")

st.divider()
st.warning(
    "Research decision-support system only—not an autonomous assay-termination system. "
    "Prospective validation is required before laboratory deployment. The training data "
    "are rat cortical MEA assays, not organ-on-chip experiments."
)
st.caption(
    f"Loaded {len(predictions):,} held-out endpoint predictions. No model training or "
    "network access occurs in this app. The r endpoint retains an extreme-tail "
    "percent-control normalization limitation."
)
