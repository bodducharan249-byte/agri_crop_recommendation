import html
import base64
from pathlib import Path

import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --agri-green: #10b981;
            --agri-lime: #a3e635;
            --agri-blue: #38bdf8;
            --agri-purple: #8b5cf6;
            --agri-amber: #f59e0b;
            --agri-red: #ef4444;
            --glass: rgba(255, 255, 255, 0.78);
            --ink: #10231d;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(34, 197, 94, 0.36), transparent 34rem),
                radial-gradient(circle at top right, rgba(56, 189, 248, 0.34), transparent 32rem),
                linear-gradient(135deg, #f5fff9 0%, #f2fbff 35%, #faf7ff 68%, #fffaf0 100%);
            background-size: 140% 140%;
            color: var(--ink);
            animation: activeGradient 14s ease-in-out infinite;
        }

        .stApp:before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            background:
                linear-gradient(115deg, transparent 0%, rgba(255, 255, 255, 0.52) 12%, transparent 24%),
                linear-gradient(65deg, transparent 0%, rgba(34, 211, 238, 0.22) 10%, transparent 22%),
                radial-gradient(circle at 20% 20%, rgba(163, 230, 53, 0.26), transparent 18rem),
                radial-gradient(circle at 82% 62%, rgba(139, 92, 246, 0.24), transparent 20rem);
            background-size: 240% 240%, 220% 220%, 100% 100%, 100% 100%;
            animation: movingLights 18s linear infinite;
        }

        .stApp > header,
        .stApp [data-testid="stSidebar"],
        .stApp .main,
        .stApp .block-container {
            position: relative;
            z-index: 1;
        }

        .block-container {
            padding-top: 2.4rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(6, 78, 59, 0.98), rgba(15, 23, 42, 0.98)) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.14);
            box-shadow: 18px 0 42px rgba(15, 23, 42, 0.18);
        }

        section[data-testid="stSidebar"] * {
            color: #eefdf7 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stPageLink"] a,
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
            border-radius: 0.95rem;
            margin: 0.18rem 0;
            padding: 0.45rem 0.65rem;
            transition: transform 160ms ease, background 160ms ease, box-shadow 160ms ease;
        }

        section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover,
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
            background: rgba(255, 255, 255, 0.12) !important;
            transform: translateX(3px);
            box-shadow: 0 10px 28px rgba(16, 185, 129, 0.18);
        }

        section[data-testid="stSidebar"] [aria-current="page"] {
            background: linear-gradient(135deg, #10b981, #22d3ee) !important;
            box-shadow: 0 14px 30px rgba(34, 211, 238, 0.24);
        }

        h1, h2, h3 {
            letter-spacing: 0;
        }

        div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stDataFrame"] {
            background: var(--glass);
            border: 1px solid rgba(255, 255, 255, 0.65);
            border-radius: 1.25rem;
            box-shadow: 0 24px 70px rgba(15, 23, 42, 0.10);
            backdrop-filter: blur(18px);
            padding: 1rem;
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.86);
            border: 1px solid rgba(255, 255, 255, 0.72);
            border-radius: 1.1rem;
            padding: 0.9rem 1rem;
            box-shadow: 0 18px 44px rgba(15, 23, 42, 0.10);
        }

        .stButton > button, div[data-testid="stFormSubmitButton"] button {
            border: 0;
            border-radius: 999px;
            background: linear-gradient(135deg, #10b981, #22d3ee, #8b5cf6);
            color: white;
            font-weight: 800;
            box-shadow: 0 16px 34px rgba(16, 185, 129, 0.28);
            transition: transform 150ms ease, box-shadow 150ms ease, filter 150ms ease;
        }

        .stButton > button:hover, div[data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-2px);
            filter: saturate(1.15);
            box-shadow: 0 22px 46px rgba(56, 189, 248, 0.35);
        }

        .premium-hero {
            position: relative;
            overflow: hidden;
            border-radius: 1.6rem;
            padding: 1.45rem 1.55rem;
            margin-bottom: 1.3rem;
            background:
                linear-gradient(135deg, rgba(16, 185, 129, 0.94), rgba(14, 165, 233, 0.88), rgba(139, 92, 246, 0.9));
            box-shadow: 0 28px 80px rgba(14, 116, 144, 0.26);
            animation: heroBreath 5.5s ease-in-out infinite;
        }

        .premium-hero:after {
            content: "";
            position: absolute;
            inset: -40%;
            background: radial-gradient(circle, rgba(255,255,255,0.32), transparent 30%);
            animation: shimmer 7s ease-in-out infinite;
        }

        .premium-hero h1 {
            position: relative;
            z-index: 1;
            margin: 0;
            color: #ffffff;
            font-size: clamp(2rem, 5vw, 3.6rem);
            font-weight: 900;
        }

        .premium-hero p {
            position: relative;
            z-index: 1;
            margin: 0.55rem 0 0;
            color: rgba(255, 255, 255, 0.92);
            font-size: 1.05rem;
            font-weight: 600;
        }

        .result-card {
            border-radius: 1.35rem;
            padding: 1.05rem 1.15rem;
            margin: 0.75rem 0;
            color: #ffffff;
            box-shadow: 0 18px 48px rgba(15, 23, 42, 0.18);
            animation: resultPop 420ms ease-out, pulseGlow 2.6s ease-in-out infinite;
            transition: transform 160ms ease, box-shadow 160ms ease;
        }

        .result-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 24px 62px rgba(15, 23, 42, 0.22);
        }

        .result-card h3 {
            margin: 0 0 0.35rem;
            color: #ffffff;
            font-size: 0.95rem;
            text-transform: uppercase;
        }

        .result-card .value {
            font-size: 1.45rem;
            line-height: 1.25;
            font-weight: 900;
        }

        .result-success { background: linear-gradient(135deg, #059669, #22c55e); }
        .result-warning { background: linear-gradient(135deg, #f59e0b, #facc15); color: #3b2600; }
        .result-danger { background: linear-gradient(135deg, #dc2626, #fb7185); }
        .result-info { background: linear-gradient(135deg, #2563eb, #8b5cf6); }

        .glass-card {
            background: rgba(255, 255, 255, 0.76);
            border: 1px solid rgba(255, 255, 255, 0.72);
            border-radius: 1.25rem;
            padding: 1rem 1.1rem;
            margin: 0.7rem 0;
            box-shadow: 0 18px 52px rgba(15, 23, 42, 0.10);
            backdrop-filter: blur(18px);
            transition: transform 180ms ease, box-shadow 180ms ease;
        }

        .glass-card:hover,
        div[data-testid="stForm"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 24px 68px rgba(15, 23, 42, 0.14);
        }

        .ai-loader {
            display: inline-flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.8rem 1rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.78);
            box-shadow: 0 16px 36px rgba(56, 189, 248, 0.18);
            font-weight: 800;
        }

        .ai-loader .dot {
            width: 0.68rem;
            height: 0.68rem;
            border-radius: 999px;
            background: #22d3ee;
            animation: pulseDot 1.1s ease-in-out infinite;
        }

        .agri-footer {
            margin-top: 2rem;
            padding: 1rem;
            text-align: center;
            color: rgba(15, 23, 42, 0.62);
            font-weight: 650;
        }

        .brand-card {
            border-radius: 1.05rem;
            padding: 0.95rem;
            margin: 0.7rem 0 1rem;
            background:
                linear-gradient(145deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.06));
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
            backdrop-filter: blur(16px);
        }

        .brand-card .brand-eyebrow {
            color: rgba(236, 253, 245, 0.72);
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.45rem;
        }

        .brand-card .brand-name {
            color: #ffffff;
            font-size: 0.98rem;
            font-weight: 900;
            line-height: 1.25;
        }

        .brand-card .brand-dept {
            color: rgba(236, 253, 245, 0.86);
            font-size: 0.82rem;
            font-weight: 650;
            line-height: 1.35;
            margin-top: 0.25rem;
        }

        .brand-fallback {
            border-radius: 0.9rem;
            padding: 0.65rem 0.75rem;
            margin: 0.45rem 0;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.16);
            color: #ffffff;
            font-weight: 800;
            line-height: 1.25;
        }

        .top-brand-strip {
            width: min(1180px, calc(100vw - 3rem));
            margin: -1.55rem auto 1.1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.65rem 1rem;
            border-radius: 0 0 1.35rem 1.35rem;
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(236, 253, 245, 0.86));
            border: 1px solid rgba(255, 255, 255, 0.72);
            box-shadow: 0 16px 44px rgba(15, 23, 42, 0.12);
            backdrop-filter: blur(18px);
            animation: brandFloat 6s ease-in-out infinite;
        }

        .top-brand-logo {
            min-height: 3.2rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .top-brand-logo img {
            max-height: 3.4rem;
            max-width: 16rem;
            object-fit: contain;
            display: block;
        }

        .top-brand-fallback {
            border-radius: 0.95rem;
            padding: 0.65rem 0.85rem;
            background: rgba(16, 185, 129, 0.1);
            color: #064e3b;
            font-weight: 900;
            text-align: center;
            line-height: 1.25;
        }

        .top-brand-center {
            flex: 1;
            text-align: center;
            color: #0f3d34;
            font-weight: 900;
            font-size: 0.95rem;
            line-height: 1.25;
        }

        .top-brand-center span {
            display: block;
            color: rgba(15, 61, 52, 0.7);
            font-size: 0.78rem;
            margin-top: 0.12rem;
            font-weight: 800;
        }

        @keyframes resultPop {
            from { opacity: 0; transform: translateY(10px) scale(0.98); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        @keyframes pulseGlow {
            0%, 100% { filter: drop-shadow(0 0 0 rgba(34, 211, 238, 0)); }
            50% { filter: drop-shadow(0 0 18px rgba(34, 211, 238, 0.34)); }
        }

        @keyframes pulseDot {
            0%, 100% { transform: scale(0.85); opacity: 0.5; }
            50% { transform: scale(1.18); opacity: 1; }
        }

        @keyframes shimmer {
            0%, 100% { transform: translate(-8%, -8%) rotate(0deg); }
            50% { transform: translate(8%, 8%) rotate(18deg); }
        }

        @keyframes activeGradient {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        @keyframes movingLights {
            0% { background-position: -140% 0%, 140% 100%, 0 0, 0 0; }
            50% { background-position: 80% 60%, 10% 35%, 0 0, 0 0; }
            100% { background-position: 220% 100%, -120% 0%, 0 0, 0 0; }
        }

        @keyframes heroBreath {
            0%, 100% { box-shadow: 0 28px 80px rgba(14, 116, 144, 0.26); }
            50% { box-shadow: 0 32px 96px rgba(139, 92, 246, 0.34); }
        }

        @keyframes brandFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(3px); }
        }

        @media (prefers-reduced-motion: reduce) {
            .stApp,
            .stApp:before,
            .premium-hero,
            .result-card,
            .top-brand-strip,
            .ai-loader .dot {
                animation: none !important;
            }
        }

        @media (max-width: 720px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .premium-hero { padding: 1.2rem; border-radius: 1.25rem; }
            .premium-hero h1 { font-size: 2rem; }
            .result-card .value { font-size: 1.15rem; }
            .top-brand-strip {
                width: calc(100vw - 1rem);
                margin-top: -1.2rem;
                flex-direction: column;
                border-radius: 0 0 1rem 1rem;
            }
            .top-brand-logo img {
                max-height: 2.9rem;
                max-width: 13rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def premium_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="premium-hero">
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def result_card(title: str, value: str, color_type: str = "info") -> None:
    safe_type = color_type if color_type in {"success", "warning", "danger", "info"} else "info"
    st.markdown(
        f"""
        <div class="result-card result-{safe_type}">
            <h3>{html.escape(title)}</h3>
            <div class="value">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ai_loading_animation(text: str = "AI is analyzing...") -> None:
    st.markdown(
        f"""
        <div class="ai-loader">
            <span class="dot"></span>
            <span>{html.escape(text)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_card(content: str) -> None:
    st.markdown(
        f"""<div class="glass-card">{content}</div>""",
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        (
            '<div class="agri-footer">'
            'Marwadi University | Information &amp; Communication Technology<br>'
            'Developed by Pawan Kalyan'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def sidebar_branding(assets_dir: Path) -> None:
    marwadi_logo = assets_dir / "marwadi_logo.png"
    ict_logo = assets_dir / "ict_logo.png"

    if marwadi_logo.exists():
        st.sidebar.image(str(marwadi_logo), width=150)
    else:
        st.sidebar.markdown(
            '<div class="brand-fallback">Marwadi University</div>',
            unsafe_allow_html=True,
        )

    if ict_logo.exists():
        st.sidebar.image(str(ict_logo), width=150)
    else:
        st.sidebar.markdown(
            '<div class="brand-fallback">Information &amp; Communication Technology</div>',
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        """
        <div class="brand-card">
            <div class="brand-eyebrow">Developed by</div>
            <div class="brand-name">Pawan Kalyan</div>
            <div class="brand-dept">Information &amp; Communication Technology</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _image_data_uri(path: Path) -> str | None:
    if not path.exists():
        return None

    image_bytes = path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def top_brand_bar(assets_dir: Path) -> None:
    marwadi_logo = _image_data_uri(assets_dir / "marwadi_logo.png")
    ict_logo = _image_data_uri(assets_dir / "ict_logo.png")

    marwadi_markup = (
        f'<img src="{marwadi_logo}" alt="Marwadi University logo">'
        if marwadi_logo
        else '<div class="top-brand-fallback">Marwadi University</div>'
    )
    ict_markup = (
        f'<img src="{ict_logo}" alt="Information and Communication Technology logo">'
        if ict_logo
        else '<div class="top-brand-fallback">Information &amp; Communication Technology</div>'
    )

    st.markdown(
        f"""
        <div class="top-brand-strip">
            <div class="top-brand-logo">{marwadi_markup}</div>
            <div class="top-brand-center">
                AgriAI Platform
                <span>Smart farming AI decision support</span>
            </div>
            <div class="top-brand-logo">{ict_markup}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
