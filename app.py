import streamlit as st


st.set_page_config(
    page_title="AgriAI Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #243244;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
    section[data-testid="stSidebar"] button[kind="header"],
    button[data-testid="stSidebarCollapseButton"] {
        background: #1f2f3f !important;
        border: 1px solid #33475d !important;
        border-radius: 0.55rem !important;
        color: #f8fafc !important;
        min-height: 2.25rem !important;
        min-width: 2.25rem !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.22);
        transition: background 120ms ease, border-color 120ms ease, transform 120ms ease;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button:hover,
    section[data-testid="stSidebar"] button[kind="header"]:hover,
    button[data-testid="stSidebarCollapseButton"]:hover {
        background: #0f766e !important;
        border-color: #14b8a6 !important;
        transform: translateY(-1px);
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg,
    section[data-testid="stSidebar"] button[kind="header"] svg,
    button[data-testid="stSidebarCollapseButton"] svg {
        fill: #f8fafc !important;
        stroke: #f8fafc !important;
    }

    section[data-testid="stSidebar"] h1 {
        color: #f8fafc;
        font-size: 1.65rem;
        font-weight: 800;
        padding-bottom: 0.45rem;
        border-bottom: 1px solid #2f3d50;
    }

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #a7b5c6;
        font-size: 0.95rem;
        line-height: 1.45;
        margin-bottom: 1.25rem;
    }

    section[data-testid="stSidebar"] [data-testid="stPageLink"],
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
        border-radius: 0.45rem;
        margin: 0.2rem 0;
        transition: background 120ms ease, color 120ms ease;
    }

    section[data-testid="stSidebar"] [data-testid="stPageLink"] a,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a *,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a *,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] * {
        color: #e5eef7 !important;
        font-weight: 650 !important;
    }

    section[data-testid="stSidebar"] [aria-current="page"],
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: #0f766e !important;
    }

    section[data-testid="stSidebar"] [aria-current="page"] *,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] *,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] * {
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] [data-testid="stPageLink"]:hover,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
        background: #1f2f3f !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("🌾 AgriAI Platform")
st.sidebar.caption("Smart farming AI tools for crop, disease, and yield support.")
st.sidebar.divider()

pages = [
    st.Page(
        "pages/1_Crop_Recommendation.py",
        title="Crop Recommendation",
        icon="🌱",
    ),
    st.Page(
        "pages/2_Plant_Disease_Detection.py",
        title="Plant Disease Detection",
        icon="🦠",
    ),
    st.Page(
        "pages/3_Crop_Yield_Prediction.py",
        title="Crop Yield Prediction",
        icon="🌾",
    ),
    st.Page(
        "pages/4_Rainfall_Prediction.py",
        title="Rainfall Prediction",
        icon="🌧️",
    ),
]

navigation = st.navigation(pages, position="sidebar")
navigation.run()
