from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from ui_style import apply_global_styles, sidebar_branding, top_brand_bar


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"


st.set_page_config(
    page_title="AgriAI Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()

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
st.sidebar.caption("Smart farming AI decision support")
st.sidebar.markdown(
    """
    **Systems**

    🌱 Crop Recommendation  
    🦠 Disease Detection  
    🌾 Yield Prediction  
    🌧️ Rainfall Forecast  
    🌰 Seed Quality  
    🧪 Pesticide Advice  
    💧 Smart Irrigation  
    📅 Planting Date
    """
)
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
    st.Page(
        "pages/5_Seed_Quality_Checker.py",
        title="Seed Quality Checker",
        icon="🌰",
    ),
    st.Page(
        "pages/6_Pesticide_Recommendation.py",
        title="Pesticide Recommendation",
        icon="🧪",
    ),
    st.Page(
        "pages/7_Smart_Irrigation.py",
        title="Smart Irrigation",
        icon="💧",
    ),
    st.Page(
        "pages/8_Best_Planting_Date.py",
        title="Best Planting Date",
        icon="📅",
    ),
]

navigation = st.navigation(pages, position="sidebar")
st.sidebar.divider()
sidebar_branding(ASSETS_DIR)
top_brand_bar(ASSETS_DIR)

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 94% 5%, rgba(255, 223, 0, 0.34), transparent 5rem),
            linear-gradient(180deg, #2874f0 0%, #1d4ed8 48%, #0f172a 100%) !important;
        border-right: 0 !important;
        box-shadow: 18px 0 46px rgba(30, 64, 175, 0.30) !important;
    }

    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.18) !important;
        margin: 0.85rem 0 !important;
    }

    section[data-testid="stSidebar"] h1 {
        position: relative;
        overflow: hidden;
        margin: 0 0 0.5rem !important;
        padding: 1.05rem 1rem !important;
        border: 1px solid rgba(255, 255, 255, 0.82) !important;
        border-radius: 1.2rem;
        background:
            radial-gradient(circle at 90% 5%, rgba(255, 223, 0, 0.82), transparent 4.8rem),
            linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(239, 246, 255, 0.92));
        color: #0f172a !important;
        font-size: 1.18rem !important;
        line-height: 1.12 !important;
        font-weight: 950 !important;
        box-shadow: 0 18px 38px rgba(15, 23, 42, 0.24);
    }

    section[data-testid="stSidebar"] h1:after {
        content: "Smart farming, faster";
        display: block;
        margin-top: 0.32rem;
        color: #2874f0;
        font-size: 0.78rem;
        font-style: italic;
        font-weight: 900;
    }

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        margin: 0.5rem 0 0.85rem !important;
        padding: 0.62rem 0.75rem;
        border-radius: 0.85rem;
        background: rgba(255, 255, 255, 0.14);
        color: rgba(255, 255, 255, 0.92) !important;
        font-size: 0.82rem !important;
        font-weight: 800 !important;
        line-height: 1.35 !important;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {
        display: block;
        margin: 0.2rem 0 0.55rem;
        color: rgba(255, 255, 255, 0.76) !important;
        font-size: 0.72rem;
        font-weight: 950 !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: rgba(255, 255, 255, 0.92) !important;
        font-size: 0.84rem;
        font-weight: 800;
        line-height: 1.65;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
    section[data-testid="stSidebar"] button[kind="header"],
    button[data-testid="stSidebarCollapseButton"] {
        background: rgba(255, 255, 255, 0.98) !important;
        border: 1px solid rgba(255, 255, 255, 0.85) !important;
        border-radius: 0.75rem !important;
        color: #1d4ed8 !important;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.22) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button:hover,
    section[data-testid="stSidebar"] button[kind="header"]:hover,
    button[data-testid="stSidebarCollapseButton"]:hover {
        background: #ffdf00 !important;
        border-color: #ffdf00 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg,
    section[data-testid="stSidebar"] button[kind="header"] svg,
    button[data-testid="stSidebarCollapseButton"] svg {
        fill: #1d4ed8 !important;
        stroke: #1d4ed8 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stPageLink"],
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
        border-radius: 0.9rem !important;
        margin: 0.22rem 0 !important;
        transition: background 140ms ease, color 140ms ease, transform 140ms ease, box-shadow 140ms ease;
    }

    section[data-testid="stSidebar"] [data-testid="stPageLink"] a,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a *,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a *,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] * {
        color: #eef6ff !important;
        font-weight: 850 !important;
    }

    section[data-testid="stSidebar"] [aria-current="page"],
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: #ffffff !important;
        box-shadow: 0 14px 30px rgba(15, 23, 42, 0.18) !important;
        transform: translateX(4px);
    }

    section[data-testid="stSidebar"] [aria-current="page"] *,
    section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] *,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] * {
        color: #1d4ed8 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stPageLink"]:hover,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover,
    section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
        background: rgba(255, 255, 255, 0.16) !important;
        transform: translateX(4px);
        box-shadow: 0 12px 26px rgba(15, 23, 42, 0.16);
    }

    .brand-card {
        background: rgba(255, 255, 255, 0.12) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        box-shadow: 0 14px 34px rgba(15, 23, 42, 0.20) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

components.html(
    """
    <script>
    const sidebarToggleCandidates = () => {
        const doc = window.parent.document;
        const direct = [
            '[data-testid="collapsedControl"] button',
            '[data-testid="collapsedControl"]',
            '[data-testid="stSidebarCollapsedControl"] button',
            '[data-testid="stSidebarCollapsedControl"]',
            '[data-testid="stSidebarCollapseButton"] button',
            'button[data-testid="stSidebarCollapseButton"]'
        ];

        const selectorMatches = direct
            .map((selector) => doc.querySelector(selector))
            .filter(Boolean);

        const labelledButtons = Array.from(doc.querySelectorAll("button")).filter((button) => {
            const label = [
                button.getAttribute("aria-label"),
                button.getAttribute("title"),
                button.textContent
            ].filter(Boolean).join(" ");
            return /sidebar|side bar|navigation|menu|collapse|expand/i.test(label);
        });

        return [...selectorMatches, ...labelledButtons];
    };

    const toggleSidebar = () => {
        const candidates = sidebarToggleCandidates();
        if (candidates.length > 0) {
            candidates[0].click();
            return;
        }

        const doc = window.parent.document;
        const sidebar = doc.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.transform = "translateX(0)";
            sidebar.style.visibility = "visible";
            sidebar.style.opacity = "1";
            sidebar.style.pointerEvents = "auto";
        }
    };

    const closeSidebarAfterNavigation = () => {
        const doc = window.parent.document;
        const sidebar = doc.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) return;

        const rect = sidebar.getBoundingClientRect();
        const isOpen = rect.width > 180 && rect.right > 100;
        if (!isOpen) return;

        const collapseButton =
            doc.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
            doc.querySelector('button[data-testid="stSidebarCollapseButton"]');

        if (collapseButton) {
            collapseButton.click();
            return;
        }

        const candidates = sidebarToggleCandidates();
        if (candidates.length > 0) {
            candidates[0].click();
        }
    };

    const bindSidebarNavAutoClose = () => {
        const doc = window.parent.document;
        const navTargets = doc.querySelectorAll([
            'section[data-testid="stSidebar"] [data-testid="stPageLink"] a',
            'section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a',
            'section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]'
        ].join(","));

        navTargets.forEach((target) => {
            if (target.dataset.agriAutocloseBound === "true") return;
            target.dataset.agriAutocloseBound = "true";
            target.addEventListener("click", () => {
                window.parent.setTimeout(closeSidebarAfterNavigation, 220);
            });
        });
    };

    const ensureAgriSidebarButton = () => {
        const doc = window.parent.document;
        if (doc.getElementById("agri-sidebar-access")) return;

        const button = doc.createElement("button");
        button.id = "agri-sidebar-access";
        button.type = "button";
        button.setAttribute("aria-label", "Open AgriAI menu");
        button.innerHTML = "<span>☰</span><strong>Menu</strong>";
        button.onclick = toggleSidebar;

        Object.assign(button.style, {
            position: "fixed",
            top: "0.7rem",
            left: "1rem",
            zIndex: "2147483647",
            display: "inline-flex",
            alignItems: "center",
            gap: "0.5rem",
            height: "2.6rem",
            padding: "0 0.85rem",
            border: "1px solid rgba(40, 116, 240, 0.22)",
            borderRadius: "0.9rem",
            background: "#ffffff",
            color: "#1d4ed8",
            boxShadow: "0 14px 34px rgba(30, 64, 175, 0.24)",
            fontFamily: "Inter, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
            fontSize: "0.92rem",
            fontWeight: "900",
            cursor: "pointer",
            pointerEvents: "auto"
        });

        const icon = button.querySelector("span");
        Object.assign(icon.style, {
            fontSize: "1.25rem",
            lineHeight: "1"
        });

        button.addEventListener("mouseenter", () => {
            button.style.background = "#ffdf00";
            button.style.transform = "translateY(-1px)";
            button.style.boxShadow = "0 18px 38px rgba(30, 64, 175, 0.32)";
        });

        button.addEventListener("mouseleave", () => {
            button.style.background = "#ffffff";
            button.style.transform = "translateY(0)";
            button.style.boxShadow = "0 14px 34px rgba(30, 64, 175, 0.24)";
        });

        doc.body.appendChild(button);
    };

    ensureAgriSidebarButton();
    bindSidebarNavAutoClose();
    window.parent.setTimeout(ensureAgriSidebarButton, 500);
    window.parent.setTimeout(bindSidebarNavAutoClose, 500);
    window.parent.setInterval(ensureAgriSidebarButton, 1600);
    window.parent.setInterval(bindSidebarNavAutoClose, 1600);
    </script>
    """,
    height=0,
)

navigation.run()
