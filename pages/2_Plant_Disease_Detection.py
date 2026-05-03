import json
from pathlib import Path

import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "artifacts" / "plant_disease_model.keras"
CLASS_NAMES_PATH = PROJECT_ROOT / "artifacts" / "class_names.json"
DEFAULT_IMAGE_SIZE = (128, 128)


def clean_label(label: str) -> str:
    return label.replace("___", " - ").replace("_", " ")


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
    if not isinstance(class_names, list) or not class_names:
        raise ValueError("class_names.json must contain a non-empty list of class names.")

    return model, class_names


def model_image_size(model: tf.keras.Model) -> tuple[int, int]:
    input_shape = model.input_shape
    if isinstance(input_shape, list):
        input_shape = input_shape[0]

    height, width = input_shape[1], input_shape[2]
    if isinstance(height, int) and isinstance(width, int):
        return height, width
    return DEFAULT_IMAGE_SIZE


def prepare_image(image: Image.Image, image_size: tuple[int, int]) -> np.ndarray:
    image = image.convert("RGB").resize(image_size)
    array = tf.keras.utils.img_to_array(image)
    return np.expand_dims(array, axis=0)


st.set_page_config(
    page_title="Plant Disease Detection",
    page_icon="leaf",
    layout="centered",
)

st.title("Plant Disease Detection")
st.write("Upload a clear leaf image to detect the likely plant disease.")

try:
    model, class_names = load_artifacts()
    image_size = model_image_size(model)
except Exception as exc:
    st.warning("System 2 model artifacts are not ready yet.")
    st.info(
        "Download the dataset with `python system2_plant_disease/download_dataset.py`, "
        "then run a quick pipeline check with `python system2_plant_disease/train_model.py --quick_test`."
    )
    st.caption(f"Missing or unreadable artifact detail: {exc}")
    st.stop()

uploaded_file = st.file_uploader("Leaf image", type=["jpg", "jpeg", "png"])

if uploaded_file is None:
    st.info("Upload one close, well-lit photo of the affected leaf.")
    st.stop()

image = Image.open(uploaded_file)
st.image(image, caption="Uploaded leaf image", use_container_width=True)

with st.spinner("Analyzing leaf image..."):
    predictions = model.predict(prepare_image(image, image_size), verbose=0)[0]

predicted_index = int(np.argmax(predictions))
predicted_class = class_names[predicted_index]
confidence = float(predictions[predicted_index]) * 100

st.subheader("Prediction")
st.metric("Disease class", clean_label(predicted_class))
st.metric("Confidence", f"{confidence:.2f}%")
st.info("Consult local agriculture expert before applying treatment.")
