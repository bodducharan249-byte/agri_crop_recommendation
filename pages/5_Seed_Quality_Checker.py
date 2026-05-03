import json
from pathlib import Path

import numpy as np
from PIL import Image
import streamlit as st
import tensorflow as tf


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "artifacts" / "seed_quality_model.keras"
CLASS_NAMES_PATH = BASE_DIR / "artifacts" / "seed_quality_class_names.json"
IMAGE_SIZE = (128, 128)


@st.cache_resource
def load_model():
    return tf.keras.models.load_model(MODEL_PATH)


@st.cache_data
def load_class_names():
    return json.loads(CLASS_NAMES_PATH.read_text(encoding="utf-8"))


def prepare_image(uploaded_image) -> np.ndarray:
    image = Image.open(uploaded_image).convert("RGB")
    image = image.resize(IMAGE_SIZE)
    image_array = np.asarray(image, dtype=np.float32)
    return np.expand_dims(image_array, axis=0)


st.title("🌰 Seed Quality Checker")
st.write(
    "This system will classify seed quality as good, damaged, broken, or infected."
)

uploaded_image = st.file_uploader(
    "Upload a seed image",
    type=["jpg", "jpeg", "png"],
)

if uploaded_image is not None:
    st.image(uploaded_image, caption="Uploaded seed image", use_container_width=True)

st.subheader("Seed Quality Result")
if not MODEL_PATH.exists() or not CLASS_NAMES_PATH.exists():
    st.info("Train the Seed Quality model first.")
elif uploaded_image is None:
    st.info("Upload a seed image to check quality.")
else:
    model = load_model()
    class_names = load_class_names()
    prediction = model.predict(prepare_image(uploaded_image), verbose=0)[0]
    class_index = int(np.argmax(prediction))
    confidence = float(prediction[class_index]) * 100

    st.success(f"Class name: {class_names[class_index]}")
    st.metric("Confidence", f"{confidence:.2f}%")

st.warning(
    "This is AI support only. Final seed selection should be verified manually."
)
