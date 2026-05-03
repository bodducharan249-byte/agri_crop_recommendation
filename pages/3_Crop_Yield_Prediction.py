import json
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from ui_style import apply_global_styles, footer, premium_header, result_card


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "artifacts" / "crop_yield_model.joblib"
SCHEMA_PATH = BASE_DIR / "artifacts" / "crop_yield_schema.json"


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def make_label(name: str) -> str:
    return name.replace("_", " ").title()


apply_global_styles()
premium_header(
    "🌾 Crop Yield Prediction",
    "Enter crop, soil, and weather details to estimate expected crop yield.",
)

if not MODEL_PATH.exists() or not SCHEMA_PATH.exists():
    st.warning("Train the Crop Yield model first.")
    st.stop()

model = load_model()
schema = load_schema()

with st.form("yield_prediction_form"):
    input_values = {}

    for field in schema["fields"]:
        name = field["name"]
        label = make_label(name)

        if field["type"] == "categorical":
            options = field.get("options", [])
            default = field.get("default", options[0] if options else "")
            default_index = options.index(default) if default in options else 0
            input_values[name] = st.selectbox(label, options, index=default_index)
        else:
            default = float(field.get("default", 0.0))
            min_value = float(field.get("min", 0.0))
            max_value = float(field.get("max", max(default, 100.0)))
            if min_value == max_value:
                max_value = min_value + 1.0
            input_values[name] = st.number_input(
                label,
                min_value=min_value,
                max_value=max_value,
                value=min(max(default, min_value), max_value),
            )

    submit = st.form_submit_button("Predict Yield")

if submit:
    with st.spinner("🤖 AI is analyzing your farm data..."):
        input_df = pd.DataFrame([input_values], columns=schema["feature_columns"])
        expected_yield = float(model.predict(input_df)[0])
        unit = schema.get("target_unit", "dataset unit, commonly tons/hectare")

    st.subheader("Estimated Yield")
    result_card("Expected yield", f"{expected_yield:.2f} {unit}", "success")
    st.warning(
        "This is an estimated yield. Actual yield depends on seed quality, "
        "pest control, fertilizer, irrigation, and local conditions."
    )

footer()
