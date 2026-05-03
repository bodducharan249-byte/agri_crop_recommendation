import streamlit as st


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
st.info("Model not trained yet")
st.warning(
    "This is AI support only. Final seed selection should be verified manually."
)
