import streamlit as st


st.set_page_config(
    page_title="AgriAI Platform",
    page_icon="🌾",
    layout="centered",
)

st.sidebar.title("🌾 AgriAI Platform")
st.sidebar.caption("Smart farming tools for crop and disease support.")

pages = [
    st.Page(
        "pages/1_Crop_Recommendation.py",
        title="🌱 Crop Recommendation",
    ),
    st.Page(
        "pages/2_Plant_Disease_Detection.py",
        title="🦠 Plant Disease Detection",
    ),
]

navigation = st.navigation(pages, position="sidebar")
navigation.run()
