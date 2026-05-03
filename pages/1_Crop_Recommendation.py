from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from ui_style import apply_global_styles, footer, premium_header, result_card


BASE_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "crop_recommendation_model.joblib"
FEATURE_COLUMNS_PATH = ARTIFACTS_DIR / "feature_columns.joblib"


@st.cache_resource
def load_artifacts():
    missing_files = [
        str(path.relative_to(BASE_DIR))
        for path in (MODEL_PATH, FEATURE_COLUMNS_PATH)
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Missing required artifact file(s): " + ", ".join(missing_files)
        )

    model = joblib.load(MODEL_PATH)
    feature_columns = joblib.load(FEATURE_COLUMNS_PATH)
    return model, feature_columns


apply_global_styles()
premium_header(
    "🌱 Crop Recommendation System",
    "Enter soil and weather details to get the best crop recommendation.",
)

try:
    model, feature_columns = load_artifacts()
except Exception as exc:
    st.error("The trained model artifacts could not be loaded.")
    st.info("Run `python train_model.py`, then deploy again with the `artifacts` folder included.")
    st.exception(exc)
    st.stop()


with st.form("crop_form"):
    N = st.number_input("Nitrogen (N)", min_value=0.0, max_value=200.0, value=50.0)
    P = st.number_input("Phosphorus (P)", min_value=0.0, max_value=200.0, value=50.0)
    K = st.number_input("Potassium (K)", min_value=0.0, max_value=250.0, value=50.0)
    temperature = st.number_input("Temperature (°C)", min_value=0.0, max_value=60.0, value=25.0)
    humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=70.0)
    ph = st.number_input("Soil pH", min_value=0.0, max_value=14.0, value=6.5)
    rainfall = st.number_input("Rainfall (mm)", min_value=0.0, max_value=500.0, value=100.0)

    submit = st.form_submit_button("Recommend Crop")

components.html(
    """
    <script>
    const fieldMap = [
        ["Nitrogen", "nitrogen"],
        ["Phosphorus", "phosphorus"],
        ["Potassium", "potassium"],
        ["Temperature", "temperature"],
        ["Humidity", "humidity"],
        ["Soil pH", "ph"],
        ["Rainfall", "rainfall"]
    ];

    const decorateCropInputs = () => {
        const doc = window.parent.document;
        const inputs = doc.querySelectorAll('div[data-testid="stNumberInput"]');

        inputs.forEach((input) => {
            const label = input.querySelector("label");
            const labelText = label ? label.textContent.trim() : "";
            const match = fieldMap.find(([name]) => labelText.includes(name));

            if (match) {
                input.dataset.agriField = match[1];
            }
        });
    };

    decorateCropInputs();
    window.parent.setTimeout(decorateCropInputs, 300);
    window.parent.setInterval(decorateCropInputs, 1200);
    </script>
    """,
    height=0,
)


if submit:
    with st.spinner("🤖 AI is analyzing your farm data..."):
        input_data = pd.DataFrame(
            [
                {
                    "N": N,
                    "P": P,
                    "K": K,
                    "temperature": temperature,
                    "humidity": humidity,
                    "ph": ph,
                    "rainfall": rainfall,
                }
            ]
        )
        input_data = input_data[feature_columns]

        probabilities = model.predict_proba(input_data)[0]
        crop_names = model.classes_
        top_3_indexes = np.argsort(probabilities)[::-1][:3]

    st.subheader("Top 3 Recommended Crops")

    for rank, index in enumerate(top_3_indexes, start=1):
        crop = crop_names[index]
        confidence = probabilities[index] * 100
        result_card(
            f"Recommendation {rank}",
            f"{crop.title()} - Confidence: {confidence:.2f}%",
            "success",
        )

    st.info(
        "This is AI support only. Final decisions should also depend on local soil "
        "tests, season, water availability, and market demand."
    )

footer()
