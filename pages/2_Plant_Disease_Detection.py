import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "artifacts" / "plant_disease_model.keras"
CLASS_NAMES_PATH = PROJECT_ROOT / "artifacts" / "class_names.json"
IMAGE_SIZE = (224, 224)


TREATMENT_SUGGESTIONS = {
    "healthy": "The leaf appears healthy. Keep monitoring the crop and maintain balanced watering and nutrition.",
    "bacterial": "Remove heavily infected leaves, avoid overhead watering, and ask a local agriculture officer about a copper-based treatment.",
    "blight": "Remove affected leaves, improve airflow, and use a locally recommended fungicide if the infection spreads.",
    "mildew": "Keep leaves dry, increase spacing, and consider sulfur or another recommended mildew treatment.",
    "rust": "Remove infected leaves, avoid wet foliage, and apply a rust-control fungicide approved for the crop.",
    "spot": "Prune infected leaves, reduce leaf wetness, and monitor nearby plants for spreading spots.",
    "scab": "Remove infected plant material and use disease-free planting stock in the next cycle.",
    "rot": "Reduce excess moisture, improve drainage, and remove severely affected plant material.",
    "virus": "Most viral diseases have no direct cure. Remove infected plants and control insect vectors.",
    "mosaic": "Remove infected plants, disinfect tools, and control sap-feeding insects such as aphids or whiteflies.",
    "curl": "Check for whiteflies or aphids, remove badly affected leaves, and use locally recommended pest control.",
}


def clean_label(label: str) -> str:
    return label.replace("___", " - ").replace("_", " ")


def treatment_for(label: str) -> str:
    normalized = label.lower()
    for keyword, suggestion in TREATMENT_SUGGESTIONS.items():
        if keyword in normalized:
            return suggestion
    return (
        "Isolate affected leaves if practical, avoid overhead watering, and confirm the diagnosis with a local "
        "agriculture expert before applying chemical treatment."
    )


@st.cache_resource
def load_artifacts() -> tuple[tf.keras.Model, list[str]]:
    missing = [
        path.relative_to(PROJECT_ROOT).as_posix()
        for path in (MODEL_PATH, CLASS_NAMES_PATH)
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError(", ".join(missing))

    model = tf.keras.models.load_model(MODEL_PATH)
    class_names = json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8"))
    return model, class_names


def prepare_image(image: Image.Image) -> np.ndarray:
    image = image.convert("RGB").resize(IMAGE_SIZE)
    array = tf.keras.utils.img_to_array(image)
    return np.expand_dims(array, axis=0)


def confidence_chart(class_names: list[str], predictions: np.ndarray, top_count: int = 3):
    top_indexes = np.argsort(predictions)[::-1][:top_count]
    labels = [clean_label(class_names[index]) for index in top_indexes][::-1]
    values = [predictions[index] * 100 for index in top_indexes][::-1]

    fig, ax = plt.subplots(figsize=(6, 2.6))
    ax.barh(labels, values, color="#2f855a")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Confidence (%)")
    ax.grid(axis="x", alpha=0.2)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    return fig


st.set_page_config(
    page_title="Plant Disease Detection",
    page_icon="leaf",
    layout="centered",
)

st.title("Plant Disease Detection")
st.write("Upload a clear leaf image to get the likely disease class, confidence, and a simple treatment suggestion.")

try:
    model, class_names = load_artifacts()
except Exception as exc:
    st.warning("System 2 model artifacts are not ready yet.")
    st.info(
        "Download the dataset with `python system2_plant_disease/download_dataset.py`, "
        "then run a quick pipeline check with `python system2_plant_disease/train_model.py --quick_test`."
    )
    st.caption(f"Missing or unreadable artifact detail: {exc}")
    st.stop()

uploaded_file = st.file_uploader("Leaf image", type=["jpg", "jpeg", "png", "webp"])

if uploaded_file is None:
    st.info("Upload one close, well-lit photo of the affected leaf.")
    st.stop()

image = Image.open(uploaded_file)
st.image(image, caption="Uploaded leaf image", use_container_width=True)

with st.spinner("Analyzing leaf image..."):
    predictions = model.predict(prepare_image(image), verbose=0)[0]

predicted_index = int(np.argmax(predictions))
predicted_class = class_names[predicted_index]
confidence = float(predictions[predicted_index]) * 100

st.subheader("Prediction")
st.metric("Disease class", clean_label(predicted_class))
st.metric("Confidence", f"{confidence:.2f}%")

st.subheader("Treatment suggestion")
st.success(treatment_for(predicted_class))

st.pyplot(confidence_chart(class_names, predictions), use_container_width=True)
st.caption("This is AI support only. Confirm severe infections with a local agriculture expert.")
