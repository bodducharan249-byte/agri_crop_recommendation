import streamlit as st

from ui_style import apply_global_styles, footer, premium_header, result_card


CROPS = ["rice", "cotton", "tomato", "chilli", "wheat", "maize"]
PESTS = [
    "aphids",
    "leaf folder",
    "stem borer",
    "whitefly",
    "fruit borer",
    "fungal infection",
]

RECOMMENDATIONS = {
    "aphids": {
        "option": "Neem oil or insecticidal soap spray",
        "caution": "Spray in the early morning or evening. Avoid spraying during flowering when bees are active.",
        "non_chemical": "Use yellow sticky traps and remove heavily infested leaves where practical.",
    },
    "leaf folder": {
        "option": "Bacillus thuringiensis (Bt) based biopesticide",
        "caution": "Apply when larvae are young and follow the label dose. Avoid repeated unnecessary sprays.",
        "non_chemical": "Monitor folded leaves, conserve natural enemies, and avoid excess nitrogen fertilizer.",
    },
    "stem borer": {
        "option": "Pheromone traps with a Bt based biopesticide if infestation is increasing",
        "caution": "Use traps for monitoring first. Apply any spray only when pest levels cross local advisory thresholds.",
        "non_chemical": "Remove dead hearts or affected plant parts and use pheromone traps for early detection.",
    },
    "whitefly": {
        "option": "Neem oil or horticultural oil spray",
        "caution": "Do not spray during hot midday conditions. Test on a small crop patch before wider use.",
        "non_chemical": "Install yellow sticky traps, remove weed hosts, and avoid overcrowding plants.",
    },
    "fruit borer": {
        "option": "Bt based biopesticide or neem seed kernel extract",
        "caution": "Target early larval stages. Do not spray close to harvest unless the product label allows it.",
        "non_chemical": "Use pheromone traps and remove damaged fruits to reduce pest carryover.",
    },
    "fungal infection": {
        "option": "Trichoderma based biofungicide or a low-risk copper/soap product where locally approved",
        "caution": "Avoid overuse of copper products and follow local label limits. Do not mix products unless advised.",
        "non_chemical": "Improve spacing, remove infected plant parts, avoid overhead irrigation, and improve drainage.",
    },
}

CROP_NOTES = {
    "rice": "Keep the field balanced with proper water management and avoid excess nitrogen.",
    "cotton": "Scout the underside of leaves regularly and conserve beneficial insects.",
    "tomato": "Remove affected fruits or leaves early and keep the crop well ventilated.",
    "chilli": "Check new shoots and flower buds often because early pest control is easier.",
    "wheat": "Monitor field edges first and avoid unnecessary preventive sprays.",
    "maize": "Check whorls and stems regularly, especially during early crop growth.",
}


apply_global_styles()
premium_header(
    "🧪 Pesticide Recommendation System",
    "Select the crop and pest/problem to get a safer, farmer-friendly control suggestion.",
)

with st.form("pesticide_recommendation_form"):
    crop = st.selectbox("Crop", CROPS)
    pest = st.selectbox("Pest / problem", PESTS)
    submit = st.form_submit_button("Get Recommendation")

if submit:
    with st.spinner("🤖 AI is analyzing your farm data..."):
        recommendation = RECOMMENDATIONS[pest]

    st.subheader("Recommended Safer Option")
    result_card("Recommended safer option", recommendation["option"], "success")

    st.subheader("Application Caution")
    st.warning(recommendation["caution"])

    st.subheader("Non-Chemical Method")
    st.info(recommendation["non_chemical"])

    st.subheader("Crop Note")
    st.write(CROP_NOTES[crop])

st.error(
    "Always consult a local agriculture officer and follow label instructions before pesticide use."
)
st.caption(
    "This rule-based system avoids banned or highly dangerous pesticides and favors safer, integrated pest management options."
)
footer()
