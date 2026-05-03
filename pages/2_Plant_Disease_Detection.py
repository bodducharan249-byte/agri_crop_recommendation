import json
from pathlib import Path

import numpy as np
import streamlit as st
import tensorflow as tf
from PIL import Image

from ui_style import apply_global_styles, footer, premium_header, result_card


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "artifacts" / "plant_disease_model.keras"
CLASS_NAMES_PATH = PROJECT_ROOT / "artifacts" / "class_names.json"
DEFAULT_IMAGE_SIZE = (128, 128)
DISEASE_GUIDANCE = {
    "Apple - Apple scab": {
        "description": "Fungal disease that causes dark, scabby spots on leaves and fruit.",
        "treatment": "Remove fallen infected leaves, improve airflow, and use a recommended fungicide if needed.",
    },
    "Apple - Black rot": {
        "description": "Fungal disease affecting leaves, branches, and fruit.",
        "treatment": "Remove infected leaves and fruit, prune diseased branches, and apply fungicide as advised.",
    },
    "Apple - Cedar apple rust": {
        "description": "Fungal disease that creates orange-yellow leaf spots and can reduce tree vigor.",
        "treatment": "Remove nearby alternate hosts where practical and apply a suitable fungicide during risk periods.",
    },
    "Apple - healthy": {
        "description": "The uploaded leaf appears healthy based on the model prediction.",
        "treatment": "Continue regular monitoring, balanced watering, and good orchard sanitation.",
    },
    "Cherry (including sour) - Powdery mildew": {
        "description": "Fungal disease that forms white powdery growth on leaves and young shoots.",
        "treatment": "Prune for airflow, avoid overhead watering, and use an approved fungicide when necessary.",
    },
    "Corn (maize) - Cercospora leaf spot Gray leaf spot": {
        "description": "Fungal leaf disease that causes gray or tan rectangular lesions on corn leaves.",
        "treatment": "Use resistant varieties, rotate crops, manage residue, and apply fungicide for severe cases.",
    },
    "Corn (maize) - Common rust ": {
        "description": "Fungal disease that produces rust-colored pustules on corn leaves.",
        "treatment": "Plant resistant varieties and consider fungicide if infection appears early and spreads quickly.",
    },
    "Corn (maize) - Northern Leaf Blight": {
        "description": "Fungal disease that creates long, cigar-shaped gray-green lesions on corn leaves.",
        "treatment": "Rotate crops, use resistant hybrids, remove residue where practical, and apply fungicide if needed.",
    },
    "Grape - Black rot": {
        "description": "Fungal disease that affects grape leaves, stems, and berries.",
        "treatment": "Remove infected fruit and plant debris, prune for airflow, and follow a grape fungicide schedule.",
    },
    "Grape - Esca (Black Measles)": {
        "description": "Trunk disease that can cause leaf striping, berry spotting, and vine decline.",
        "treatment": "Prune infected wood, avoid pruning wounds in wet conditions, and consult an expert for vine management.",
    },
    "Grape - Leaf blight (Isariopsis Leaf Spot)": {
        "description": "Fungal disease that causes brown leaf spots and premature leaf drop.",
        "treatment": "Remove infected leaves, improve airflow, and use a recommended fungicide if disease pressure is high.",
    },
    "Orange - Haunglongbing (Citrus greening)": {
        "description": "Serious bacterial citrus disease that causes yellow shoots, misshapen fruit, and tree decline.",
        "treatment": "Control psyllid insects, remove severely infected trees, and contact local agricultural authorities.",
    },
    "Peach - Bacterial spot": {
        "description": "Bacterial disease that causes dark leaf spots, shot holes, and fruit blemishes.",
        "treatment": "Use resistant varieties, avoid overhead irrigation, prune for airflow, and apply copper products as advised.",
    },
    "Pepper, bell - Bacterial spot": {
        "description": "Bacterial disease that causes water-soaked spots on leaves and fruit.",
        "treatment": "Remove infected plants, avoid wet foliage, rotate crops, and use copper-based sprays when recommended.",
    },
    "Potato - Early blight": {
        "description": "Fungal disease that causes brown target-like spots, usually on older leaves first.",
        "treatment": "Remove infected foliage, rotate crops, avoid overhead watering, and apply fungicide if disease spreads.",
    },
    "Potato - Late blight": {
        "description": "Aggressive disease that causes dark, water-soaked lesions and can rapidly damage plants.",
        "treatment": "Remove infected plants, avoid wet foliage, and seek urgent local guidance for fungicide treatment.",
    },
    "Squash - Powdery mildew": {
        "description": "Fungal disease that creates white powdery patches on squash leaves.",
        "treatment": "Improve airflow, remove heavily infected leaves, and use approved fungicide or sulfur products if suitable.",
    },
    "Strawberry - Leaf scorch": {
        "description": "Fungal disease that causes reddish-purple spots and scorched-looking leaf edges.",
        "treatment": "Remove infected leaves, improve spacing, avoid overhead watering, and use recommended fungicide if needed.",
    },
    "Tomato - Bacterial spot": {
        "description": "Bacterial disease that causes small dark spots on leaves, stems, and fruit.",
        "treatment": "Remove infected debris, avoid overhead watering, rotate crops, and use copper sprays as advised.",
    },
    "Tomato - Early blight": {
        "description": "Fungal disease that forms dark target-like spots and yellowing on older leaves.",
        "treatment": "Remove lower infected leaves, mulch soil, rotate crops, and apply fungicide if disease advances.",
    },
    "Tomato - Late blight": {
        "description": "Fast-spreading disease that causes dark leaf lesions and fruit rot.",
        "treatment": "Remove infected plants promptly and contact an agricultural expert for local treatment guidance.",
    },
    "Tomato - Leaf Mold": {
        "description": "Fungal disease common in humid conditions, causing yellow patches and moldy leaf undersides.",
        "treatment": "Increase ventilation, reduce leaf wetness, remove affected leaves, and use fungicide if needed.",
    },
    "Tomato - Septoria leaf spot": {
        "description": "Fungal disease that causes many small circular spots on tomato leaves.",
        "treatment": "Remove infected leaves, mulch, avoid overhead watering, rotate crops, and apply fungicide when needed.",
    },
    "Tomato - Spider mites Two-spotted spider mite": {
        "description": "Mite damage that causes stippling, yellowing, and fine webbing on leaves.",
        "treatment": "Spray leaves with water, remove heavily infested foliage, and use miticide or insecticidal soap as advised.",
    },
    "Tomato - Target Spot": {
        "description": "Fungal disease that causes circular brown leaf spots with target-like rings.",
        "treatment": "Remove infected leaves, improve airflow, avoid wet foliage, and apply fungicide if symptoms spread.",
    },
    "Tomato - Tomato Yellow Leaf Curl Virus": {
        "description": "Viral disease that causes curled yellow leaves and stunted tomato growth.",
        "treatment": "Control whiteflies, remove infected plants, and use resistant varieties in future planting.",
    },
    "Tomato - Tomato mosaic virus": {
        "description": "Viral disease that causes mottled leaves, curling, and reduced plant vigor.",
        "treatment": "Remove infected plants, sanitize tools, control handling spread, and use virus-free seed.",
    },
}


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


apply_global_styles()
premium_header(
    "🦠 Plant Disease Detection",
    "Upload a clear leaf image to detect the likely plant disease.",
)

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

st.subheader("Uploaded Image")
st.image(image, use_column_width=True)

with st.spinner("🤖 AI is analyzing your farm data..."):
    predictions = model.predict(prepare_image(image, image_size), verbose=0)[0]

predicted_index = int(np.argmax(predictions))
predicted_class = class_names[predicted_index]
confidence = float(predictions[predicted_index]) * 100
disease_name = clean_label(predicted_class)

st.subheader("Detection Result")

result_col, confidence_col = st.columns(2)
with result_col:
    result_card("Disease name", disease_name, "info")
with confidence_col:
    result_card("Confidence", f"{confidence:.2f}%", "success")

guidance = DISEASE_GUIDANCE.get(disease_name)
if guidance:
    st.info(f"Description: {guidance['description']}")
    st.warning(f"Treatment: {guidance['treatment']}")
else:
    st.info("Description: Guidance is not available for this prediction yet.")
    st.warning("Treatment: Consult an agricultural expert for crop-specific treatment advice.")

st.info("Consult agricultural expert before applying treatment")
footer()
