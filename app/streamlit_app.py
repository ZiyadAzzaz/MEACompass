from pathlib import Path
import streamlit as st
from app.data import load_demo_predictions

st.set_page_config(page_title="NeuroChip-Twin", layout="wide")
st.title("NeuroChip-Twin")
st.caption("Research decision support for neural MEA assays — interface skeleton")

path = Path("results/standardized_predictions.csv")
try:
    predictions = load_demo_predictions(path)
except (FileNotFoundError, ValueError) as error:
    predictions = None
    st.info(f"Precomputed prediction artifact is not available yet: {error}")

st.sidebar.header("Held-out example")
st.sidebar.selectbox("Chemical", ["-- Select after Gate L1 --"], disabled=True)
st.sidebar.selectbox("Dose", ["-- Select after Gate L1 --"], disabled=True)
st.sidebar.toggle("Include DIV9 hypothesis", value=False, disabled=True)

observed, predicted, hypothesis = st.columns(3)
with observed:
    st.subheader("OBSERVED")
    st.write("DIV5 and DIV7 measurements will appear here.")
with predicted:
    st.subheader("PREDICTED")
    st.write("The precomputed DIV12 prediction and 90% interval will appear here.")
    st.info("RELIABILITY BADGE — pending Gate M2/M3")
with hypothesis:
    st.subheader("HYPOTHESIS")
    st.write("Optional DIV9 scenario; not an observed measurement unless explicitly revealed.")

st.divider()
st.warning("Research decision-support system only. It is not an autonomous assay-termination system; prospective validation is required before laboratory deployment.")
if predictions is not None:
    st.caption(f"Loaded {len(predictions):,} precomputed rows using prediction schema v1.0.0. No model training occurs in this app.")
