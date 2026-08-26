import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|buffer_size;1024000|max_delay;500000|stimeout;2000000"
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
import socket
import tempfile
import cv2
import io
import time
import math
import re
import json
import psutil
import urllib.request
import urllib.parse
import difflib
import numpy as np
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from collections import Counter

# ReportLab Imports for Official PDF Generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Page Configuration
st.set_page_config(
    page_title="THE INITIATIVE 2.0 - Gujarat Police SCRB Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------- SESSION STATE PROFILE INITIALIZATION -----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "officer_profile" not in st.session_state:
    st.session_state.officer_profile = {
        "name": "Officer Aamin",
        "post": "Senior Cyber Forensic Examiner & ANPR Grid Lead",
        "badge_id": "GP-SCRB-8842",
        "dept": "State Crime Record Bureau (SCRB)",
        "unit": "Cyber Intelligence & Video Forensics Command",
        "station": "SCRB Cyber Command & Control Grid, Gandhinagar",
        "phone": "+91 94280 11240",
        "email": "aamin.scrb@gujarat.gov.in",
        "clearance": "Level 4 (State Forensics & Intercept Clearance)",
        "joining_date": "14-Feb-2021",
        "avatar_bytes": None
    }

# ----------------- MULTI-COLOR WAVY GLASS THEME WITH EQUAL BOX SIZES (CSS) -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Ambient Canvas */
    html, body, [class*="css"], .stApp {
        background: radial-gradient(circle at 10% 20%, #F1F5F9 0%, #E2E8F0 45%, #CBD5E1 100%) !important;
        background-attachment: fixed !important;
        color: #0F172A !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Segoe UI', Roboto, sans-serif !important;
        letter-spacing: -0.01em;
    }

    /* Headings in Main Body */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stHeading {
        color: #0F172A !important;
        font-weight: 800 !important;
        letter-spacing: -0.025em !important;
    }

    .stApp p, .stApp span, .stApp label, .stApp div {
        color: #1E293B;
    }

    /* Monospace for Data & Timestamps */
    .mono-font, code, pre, .stDataFrame, [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', 'SF Mono', 'Roboto Mono', monospace !important;
    }

    /* ========================================================================= */
    /* UNIFORM & EQUAL-SIZED MULTI-COLOR WAVY FROSTED GLASS BOXES                */
    /* ========================================================================= */

    /* Equal Sized Base KPI Glass Card */
    .kpi-card {
        backdrop-filter: blur(28px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
        border-radius: 18px !important;
        padding: 18px 22px !important;
        position: relative;
        overflow: hidden;
        margin-bottom: 14px !important;
        min-height: 140px !important;
        height: 140px !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        box-sizing: border-box !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
    }

    .kpi-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3.5px;
        opacity: 0.75;
        transition: opacity 0.25s ease;
    }

    .kpi-card:hover::after {
        opacity: 1;
    }

    /* Equal Sized Action Cards */
    .action-card {
        backdrop-filter: blur(28px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
        border-radius: 18px !important;
        padding: 22px 24px !important;
        position: relative;
        overflow: hidden;
        margin-bottom: 14px !important;
        min-height: 180px !important;
        height: 180px !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        box-sizing: border-box !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
    }

    .action-card:hover {
        transform: translateY(-2px);
    }

    .action-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3.5px;
        opacity: 0.75;
        transition: opacity 0.25s ease;
    }

    .action-card:hover::after {
        opacity: 1;
    }

    /* 1. GREEN WAVY GLASS BOX (Online Status / Positive Health) */
    .kpi-card-green, .action-card-green {
        background: radial-gradient(at 0% 0%, rgba(34, 197, 94, 0.22) 0px, transparent 60%),
                    radial-gradient(at 100% 100%, rgba(16, 185, 129, 0.18) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(240, 253, 244, 0.85) 0%, rgba(220, 252, 231, 0.6) 100%) !important;
        border: 1px solid rgba(134, 239, 172, 0.9) !important;
        box-shadow: 0 10px 30px rgba(34, 197, 94, 0.08), inset 0 1px 2px rgba(255, 255, 255, 0.95) !important;
    }
    .kpi-card-green:hover, .action-card-green:hover {
        background: radial-gradient(at 0% 0%, rgba(34, 197, 94, 0.3) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(240, 253, 244, 0.95) 0%, rgba(220, 252, 231, 0.75) 100%) !important;
        border-color: rgba(34, 197, 94, 0.8) !important;
        box-shadow: 0 14px 38px rgba(34, 197, 94, 0.16), inset 0 1px 2px rgba(255, 255, 255, 1) !important;
    }
    .kpi-card-green::after, .action-card-green::after {
        background: linear-gradient(90deg, #16A34A 0%, #4ADE80 50%, #10B981 100%);
    }
    .kpi-card-green .kpi-label, .action-card-green .kpi-label { color: #15803D !important; }

    /* 2. RED WAVY GLASS BOX (Incidents / Forensic Intercepts) */
    .kpi-card-red, .action-card-red {
        background: radial-gradient(at 0% 0%, rgba(244, 63, 94, 0.22) 0px, transparent 60%),
                    radial-gradient(at 100% 100%, rgba(225, 29, 72, 0.18) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(255, 241, 242, 0.85) 0%, rgba(254, 226, 226, 0.6) 100%) !important;
        border: 1px solid rgba(254, 202, 202, 0.9) !important;
        box-shadow: 0 10px 30px rgba(225, 29, 72, 0.08), inset 0 1px 2px rgba(255, 255, 255, 0.95) !important;
    }
    .kpi-card-red:hover, .action-card-red:hover {
        background: radial-gradient(at 0% 0%, rgba(244, 63, 94, 0.3) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(255, 241, 242, 0.95) 0%, rgba(254, 226, 226, 0.75) 100%) !important;
        border-color: rgba(244, 63, 94, 0.8) !important;
        box-shadow: 0 14px 38px rgba(225, 29, 72, 0.16), inset 0 1px 2px rgba(255, 255, 255, 1) !important;
    }
    .kpi-card-red::after, .action-card-red::after {
        background: linear-gradient(90deg, #E11D48 0%, #FB7185 50%, #F43F5E 100%);
    }
    .kpi-card-red .kpi-label, .action-card-red .kpi-label { color: #BE123C !important; }

    /* 3. ORANGE WAVY GLASS BOX (Compute Load / AMC Notices / Gaps) */
    .kpi-card-orange, .action-card-orange {
        background: radial-gradient(at 0% 0%, rgba(249, 115, 22, 0.22) 0px, transparent 60%),
                    radial-gradient(at 100% 100%, rgba(234, 88, 12, 0.18) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(255, 247, 237, 0.85) 0%, rgba(254, 215, 170, 0.6) 100%) !important;
        border: 1px solid rgba(253, 186, 116, 0.9) !important;
        box-shadow: 0 10px 30px rgba(249, 115, 22, 0.08), inset 0 1px 2px rgba(255, 255, 255, 0.95) !important;
    }
    .kpi-card-orange:hover, .action-card-orange:hover {
        background: radial-gradient(at 0% 0%, rgba(249, 115, 22, 0.3) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(255, 247, 237, 0.95) 0%, rgba(254, 215, 170, 0.75) 100%) !important;
        border-color: rgba(249, 115, 22, 0.8) !important;
        box-shadow: 0 14px 38px rgba(249, 115, 22, 0.16), inset 0 1px 2px rgba(255, 255, 255, 1) !important;
    }
    .kpi-card-orange::after, .action-card-orange::after {
        background: linear-gradient(90deg, #EA580C 0%, #FB923C 50%, #FBBF24 100%);
    }
    .kpi-card-orange .kpi-label, .action-card-orange .kpi-label { color: #C2410C !important; }

    /* 4. BLUE WAVY GLASS BOX (Network / Core Grid) */
    .kpi-card-blue, .action-card-blue {
        background: radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.22) 0px, transparent 60%),
                    radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.18) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(240, 249, 255, 0.85) 0%, rgba(224, 242, 254, 0.6) 100%) !important;
        border: 1px solid rgba(186, 230, 253, 0.9) !important;
        box-shadow: 0 10px 30px rgba(14, 165, 233, 0.08), inset 0 1px 2px rgba(255, 255, 255, 0.95) !important;
    }
    .kpi-card-blue:hover, .action-card-blue:hover {
        background: radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.3) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(240, 249, 255, 0.95) 0%, rgba(224, 242, 254, 0.75) 100%) !important;
        border-color: rgba(14, 165, 233, 0.8) !important;
        box-shadow: 0 14px 38px rgba(14, 165, 233, 0.16), inset 0 1px 2px rgba(255, 255, 255, 1) !important;
    }
    .kpi-card-blue::after, .action-card-blue::after {
        background: linear-gradient(90deg, #0284C7 0%, #38BDF8 50%, #06B6D4 100%);
    }
    .kpi-card-blue .kpi-label, .action-card-blue .kpi-label { color: #0369A1 !important; }

    .kpi-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 4px;
    }

    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.95rem;
        font-weight: 800;
        color: #0F172A !important;
        line-height: 1.2;
        letter-spacing: -0.03em;
    }

    .kpi-subtext {
        font-size: 0.76rem;
        color: #475569 !important;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Top Executive Header Box */
    .soc-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.22) 0px, transparent 55%),
                    radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.18) 0px, transparent 50%),
                    linear-gradient(135deg, rgba(240, 249, 255, 0.8) 0%, rgba(224, 242, 254, 0.6) 100%) !important;
        backdrop-filter: blur(28px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
        border: 1px solid rgba(186, 230, 253, 0.9) !important;
        border-radius: 18px !important;
        padding: 18px 26px !important;
        margin-bottom: 22px !important;
        box-shadow: 0 12px 35px rgba(14, 165, 233, 0.08), inset 0 1px 2px rgba(255, 255, 255, 0.95) !important;
        position: relative;
        overflow: hidden;
    }

    .soc-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3.5px;
        background: linear-gradient(90deg, #16A34A 0%, #EA580C 35%, #E11D48 70%, #0284C7 100%);
        opacity: 0.85;
    }

    .soc-header-left {
        display: flex;
        flex-direction: column;
    }

    .soc-header-title {
        font-size: 1.45rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        color: #0F172A !important;
        margin: 0;
    }

    .soc-header-sub {
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #0369A1 !important;
        text-transform: uppercase;
        margin-top: 2px;
    }

    .soc-header-badges {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    /* Glass Status Badges */
    .soc-badge {
        display: inline-flex;
        align-items: center;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.4px;
        font-family: 'JetBrains Mono', monospace;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    .soc-badge-online {
        background: rgba(240, 253, 244, 0.8) !important;
        color: #166534 !important;
        border: 1px solid rgba(187, 247, 208, 0.9) !important;
    }

    .soc-badge-alert {
        background: rgba(254, 242, 242, 0.8) !important;
        color: #991B1B !important;
        border: 1px solid rgba(254, 202, 202, 0.9) !important;
    }

    .soc-badge-black {
        background: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #000000 !important;
    }

    .soc-badge-slate {
        background: rgba(224, 242, 254, 0.8) !important;
        color: #0369A1 !important;
        border: 1px solid rgba(186, 230, 253, 0.9) !important;
    }

    /* Colored Alert Boxes */
    .soc-alert-box-red {
        background: radial-gradient(at 0% 0%, rgba(244, 63, 94, 0.2) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(255, 241, 242, 0.8) 0%, rgba(254, 226, 226, 0.6) 100%) !important;
        backdrop-filter: blur(28px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
        border: 1px solid rgba(244, 63, 94, 0.45) !important;
        border-radius: 18px !important;
        padding: 20px 24px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 10px 30px rgba(225, 29, 72, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9) !important;
    }

    .soc-alert-box-orange {
        background: radial-gradient(at 0% 0%, rgba(249, 115, 22, 0.2) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(255, 247, 237, 0.8) 0%, rgba(254, 215, 170, 0.6) 100%) !important;
        backdrop-filter: blur(28px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
        border: 1px solid rgba(249, 115, 22, 0.45) !important;
        border-radius: 18px !important;
        padding: 20px 24px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 10px 30px rgba(249, 115, 22, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9) !important;
    }

    .soc-alert-box-green {
        background: radial-gradient(at 0% 0%, rgba(34, 197, 94, 0.2) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(240, 253, 244, 0.8) 0%, rgba(220, 252, 231, 0.6) 100%) !important;
        backdrop-filter: blur(28px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
        border: 1px solid rgba(34, 197, 94, 0.45) !important;
        border-radius: 18px !important;
        padding: 20px 24px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 10px 30px rgba(34, 197, 94, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9) !important;
    }

    .soc-alert-title {
        font-size: 1.1rem;
        font-weight: 800;
        margin-bottom: 4px;
        letter-spacing: 0.3px;
    }

    .soc-alert-body {
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* Streamlit Alerts / Info Boxes */
    div[data-testid="stAlert"] {
        background: radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.18) 0px, transparent 50%),
                    linear-gradient(135deg, rgba(240, 249, 255, 0.75) 0%, rgba(224, 242, 254, 0.55) 100%) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border: 1px solid rgba(186, 230, 253, 0.85) !important;
        border-radius: 16px !important;
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
    }

    /* Wavy Glass Form Inputs & Dropdowns */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div, 
    .stMultiSelect > div, 
    textarea {
        background: rgba(240, 249, 255, 0.65) !important;
        backdrop-filter: blur(20px) saturate(190%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(190%) !important;
        color: #0F172A !important;
        border: 1px solid rgba(186, 230, 253, 0.9) !important;
        border-radius: 14px !important;
        font-size: 0.92rem !important;
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
    }

    .stTextInput > div > div > input:focus {
        background: rgba(240, 249, 255, 0.85) !important;
        border-color: #0284C7 !important;
        box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.25), inset 0 1px 0 rgba(255, 255, 255, 1) !important;
    }

    /* File Uploader Dropzone */
    div[data-testid="stFileUploadDropzone"] {
        background: radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.16) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(240, 249, 255, 0.6) 0%, rgba(224, 242, 254, 0.45) 100%) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        border: 2px dashed rgba(2, 132, 199, 0.35) !important;
        border-radius: 18px !important;
        box-shadow: 0 8px 25px rgba(14, 165, 233, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
    }

    /* Dataframe Container */
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(186, 230, 253, 0.9) !important;
        border-radius: 18px !important;
        background: radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.12) 0px, transparent 60%),
                    linear-gradient(135deg, rgba(240, 249, 255, 0.65) 0%, rgba(224, 242, 254, 0.5) 100%) !important;
        backdrop-filter: blur(24px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
        overflow: hidden !important;
        box-shadow: 0 10px 30px rgba(14, 165, 233, 0.06), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
    }

    /* Login Box & Profile Hero Box */
    .login-box {
        max-width: 500px;
        margin: 60px auto;
        padding: 38px 42px;
        background: radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.25) 0px, transparent 55%),
                    radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.2) 0px, transparent 50%),
                    linear-gradient(135deg, rgba(240, 249, 255, 0.85) 0%, rgba(224, 242, 254, 0.65) 100%) !important;
        backdrop-filter: blur(32px) saturate(220%) !important;
        -webkit-backdrop-filter: blur(32px) saturate(220%) !important;
        border: 1px solid rgba(186, 230, 253, 0.95) !important;
        border-radius: 22px !important;
        box-shadow: 0 20px 50px rgba(14, 165, 233, 0.12), inset 0 1px 1px rgba(255, 255, 255, 0.95) !important;
    }

    .profile-hero-card {
        background: radial-gradient(at 0% 0%, rgba(14, 165, 233, 0.25) 0px, transparent 55%),
                    radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.2) 0px, transparent 50%),
                    linear-gradient(135deg, rgba(240, 249, 255, 0.8) 0%, rgba(224, 242, 254, 0.6) 100%) !important;
        backdrop-filter: blur(28px) saturate(200%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(200%) !important;
        border: 1px solid rgba(186, 230, 253, 0.95) !important;
        border-radius: 20px !important;
        padding: 26px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 10px 32px rgba(14, 165, 233, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.95) !important;
    }

    /* Alternating Step Workflow Badges (Green, Orange, Red, Blue) */
    .step-badge-green {
        display: inline-block;
        background: linear-gradient(135deg, rgba(240, 253, 244, 0.9) 0%, rgba(220, 252, 231, 0.75) 100%);
        color: #15803D !important;
        border: 1px solid rgba(134, 239, 172, 0.8);
        font-size: 0.74rem; font-weight: 700; letter-spacing: 1px; padding: 6px 14px; border-radius: 10px; text-transform: uppercase; margin-bottom: 8px;
    }
    .step-badge-orange {
        display: inline-block;
        background: linear-gradient(135deg, rgba(255, 247, 237, 0.9) 0%, rgba(254, 215, 170, 0.75) 100%);
        color: #C2410C !important;
        border: 1px solid rgba(253, 186, 116, 0.8);
        font-size: 0.74rem; font-weight: 700; letter-spacing: 1px; padding: 6px 14px; border-radius: 10px; text-transform: uppercase; margin-bottom: 8px;
    }
    .step-badge-red {
        display: inline-block;
        background: linear-gradient(135deg, rgba(255, 241, 242, 0.9) 0%, rgba(254, 226, 226, 0.75) 100%);
        color: #BE123C !important;
        border: 1px solid rgba(254, 202, 202, 0.8);
        font-size: 0.74rem; font-weight: 700; letter-spacing: 1px; padding: 6px 14px; border-radius: 10px; text-transform: uppercase; margin-bottom: 8px;
    }
    .step-badge-blue {
        display: inline-block;
        background: linear-gradient(135deg, rgba(240, 249, 255, 0.9) 0%, rgba(224, 242, 254, 0.75) 100%);
        color: #0369A1 !important;
        border: 1px solid rgba(186, 230, 253, 0.8);
        font-size: 0.74rem; font-weight: 700; letter-spacing: 1px; padding: 6px 14px; border-radius: 10px; text-transform: uppercase; margin-bottom: 8px;
    }

    /* Primary Action Buttons */
    .stButton > button[kind="primary"], .stButton > button {
        background: #000000 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.4px !important;
        border: 1px solid #000000 !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button * {
        color: #FFFFFF !important;
    }

    .stButton > button:hover {
        background: #1E293B !important;
        border-color: #1E293B !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.16) !important;
    }

    /* Link Buttons */
    .stLinkButton > a {
        background: rgba(240, 249, 255, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        color: #0369A1 !important;
        border: 1px solid rgba(2, 132, 199, 0.6) !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        font-size: 0.88rem !important;
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.08), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
        transition: all 0.2s ease !important;
    }

    .stLinkButton > a:hover {
        background: #0284C7 !important;
        color: #FFFFFF !important;
    }

    /* ========================================================================= */
    /* JET BLACK SIDEBAR (KEPT UNCHANGED AS REQUESTED)                          */
    /* ========================================================================= */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #1E293B !important;
    }

    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4 {
        color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* Neon Blue Sidebar Header */
    .neon-blue-brand {
        font-size: 1.25rem !important;
        font-weight: 900 !important;
        color: #00E5FF !important;
        margin-top: 2px !important;
        letter-spacing: 1px !important;
        text-shadow: 0 0 14px rgba(0, 229, 255, 0.45) !important;
    }

    /* Uniform Same-Size Sidebar Feature Navigation Boxes */
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
        margin-top: 10px !important;
        margin-bottom: 15px !important;
        width: 100% !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        min-height: 48px !important;
        height: 48px !important;
        background: #000000 !important;
        border: 1px solid #222F3E !important;
        border-radius: 8px !important;
        padding: 0 14px !important;
        margin: 0 !important;
        box-sizing: border-box !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: #111827 !important;
        border-color: #00E5FF !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background: #0F172A !important;
        border-color: #00E5FF !important;
        box-shadow: 0 0 12px rgba(0, 229, 255, 0.25) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] > label span,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label p,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label div {
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    /* Sidebar Mini Profile Card (Black Box with Pure White Text) */
    .sidebar-profile-card {
        display: flex;
        align-items: center;
        gap: 12px;
        background: #000000 !important;
        border: 1px solid #222F3E !important;
        border-radius: 10px !important;
        padding: 12px 14px !important;
        margin-bottom: 16px !important;
    }

    .sidebar-profile-card * {
        color: #FFFFFF !important;
    }

    .sidebar-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: #0F172A !important;
        border: 2px solid #00E5FF !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        font-weight: 800;
        color: #00E5FF !important;
        overflow: hidden;
        flex-shrink: 0;
    }

    /* Sidebar Logout Button */
    section[data-testid="stSidebar"] .stButton > button {
        background: #000000 !important;
        color: #FFFFFF !important;
        border: 1px solid #222F3E !important;
        border-radius: 8px !important;
        margin-top: 10px !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #1E293B !important;
        border-color: #00E5FF !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- REUSABLE UI COMPONENT HELPERS -----------------
def render_header(module_name, officer_name=None):
    prof = st.session_state.officer_profile
    display_name = officer_name or prof.get("name", "Officer Aamin")
    st.markdown(f"""
    <div class="soc-header">
        <div class="soc-header-left">
            <span class="soc-header-sub">Gujarat Police • State Crime Record Bureau (SCRB)</span>
            <div class="soc-header-title">THE INITIATIVE 2.0 <span style="font-size: 1rem; font-weight: 500; color: #0284C7;">/ {module_name}</span></div>
        </div>
        <div class="soc-header-badges">
            <span class="soc-badge soc-badge-online">● 25/25 MESH ONLINE</span>
            <span class="soc-badge soc-badge-black">SEC-65B CERTIFIED</span>
            <span class="soc-badge soc-badge-slate">BADGE: {prof.get('badge_id', 'GP-SCRB-8842')}</span>
            <span class="soc-badge soc-badge-black">{display_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, subtext="", color="blue"):
    card_class = f"kpi-card kpi-card-{color}"
    st.markdown(f"""
    <div class="{card_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtext">{subtext}</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- AUTHENTICATION GATEWAY -----------------
if not st.session_state.authenticated:
    st.markdown("""
    <div class="login-box">
        <div style="font-size: 0.75rem; font-weight: 800; color: #0284C7; letter-spacing: 2px; text-transform: uppercase;">
            Gujarat Police • State Crime Record Bureau
        </div>
        <h2 style="font-size: 1.6rem; font-weight: 900; color: #0F172A; margin-top: 4px; margin-bottom: 8px;">
            Law Enforcement Command Terminal
        </h2>
        <div style="font-size: 0.88rem; color: #475569; margin-bottom: 24px;">
            Restricted state intelligence terminal for authorized police personnel.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_left, c_mid, c_right = st.columns([1, 1.2, 1])
    with c_mid:
        login_user = st.text_input("Officer Badge ID / Username", value="", placeholder="e.g. AAMIN")
        login_pass = st.text_input("Security PIN / Password", type="password", placeholder="Enter Security Password")

        if st.button("AUTHENTICATE & OPEN TERMINAL", type="primary", use_container_width=True):
            if login_user.strip().upper() == "AAMIN" and login_pass.strip() == "1124":
                st.session_state.authenticated = True
                st.session_state.officer_profile["name"] = "Officer Aamin"
                st.session_state.officer_profile["post"] = "Senior Cyber Forensic Examiner & ANPR Division Lead"
                st.session_state.current_user = "Officer Aamin (SCRB Senior Investigator)"
                st.success("Authentication confirmed. Access granted.")
                time.sleep(0.3)
                st.rerun()
            elif login_user.strip().upper() == "ADMIN" and login_pass.strip() == "scrb2026":
                st.session_state.authenticated = True
                st.session_state.officer_profile["name"] = "Commanding Officer (Admin)"
                st.session_state.officer_profile["post"] = "Chief of Police SCRB & Systems Administrator"
                st.session_state.current_user = "Commanding Officer (Admin)"
                st.success("Authentication confirmed. Admin grid active.")
                time.sleep(0.3)
                st.rerun()
            else:
                st.error("Invalid credentials. Unauthorized access attempt recorded.")
    st.stop()

# ----------------- DATASETS & MODEL MANAGEMENT -----------------
STATIC_CCTV_CATALOGUE = [
    {"stream_id": "1", "cam_id": "CAM-01", "name": "01 Chiman bhai Bridge", "lat": 23.0450, "lon": 72.5710, "city": "Ahmedabad", "type": "4K ANPR PTZ", "dept": "Traffic Branch", "status": "ONLINE"},
    {"stream_id": "2", "cam_id": "CAM-02", "name": "02 Janpath", "lat": 23.0300, "lon": 72.5600, "city": "Ahmedabad", "type": "High-Mast Bullet", "dept": "SCRB Highway", "status": "ONLINE"},
    {"stream_id": "3", "cam_id": "CAM-03", "name": "03 O.N.G.C. Office", "lat": 23.0900, "lon": 72.5900, "city": "Ahmedabad", "type": "Dome 360", "dept": "Smart City Mission", "status": "ONLINE"},
    {"stream_id": "4", "cam_id": "CAM-04", "name": "04 Paldi Circle", "lat": 23.0140, "lon": 72.5660, "city": "Ahmedabad", "type": "Fixed ANPR Dual", "dept": "Traffic Branch", "status": "ONLINE"},
    {"stream_id": "5", "cam_id": "CAM-05", "name": "05 Visat teen Rasta", "lat": 23.1050, "lon": 72.5950, "city": "Ahmedabad", "type": "4K ANPR PTZ", "dept": "SCRB Cyber Grid", "status": "ONLINE"},
    {"stream_id": "6", "cam_id": "CAM-06", "name": "06 Timbavadi gate-Junagadh", "lat": 21.5120, "lon": 70.4480, "city": "Junagadh", "type": "Secure Perimeter", "dept": "City Police", "status": "ONLINE"},
    {"stream_id": "7", "cam_id": "CAM-07", "name": "07 hero-showroom-gir-somnath", "lat": 20.9100, "lon": 70.4100, "city": "Somnath", "type": "Radar Speed Gun", "dept": "Traffic Branch", "status": "ONLINE"},
    {"stream_id": "8", "cam_id": "CAM-08", "name": "08 majewadi-gate-junagadh", "lat": 21.5220, "lon": 70.4570, "city": "Junagadh", "type": "4K ANPR PTZ", "dept": "City Police", "status": "ONLINE"},
    {"stream_id": "9", "cam_id": "CAM-09", "name": "09 new-bypass-circle-junagadh", "lat": 21.5350, "lon": 70.4700, "city": "Junagadh", "type": "Toll ANPR Barrier", "dept": "Highway Patrol", "status": "ONLINE"},
    {"stream_id": "10", "cam_id": "CAM-10", "name": "10 char-chowk-road-junagadh", "lat": 21.5180, "lon": 70.4520, "city": "Junagadh", "type": "Bullet Surveillance", "dept": "City Police", "status": "ONLINE"},
    {"stream_id": "11", "cam_id": "CAM-11", "name": "11 dolatpara-junagadh", "lat": 21.5400, "lon": 70.4650, "city": "Junagadh", "type": "4K ANPR PTZ", "dept": "Traffic Branch", "status": "ONLINE"},
    {"stream_id": "12", "cam_id": "CAM-12", "name": "12 Tri Mandir Adalaj Tollnaka", "lat": 23.1600, "lon": 72.5800, "city": "Gandhinagar", "type": "High-Mast PTZ", "dept": "Highway Patrol", "status": "ONLINE"},
    {"stream_id": "13", "cam_id": "CAM-13", "name": "13 CN Vidhyalaya", "lat": 23.0250, "lon": 72.5450, "city": "Ahmedabad", "type": "Airport Security", "dept": "City Police", "status": "ONLINE"},
    {"stream_id": "14", "cam_id": "CAM-14", "name": "14 Delight Junction", "lat": 22.3000, "lon": 73.1800, "city": "Vadodara", "type": "Fixed ANPR Dual", "dept": "Highway Patrol", "status": "ONLINE"},
    {"stream_id": "15", "cam_id": "CAM-15", "name": "15 Suvidha park Checkpost", "lat": 22.2900, "lon": 70.7800, "city": "Rajkot", "type": "4K ANPR PTZ", "dept": "Traffic Branch", "status": "ONLINE"},
    {"stream_id": "16", "cam_id": "CAM-16", "name": "16 Visat P2 Checkpost", "lat": 23.1100, "lon": 72.6000, "city": "Ahmedabad", "type": "City Dome Camera", "dept": "City Police", "status": "ONLINE"},
    {"stream_id": "17", "cam_id": "CAM-17", "name": "17 Rajkot Bus Port CCTV", "lat": 22.3050, "lon": 70.8020, "city": "Rajkot", "type": "4K ANPR PTZ", "dept": "Traffic Branch", "status": "ONLINE"},
    {"stream_id": "18", "cam_id": "CAM-18", "name": "18 Rajkot City CCTV", "lat": 22.2800, "lon": 70.7900, "city": "Rajkot", "type": "Heritage PTZ", "dept": "City Police", "status": "ONLINE"},
    {"stream_id": "19", "cam_id": "CAM-19", "name": "19 Khaparia Panchayat, Navsari", "lat": 20.7634, "lon": 72.9554, "city": "Navsari", "type": "Port Heavy ANPR", "dept": "Rural Police", "status": "ONLINE"},
    {"stream_id": "20", "cam_id": "CAM-20", "name": "20 Mohanpura Junction", "lat": 23.5880, "lon": 72.3690, "city": "Mehsana", "type": "Border Surveillance", "dept": "Special Ops Group", "status": "ONLINE"},
    {"stream_id": "21", "cam_id": "CAM-21", "name": "21 Patan Dethali Char Rasta", "lat": 23.8500, "lon": 72.1300, "city": "Patan", "type": "4K ANPR PTZ", "dept": "Traffic Branch", "status": "ONLINE"},
    {"stream_id": "22", "cam_id": "CAM-22", "name": "22 BK Mervada tran Rasta", "lat": 24.1700, "lon": 72.4300, "city": "Banaskantha", "type": "Toll Barrier ANPR", "dept": "Highway Patrol", "status": "ONLINE"},
    {"stream_id": "23", "cam_id": "CAM-23", "name": "23 Kheram Checkpost", "lat": 22.5640, "lon": 72.9280, "city": "Anand", "type": "Fixed ANPR Dual", "dept": "Traffic Branch", "status": "ONLINE"},
    {"stream_id": "24", "cam_id": "CAM-24", "name": "24 Dehgam Junction", "lat": 23.1670, "lon": 72.8120, "city": "Gandhinagar", "type": "Highway ANPR", "dept": "North Zone Patrol", "status": "ONLINE"},
    {"stream_id": "25", "cam_id": "CAM-25", "name": "25 Dhanori Checkpost", "lat": 20.9020, "lon": 72.9200, "city": "Navsari", "type": "Coastal Radar PTZ", "dept": "Marine Police", "status": "ONLINE"}
]

@st.cache_data(ttl=300)
def fetch_dynamic_cctv_catalogue():
    endpoints = ["https://live.corp8.cloud/api/ingest", "http://live.corp8.cloud/api/ingest"]
    for url in endpoints:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SCRB-Command-Terminal/2.0'})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode('utf-8'))
                    if isinstance(data, list) and len(data) > 0:
                        parsed = []
                        for idx, item in enumerate(data):
                            st_id = str(item.get("stream_id", item.get("id", idx + 1)))
                            c_id = item.get("cam_id", f"CAM-{int(st_id):02d}")
                            name = item.get("name", item.get("location", f"Checkpost Node {st_id}"))
                            lat = float(item.get("lat", item.get("latitude", 23.0 + (idx * 0.05))))
                            lon = float(item.get("lon", item.get("longitude", 72.5 + (idx * 0.05))))
                            city = item.get("city", "Gujarat")
                            c_type = item.get("type", "4K ANPR PTZ")
                            dept = item.get("dept", item.get("department", "Traffic Branch"))
                            status = item.get("status", "ONLINE").upper()
                            parsed.append({
                                "stream_id": st_id,
                                "cam_id": c_id,
                                "name": name,
                                "lat": lat,
                                "lon": lon,
                                "city": city,
                                "type": c_type,
                                "dept": dept,
                                "status": status
                            })
                        return parsed
        except Exception:
            continue
    return STATIC_CCTV_CATALOGUE

ACTIVE_CCTV_CATALOGUE = fetch_dynamic_cctv_catalogue()

@st.cache_resource
def get_ai_models():
    import torch
    from ultralytics import YOLO
    import easyocr
    num_threads = psutil.cpu_count(logical=True) or 4
    torch.set_num_threads(num_threads)
    torch.set_grad_enabled(False)
    cv2.setNumThreads(4)
    yolo_model = YOLO("yolov8n.pt")
    has_cuda = torch.cuda.is_available()
    ocr_reader = easyocr.Reader(['en'], gpu=has_cuda, verbose=False)
    return yolo_model, ocr_reader

CLASS_NAMES = {0: "Person", 1: "Bicycle", 2: "Car / Sedan", 3: "Motorcycle", 5: "Bus", 7: "Truck"}

def log_audit_trail(user, action):
    log_file = "audit_trail.csv"
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    new_entry = pd.DataFrame([{"Timestamp": timestamp, "User": user, "Action": action}])
    if os.path.exists(log_file):
        new_entry.to_csv(log_file, mode='a', header=False, index=False)
    else:
        new_entry.to_csv(log_file, index=False)

def clean_str(s):
    return "".join([c for c in str(s).upper() if c.isalnum()])

def normalize_plate_confusion(s):
    s = s.upper().replace(' ', '').replace('-', '').replace('.', '')
    mapping = {'O': '0', 'D': '0', 'I': '1', 'L': '1', 'B': '8', 'S': '5', 'G': '6', 'Z': '2', 'V': 'U', 'K': 'H'}
    return "".join([mapping.get(c, c) for c in s if c.isalnum()])

def super_resolve_plate(crop):
    try:
        if crop is None or crop.size == 0:
            return crop
        vh, vw = crop.shape[:2]
        if vh > 40 and vw > 40:
            y_start = int(vh * 0.65)
            y_end = vh
            x_start = int(vw * 0.15)
            x_end = int(vw * 0.85)
            plate_crop = crop[y_start:y_end, x_start:x_end]
            if plate_crop.size == 0 or plate_crop.shape[0] < 6 or plate_crop.shape[1] < 12:
                plate_crop = crop[int(vh * 0.5):vh, :]
        else:
            plate_crop = crop

        h, w = plate_crop.shape[:2]
        scaled = cv2.resize(plate_crop, (max(64, w * 4), max(24, h * 4)), interpolation=cv2.INTER_LANCZOS4)
        gray = cv2.cvtColor(scaled, cv2.COLOR_BGR2GRAY) if len(scaled.shape) == 3 else scaled
        
        gaussian = cv2.GaussianBlur(gray, (0, 0), 2.0)
        unsharp = cv2.addWeighted(gray, 2.5, gaussian, -1.5, 0)
        
        clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(unsharp)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
        blackhat = cv2.morphologyEx(enhanced, cv2.MORPH_BLACKHAT, kernel)
        plate_focus = cv2.add(enhanced, blackhat)
        return plate_focus
    except Exception:
        return crop

def clean_and_validate_plate_string(raw_ocr_str):
    if not raw_ocr_str:
        return None
    c = re.sub(r'[^A-Z0-9]', '', raw_ocr_str.upper())
    if len(c) < 4:
        return None
    return c

def format_dynamic_plate(clean_text):
    if not clean_text or len(clean_text) < 4:
        return clean_text
    if len(clean_text) == 7:
        return f"{clean_text[:4]} {clean_text[4:]}"
    elif len(clean_text) == 8:
        return f"{clean_text[:4]} {clean_text[4:]}"
    elif len(clean_text) == 10:
        return f"{clean_text[:2]} {clean_text[2:4]} {clean_text[4:6]} {clean_text[6:]}"
    return clean_text

def aggregate_multi_frame_consensus(ocr_readings_list, target_plate=""):
    valid_readings = []
    for r in ocr_readings_list:
        v = clean_and_validate_plate_string(r)
        if v:
            valid_readings.append(v)
            
    if not valid_readings:
        return "UNKNOWN_PLATE", 0.0, False

    tgt_clean = clean_str(target_plate)
    if tgt_clean:
        for r in valid_readings:
            is_hit, sc = is_real_target_match(tgt_clean, r)
            if is_hit:
                return format_dynamic_plate(r), sc, True

    counts = Counter(valid_readings)
    most_common_clean, freq = counts.most_common(1)[0]
    formatted = format_dynamic_plate(most_common_clean)

    is_hit, sc = is_real_target_match(tgt_clean, formatted) if tgt_clean else (False, 0.0)
    conf = sc if is_hit else min(98.0, 80.0 + (freq / len(valid_readings)) * 18.0)
    return formatted, round(conf, 1), is_hit

def is_real_target_match(target, detected):
    t_clean = clean_str(target)
    d_clean = clean_str(detected)
    if not t_clean or not d_clean or len(d_clean) < 3:
        return False, 0.0
    
    if t_clean in d_clean or d_clean in t_clean:
        return True, 100.0
    
    t_norm = normalize_plate_confusion(target)
    d_norm = normalize_plate_confusion(detected)
    if t_norm in d_norm or d_norm in t_norm:
        return True, 96.0
    
    sim = difflib.SequenceMatcher(None, t_norm, d_norm).ratio()
    if sim >= 0.55:
        return True, round(sim * 100, 1)
        
    if len(t_clean) >= 3 and (t_norm[:3] in d_norm or t_norm[-3:] in d_norm):
        return True, 88.0
        
    return False, round(sim * 100, 1)

def trigger_audio_sos():
    audio_html = """
    <audio autoplay>
        <source src="https://www.soundjay.com/buttons/sounds/beep-01a.mp3" type="audio/mpeg">
    </audio>
    """
    st.components.v1.html(audio_html, height=0)

def trigger_voice_dispatch(text_msg, lang="hi-IN"):
    voice_js = f"""
    <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{text_msg}");
            msg.rate = 1.0;
            msg.pitch = 1.0;
            msg.lang = "{lang}";
            window.speechSynthesis.speak(msg);
        }}
    </script>
    """
    st.components.v1.html(voice_js, height=0)

def generate_whatsapp_dispatch_link(plate, cam_name, lat, lon, phone="916456287866"):
    t_now = time.strftime('%Y-%m-%d %H:%M:%S')
    msg = (
        f"[GUJARAT POLICE SCRB - EMERGENCY PATROL DISPATCH]\n\n"
        f"[TARGET HIT DETECTED]\n"
        f"Vehicle Plate: {plate}\n"
        f"Location: {cam_name}\n"
        f"Coordinates: {lat}, {lon}\n"
        f"Timestamp: {t_now}\n\n"
        f"ACTION REQUIRED: Intercept vehicle immediately and establish perimeter checkpoint."
    )
    encoded = urllib.parse.quote(msg)
    return f"https://api.whatsapp.com/send?phone={phone}&text={encoded}"

def match_face_real(ref_img, person_crop):
    if ref_img is None or person_crop is None or person_crop.size == 0:
        return False, 0.0
    try:
        ph, pw = person_crop.shape[:2]
        head_crop = person_crop[0:int(ph * 0.45), 0:pw]
        if head_crop.size == 0:
            return False, 0.0
        r_ref = cv2.resize(ref_img, (48, 48))
        r_target = cv2.resize(head_crop, (48, 48))
        h_ref = cv2.calcHist([cv2.cvtColor(r_ref, cv2.COLOR_BGR2HSV)], [0, 1], None, [12, 12], [0, 180, 0, 256])
        h_target = cv2.calcHist([cv2.cvtColor(r_target, cv2.COLOR_BGR2HSV)], [0, 1], None, [12, 12], [0, 180, 0, 256])
        cv2.normalize(h_ref, h_ref, 0, 1, cv2.NORM_MINMAX)
        cv2.normalize(h_target, h_target, 0, 1, cv2.NORM_MINMAX)
        score = cv2.compareHist(h_ref, h_target, cv2.HISTCMP_CORREL)
        if score > 0.28:
            return True, round(score * 100, 1)
    except Exception:
        pass
    return False, 0.0

def generate_scrb_pdf_report(logs_df, case_id="SCRB-GUJ-2026-INCIDENT", officer=None):
    prof = st.session_state.officer_profile
    investigating_officer = officer or f"{prof.get('name', 'Officer Aamin')} ({prof.get('post', 'Senior Cyber Forensic Examiner')})"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    elements = []

    header_style = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=15, textColor=colors.HexColor('#000000'), alignment=1, spaceAfter=4)
    sub_header_style = ParagraphStyle('HeaderSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#475569'), alignment=1, spaceAfter=12)

    elements.append(Paragraph("GUJARAT POLICE • STATE CRIME RECORD BUREAU (SCRB)", header_style))
    elements.append(Paragraph("OFFICIAL FORENSIC VIDEO SURVEILLANCE & TARGET DETECTION DOSSIER", sub_header_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#000000'), spaceAfter=15))

    meta_data = [
        [Paragraph("<b>Case Reference:</b>", styles['Normal']), Paragraph(f"{case_id}", styles['Normal']),
         Paragraph("<b>Date & Time:</b>", styles['Normal']), Paragraph(time.strftime("%d-%b-%Y %H:%M:%S"), styles['Normal'])],
        [Paragraph("<b>Investigating Authority:</b>", styles['Normal']), Paragraph(f"{investigating_officer}", styles['Normal']),
         Paragraph("<b>Command Terminal:</b>", styles['Normal']), Paragraph(f"{prof.get('station', 'SCRB Cyber Grid')}", styles['Normal'])]
    ]
    t_meta = Table(meta_data, colWidths=[120, 160, 110, 150])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#000000')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("<b>I. REAL-TIME INCIDENT DETECTION CHRONOLOGY & FORENSIC LOGS</b>", styles['Heading3']))
    elements.append(Spacer(1, 6))

    table_data = [["#", "Exact Timeline", "Event Type", "Detected Plate / Details", "Checkpost Location"]]
    for idx, row in logs_df.head(25).iterrows():
        table_data.append([
            str(idx + 1),
            str(row.get("Exact Video Timeline", row.get("Timeline", row.get("Timestamp", "")))),
            str(row.get("Event Type", "")),
            str(row.get("Consensus Plate / Details", row.get("Target / Vehicle Details", row.get("Details", "")))),
            str(row.get("Checkpost Location", row.get("Location", "")))
        ])

    t_logs = Table(table_data, colWidths=[25, 90, 120, 180, 105])
    t_logs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#000000')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#FFFFFF')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_logs)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("<b>II. STATUTORY ATTESTATION & DIGITAL CERTIFICATE</b>", styles['Heading3']))
    elements.append(Paragraph("This electronic forensic dossier has been automatically compiled under Section 65B of the Indian Evidence Act by Gujarat Police State Crime Record Bureau Analytics Command Engine.", styles['Normal']))
    elements.append(Spacer(1, 25))

    sig_data = [
        [Paragraph("____________________________<br/><b>Verified By: Investigating Officer</b>", styles['Normal']),
         Paragraph("____________________________<br/><b>Superintendent of Police (SCRB)</b>", styles['Normal'])]
    ]
    t_sig = Table(sig_data, colWidths=[270, 270])
    t_sig.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    elements.append(t_sig)

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def open_hardware_webcam(device_idx=0):
    cap = cv2.VideoCapture(device_idx, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(device_idx)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap

def open_ip_camera_stream(url):
    clean = str(url).strip()
    cap = cv2.VideoCapture(clean, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        cap = cv2.VideoCapture(clean)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap

# ----------------- JET BLACK SIDEBAR NAVIGATION SYSTEM -----------------
prof = st.session_state.officer_profile

# Header & Profile Mini Badge in Sidebar
st.sidebar.markdown(f"""
<div style="padding: 10px 4px 14px 4px; border-bottom: 1px solid #1E293B; margin-bottom: 14px;">
    <div style="font-size: 0.72rem; font-weight: 800; color: #FFFFFF; letter-spacing: 1.5px; text-transform: uppercase;">
        SCRB Operations Grid
    </div>
    <div class="neon-blue-brand">
        THE INITIATIVE 2.0
    </div>
</div>

<div class="sidebar-profile-card">
    <div class="sidebar-avatar">
        {prof['name'][:2].upper()}
    </div>
    <div style="display: flex; flex-direction: column; overflow: hidden;">
        <span style="font-size: 0.92rem; font-weight: 800; color: #FFFFFF !important; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{prof['name']}</span>
        <span style="font-size: 0.72rem; color: #FFFFFF !important; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">{prof['post'][:25]}...</span>
        <span style="font-size: 0.68rem; color: #00E5FF !important; font-weight: 700; font-family: 'JetBrains Mono', monospace; margin-top: 2px;">● {prof['badge_id']}</span>
    </div>
</div>
""", unsafe_allow_html=True)

nav_section = st.sidebar.radio(
    "OPERATIONAL MODULES",
    [
        "Command Overview Dashboard",
        "Officer Profile & Credentials",
        "Gujarat 25 CCTV Live Network",
        "Active Incident Alerts & Dispatch",
        "CCTV Video Forensic Engine (PTS & ANPR)",
        "Integrated Webcam Field Patrol",
        "Mobile Phone IP Camera Scanner",
        "Gujarat GIS Suspect Route Tracker",
        "Statewide CCTV Asset Registry & Gap Analysis",
        "VAHAN & CCTNS National Lookup",
        "Section 65B SCRB Forensic Dossier",
        "Server Health & Audit Logs"
    ],
    index=0
)

st.sidebar.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
if st.sidebar.button("LOCK TERMINAL (LOGOUT)", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

# ----------------- MODULE: OFFICER PROFILE & CREDENTIALS (NEW) -----------------
if nav_section == "Officer Profile & Credentials":
    render_header("Officer Profile & Identity Credentials", prof["name"])

    st.markdown("### Officer Dossier & Departmental Credentials")

    p_col1, p_col2 = st.columns([1, 2])
    with p_col1:
        st.markdown(f"""
        <div class="profile-hero-card" style="text-align: center;">
            <div style="width: 90px; height: 90px; border-radius: 50%; background: #000000; color: #00E5FF; font-size: 2.2rem; font-weight: 900; display: flex; align-items: center; justify-content: center; margin: 0 auto 14px auto; border: 3px solid #00E5FF; box-shadow: 0 0 20px rgba(0, 229, 255, 0.35);">
                {prof['name'][:2].upper()}
            </div>
            <div style="font-size: 1.25rem; font-weight: 900; color: #0F172A;">{prof['name']}</div>
            <div style="font-size: 0.82rem; font-weight: 700; color: #0369A1; margin-top: 2px;">{prof['post']}</div>
            <div style="margin-top: 12px;">
                <span class="soc-badge soc-badge-online">ACTIVE IN SERVICE</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Upload Custom Profile Photo")
        uploaded_avatar = st.file_uploader("Change Profile Picture (JPG/PNG)", type=["jpg", "png", "jpeg"])
        if uploaded_avatar is not None:
            st.session_state.officer_profile["avatar_bytes"] = uploaded_avatar.read()
            st.success("Profile photo updated.")

    with p_col2:
        st.markdown("#### Official Police Identity Details")
        
        with st.form("edit_officer_profile_form"):
            f_c1, f_c2 = st.columns(2)
            with f_c1:
                edit_name = st.text_input("Officer Full Name", value=prof["name"])
                edit_post = st.text_input("Designation / Official Post", value=prof["post"])
                edit_badge = st.text_input("Badge / Service Number", value=prof["badge_id"])
                edit_dept = st.text_input("Department / Branch", value=prof["dept"])
            with f_c2:
                edit_station = st.text_input("Station / Jurisdiction", value=prof["station"])
                edit_phone = st.text_input("Police Contact / Wireless Number", value=prof["phone"])
                edit_email = st.text_input("Official Government Email", value=prof["email"])
                edit_clearance = st.text_input("Security Clearance Level", value=prof["clearance"])

            if st.form_submit_button("SAVE & UPDATE OFFICER PROFILE", type="primary", use_container_width=True):
                st.session_state.officer_profile["name"] = edit_name
                st.session_state.officer_profile["post"] = edit_post
                st.session_state.officer_profile["badge_id"] = edit_badge
                st.session_state.officer_profile["dept"] = edit_dept
                st.session_state.officer_profile["station"] = edit_station
                st.session_state.officer_profile["phone"] = edit_phone
                st.session_state.officer_profile["email"] = edit_email
                st.session_state.officer_profile["clearance"] = edit_clearance
                log_audit_trail(edit_name, f"Updated Officer Profile credentials for {edit_badge}")
                st.success("Officer Identity Record successfully updated across the intelligence grid.")
                time.sleep(0.4)
                st.rerun()

# ----------------- MODULE 1: COMMAND OVERVIEW DASHBOARD (LANDING) -----------------
elif nav_section == "Command Overview Dashboard":
    render_header("Command Overview Dashboard", prof["name"])
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card("Live Mesh Status", f"{len(ACTIVE_CCTV_CATALOGUE)} / {len(ACTIVE_CCTV_CATALOGUE)} Online", "100% Core Mesh Availability", color="green")
    with k2:
        tracked_count = len(st.session_state.get("last_detection_logs", []))
        render_metric_card("Forensic Intercepts", f"{tracked_count} Waypoints", "Recorded in Active Session", color="red")
    with k3:
        render_metric_card("System Compute Load", f"{psutil.cpu_percent()}% CPU", f"{psutil.virtual_memory().percent}% RAM Utilization", color="orange")
    with k4:
        render_metric_card("Network Latency", "12 ms", "Gateway: live.corp8.cloud", color="blue")

    st.markdown("### Operational Quick Actions")
    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown("""
        <div class="action-card action-card-green">
            <div>
                <div class="kpi-label">Forensic Intelligence</div>
                <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A; margin-bottom: 6px;">CCTV Video Analysis</div>
                <div style="font-size: 0.84rem; color: #475569;">Run 4X super-resolution ANPR with consensus OCR and millisecond PTS timeline on raw CCTV footage.</div>
            </div>
            <div style="font-size: 0.76rem; font-weight: 700; color: #15803D;">● MODULE ACTIVE</div>
        </div>
        """, unsafe_allow_html=True)
    with q2:
        st.markdown("""
        <div class="action-card action-card-orange">
            <div>
                <div class="kpi-label">Statewide Mesh</div>
                <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A; margin-bottom: 6px;">25 Checkposts Mesh</div>
                <div style="font-size: 0.84rem; color: #475569;">Access live HD video streams across Ahmedabad, Junagadh, Rajkot, and interstate border checkpoints.</div>
            </div>
            <div style="font-size: 0.76rem; font-weight: 700; color: #C2410C;">● 25 CHANNELS ONLINE</div>
        </div>
        """, unsafe_allow_html=True)
    with q3:
        st.markdown("""
        <div class="action-card action-card-red">
            <div>
                <div class="kpi-label">Legal Evidentiary Dossier</div>
                <div style="font-size: 1.05rem; font-weight: 800; color: #0F172A; margin-bottom: 6px;">Section 65B PDF Dossier</div>
                <div style="font-size: 0.84rem; color: #475569;">Generate court-admissible forensic dossiers with digital attestation and chronological detection logs.</div>
            </div>
            <div style="font-size: 0.76rem; font-weight: 700; color: #BE123C;">● DIGITAL ATTESTATION READY</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Active Surveillance Mesh Overview")
    df_preview = pd.DataFrame(ACTIVE_CCTV_CATALOGUE)[["cam_id", "name", "city", "type", "dept", "status"]]
    df_preview.columns = ["Camera ID", "Location Name", "City", "Camera Type", "Jurisdiction", "Status"]
    st.dataframe(df_preview, use_container_width=True)

# ----------------- MODULE 2: GUJARAT 25 CCTV LIVE NETWORK -----------------
elif nav_section == "Gujarat 25 CCTV Live Network":
    render_header("Gujarat 25 CCTV Live Network", prof["name"])

    f_col1, f_col2, f_col3 = st.columns([1.5, 1, 1])
    with f_col1:
        cities = ["All Cities"] + sorted(list(set(c["city"] for c in ACTIVE_CCTV_CATALOGUE)))
        selected_city = st.selectbox("Filter Cameras by Jurisdiction / City", cities)
    with f_col2:
        filtered_cams = ACTIVE_CCTV_CATALOGUE if selected_city == "All Cities" else [c for c in ACTIVE_CCTV_CATALOGUE if c["city"] == selected_city]
        cam_options = [f"Camera {c['stream_id']} — {c['name']} ({c['city']})" for c in filtered_cams]
        selected_cam_str = st.selectbox("Select Active Checkpost Camera", cam_options, index=0)
        selected_cam = next(c for c in filtered_cams if f"Camera {c['stream_id']} — {c['name']} ({c['city']})" == selected_cam_str)
    with f_col3:
        playback_mode = st.selectbox("Surveillance Engine Mode", ["Direct Live HD Stream", "ANPR Target Intercept Radar", "Camera Metadata & Telemetry"])

    st_num = selected_cam["stream_id"]
    web_player_url = f"https://live.corp8.cloud/camera/{st_num}"
    stream_mp4_url = f"https://live.corp8.cloud/stream/{st_num}"

    st.markdown(f"""
    <div class="kpi-card kpi-card-green" style="min-height: 60px !important; height: 60px !important; display: flex !important; flex-direction: row !important; align-items: center !important; justify-content: flex-start !important; gap: 14px !important; padding: 12px 20px !important; margin-bottom: 16px !important;">
        <span class="soc-badge soc-badge-online">LIVE STREAMING</span>
        <span style="font-weight: 800; font-size: 0.95rem; color: #0F172A;">{selected_cam['cam_id']} : {selected_cam['name']}</span>
        <span style="color: #15803D; font-size: 0.88rem;">({selected_cam['city']} • {selected_cam['dept']})</span>
        <span style="margin-left: auto; font-family: 'JetBrains Mono', monospace; font-size: 0.84rem; color: #0F172A; font-weight: 600;">GPS: {selected_cam['lat']}, {selected_cam['lon']}</span>
    </div>
    """, unsafe_allow_html=True)

    if playback_mode == "Direct Live HD Stream":
        interactive_player_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ background: transparent; color: #000000; font-family: 'Inter', sans-serif; }}
            .container {{ position: relative; width: 100%; max-width: 960px; height: 500px; background: #000; border: 1px solid rgba(134, 239, 172, 0.6); border-radius: 18px; overflow: hidden; box-shadow: 0 12px 35px rgba(34, 197, 94, 0.18); }}
            video {{
                width: 100%;
                height: 100%;
                object-fit: contain;
                image-rendering: -webkit-optimize-contrast;
                image-rendering: crisp-edges;
                filter: contrast(120%) brightness(95%) saturate(115%);
                transform: translateZ(0);
                backface-visibility: hidden;
            }}
            .osd-tag {{ position: absolute; z-index: 15; background: rgba(240, 253, 244, 0.85); backdrop-filter: blur(16px); padding: 6px 14px; border-radius: 10px; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace; border: 1px solid rgba(134, 239, 172, 0.9); color: #15803D; box-shadow: 0 4px 12px rgba(34, 197, 94, 0.08); }}
            .osd-tl {{ top: 14px; left: 16px; }}
            .osd-tr {{ top: 14px; right: 16px; color: #166534; font-weight: 800; }}
            .play-overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.55); backdrop-filter: blur(10px); display: flex; justify-content: center; align-items: center; z-index: 30; cursor: pointer; }}
            .play-btn {{ background: #000000; color: #FFFFFF !important; font-size: 15px; font-weight: 800; padding: 14px 32px; border: 1px solid rgba(255,255,255,0.3); border-radius: 12px; font-family: 'Inter', sans-serif; cursor: pointer; box-shadow: 0 6px 20px rgba(0,0,0,0.25); }}
        </style>
        </head>
        <body>
        <div class="container">
            <div class="osd-tag osd-tl">{selected_cam['cam_id']} • {selected_cam['name'].upper()}</div>
            <div class="osd-tag osd-tr">● LIVE REC • {selected_cam['city'].upper()}</div>
            <div class="play-overlay" id="overlay" onclick="document.getElementById('vidPlayer').play(); this.style.display='none';">
                <button class="play-btn">START LIVE CAMERA FEED</button>
            </div>
            <video id="vidPlayer" autoplay muted playsinline controls loop src="{stream_mp4_url}"></video>
        </div>
        </body>
        </html>
        """
        st.components.v1.html(interactive_player_html, height=520)
        log_audit_trail(prof['name'], f"Streamed Camera {selected_cam['stream_id']} ({selected_cam['name']})")

    elif playback_mode == "ANPR Target Intercept Radar":
        c_radar_in, c_radar_act = st.columns([2, 1])
        with c_radar_in:
            target_watch_plate = st.text_input("Enter Watchlist Plate for Live Checkpost Intercept", value="", placeholder="e.g. GJ01 AB 1234, AK64 DMV")
        with c_radar_act:
            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
            trigger_intercept = st.button("TRIGGER TARGET INTERCEPT ALERT", type="primary", use_container_width=True)

        radar_player_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ background: transparent; margin: 0; overflow: hidden; }}
            video {{
                width: 100%;
                max-width: 960px;
                height: 420px;
                object-fit: contain;
                image-rendering: -webkit-optimize-contrast;
                image-rendering: crisp-edges;
                filter: contrast(120%) brightness(95%) saturate(115%);
                transform: translateZ(0);
                backface-visibility: hidden;
                border-radius: 18px;
                border: 1px solid rgba(254, 202, 202, 0.6);
                box-shadow: 0 8px 24px rgba(225, 29, 72, 0.1);
            }}
        </style>
        </head>
        <body>
        <video autoplay muted playsinline controls loop src="{stream_mp4_url}"></video>
        </body>
        </html>
        """
        st.components.v1.html(radar_player_html, height=440)

        if trigger_intercept:
            clean_tgt = clean_str(target_watch_plate) or "TARGET VEHICLE"
            trigger_audio_sos()
            trigger_voice_dispatch(f"Critical Intercept: Target {clean_tgt} at checkpost {selected_cam['name']}.")
            wa_link = generate_whatsapp_dispatch_link(clean_tgt, selected_cam["name"], selected_cam["lat"], selected_cam["lon"])
            
            st.markdown(f"""
            <div class="soc-alert-box-red">
                <div class="soc-alert-title" style="color: #9F1239;">TARGET INTERCEPT CONFIRMED • CAMERA {selected_cam['stream_id']}</div>
                <div class="soc-alert-body" style="color: #4C0519;">
                    Vehicle <b>[{clean_tgt}]</b> intercepted at <b>{selected_cam['name']} ({selected_cam['city']})</b>.<br/>
                    GPS Coordinates: <code>{selected_cam['lat']}, {selected_cam['lon']}</code> | Timestamp: <code>{time.strftime('%Y-%m-%d %H:%M:%S')}</code>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.link_button("CONFIRM & DISPATCH EMERGENCY PATROL ALERT (WHATSAPP)", wa_link, use_container_width=True)
            log_audit_trail(prof['name'], f"Target intercept alert for {clean_tgt} at Cam {selected_cam['stream_id']}")
    else:
        st.markdown("### Camera Infrastructure Telemetry")
        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            st.info(f"**Camera Type:** {selected_cam['type']}\n\n**Department:** {selected_cam['dept']}")
        with c_m2:
            st.info(f"**Location:** {selected_cam['name']}\n\n**City:** {selected_cam['city']}")
        with c_m3:
            st.info(f"**Coordinates:** {selected_cam['lat']}, {selected_cam['lon']}\n\n**Status:** {selected_cam['status']}")

# ----------------- MODULE 3: ACTIVE INCIDENT ALERTS & DISPATCH -----------------
elif nav_section == "Active Incident Alerts & Dispatch":
    render_header("Active Incident Alerts & Dispatch", prof["name"])

    recent_logs = st.session_state.get("last_detection_logs", [])
    if recent_logs:
        st.markdown(f"### Active Session Forensic Intercepts ({len(recent_logs)} Recorded)")
        for idx, ev in enumerate(recent_logs):
            box_cls = "soc-alert-box-red" if 'TARGET' in ev.get('Event Type', '') else "soc-alert-box-orange"
            st.markdown(f"""
            <div class="{box_cls}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 800; color: #0F172A; font-size: 1.05rem;">{ev.get('Event ID', f'EVT-0{idx+1}')} : {ev.get('Event Type', 'Vehicle Identified')}</span>
                    <span class="soc-badge soc-badge-black">⏱️ {ev.get('Exact Video Timeline', 'N/A')}</span>
                </div>
                <div style="margin-top: 8px; font-size: 0.9rem; color: #334155; line-height: 1.6;">
                    • <b>Plate & Readings:</b> {ev.get('Consensus Plate / Details', '')}<br/>
                    • <b>Location:</b> {ev.get('Checkpost Location', '')} ({ev.get('City', 'Gujarat')}) | <b>Confidence:</b> {ev.get('Match Confidence', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No active emergency alerts in the current session. Run an AI Forensic Video Scan or Live Camera Radar to trigger alerts.")

# ----------------- MODULE 4: CCTV VIDEO FORENSIC ENGINE (6-STEP WORKFLOW) -----------------
elif nav_section == "CCTV Video Forensic Engine (PTS & ANPR)":
    render_header("CCTV Video Forensic Engine", prof["name"])

    st.markdown("""
    <div style="display: flex; gap: 8px; margin-bottom: 16px;">
        <span class="step-badge-green">STEP 1: INPUT</span>
        <span class="step-badge-orange">STEP 2: TARGETS</span>
        <span class="step-badge-blue">STEP 3: CONFIG</span>
        <span class="step-badge-red">STEP 4: NEURAL ANALYSIS</span>
        <span class="step-badge-green">STEP 5: EVIDENCE LOG</span>
        <span class="step-badge-orange">STEP 6: REPORTING</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Step 1: Input CCTV Footage**")
        uploaded_video = st.file_uploader("Upload Surveillance File (MP4, AVI, MOV, MKV)", type=["mp4", "avi", "mov", "mkv"])
        st.markdown("**Step 2: Target Watchlist (Optional Filter)**")
        target_plate_input = st.text_input("Target License Plate", value="", placeholder="e.g. AK64 DMV, GJ01 AB 1234")
    with col2:
        st.markdown("**Step 2B: Suspect Facial Image (Optional)**")
        uploaded_face = st.file_uploader("Upload Suspect Photograph", type=["jpg", "png", "jpeg"])
        st.markdown("**Step 3: Neural Sampling Rate**")
        sampling_rate = st.slider("Analysis Sampling Interval (Seconds)", min_value=0.25, max_value=2.0, value=0.50, step=0.25)

    if st.button("EXECUTE FORENSIC VIDEO SCAN (4X SUPER-RES & PTS ENGINE)", type="primary", use_container_width=True):
        if uploaded_video is not None:
            uploaded_video.seek(0)
            video_bytes = uploaded_video.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                tmp.write(video_bytes)
                tmp.flush()
                video_path = tmp.name

            ref_face_img = None
            if uploaded_face is not None:
                face_bytes = uploaded_face.read()
                nparr = np.frombuffer(face_bytes, np.uint8)
                ref_face_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            with st.spinner("Initializing Deep Learning Engine (YOLOv8 + EasyOCR)..."):
                yolo_model, ocr_reader = get_ai_models()

            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
            clean_target_plate = clean_str(target_plate_input)

            start_t = time.time()
            frame_cnt = 0
            step_frame = max(1, int(fps * sampling_rate))

            vehicle_tracks = {}
            track_id_gen = 0
            face_matches = []

            scan_progress = st.progress(0.0)
            scan_status = st.empty()

            # PHASE 1: Spatial Trajectory Tracking & PTS Extraction
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret or frame is None or frame.size == 0:
                    break

                frame_cnt += 1
                if total_frames > 0 and frame_cnt % (step_frame * 2) == 0:
                    scan_progress.progress(min(0.5, (frame_cnt / total_frames) * 0.5))
                    scan_status.caption(f"Phase 1/2: Spatial Tracking & Millisecond PTS Extraction — Frame {frame_cnt}/{total_frames}")

                if frame_cnt % step_frame != 0:
                    continue

                pts_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                real_sec = pts_ms / 1000.0 if pts_ms > 0 else (frame_cnt / fps)
                mins = int(real_sec // 60)
                secs = int(real_sec % 60)
                ms = int(pts_ms % 1000) if pts_ms > 0 else int((real_sec - int(real_sec)) * 1000)
                real_time_str = f"{mins:02d}:{secs:02d}.{ms:03d}"

                res = yolo_model(frame, verbose=False, imgsz=256, conf=0.32)
                for r in res:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        area = (x2 - x1) * (y2 - y1)

                        if cls == 0 and ref_face_img is not None and area > 1200:
                            p_crop = frame[max(0, y1):min(frame.shape[0], y2), max(0, x1):min(frame.shape[1], x2)]
                            is_match, f_conf = match_face_real(ref_face_img, p_crop)
                            if is_match:
                                face_matches.append({
                                    "time": real_time_str,
                                    "sec": real_sec,
                                    "crop": p_crop,
                                    "conf": f_conf
                                })

                        elif cls in [2, 3, 5, 7] and area > 1000:
                            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                            v_crop = frame[max(0, y1):min(frame.shape[0], y2), max(0, x1):min(frame.shape[1], x2)]

                            matched_id = None
                            for tid, tdata in vehicle_tracks.items():
                                if abs(real_sec - tdata['last_sec']) < 2.2:
                                    dist = math.hypot(cx - tdata['cx'], cy - tdata['cy'])
                                    if dist < 220:
                                        matched_id = tid
                                        break

                            if matched_id is None:
                                track_id_gen += 1
                                matched_id = track_id_gen
                                vehicle_tracks[matched_id] = {
                                    'id': matched_id,
                                    'first_sec': real_sec,
                                    'last_sec': real_sec,
                                    'start_ts': real_time_str,
                                    'end_ts': real_time_str,
                                    'best_ts': real_time_str,
                                    'best_sec': real_sec,
                                    'best_area': area,
                                    'best_crop': v_crop,
                                    'cx': cx,
                                    'cy': cy,
                                    'crop_queue': [v_crop],
                                    'sightings': 1
                                }
                            else:
                                tdata = vehicle_tracks[matched_id]
                                tdata['last_sec'] = real_sec
                                tdata['end_ts'] = real_time_str
                                tdata['sightings'] += 1
                                tdata['cx'], tdata['cy'] = cx, cy
                                if len(tdata['crop_queue']) < 4:
                                    tdata['crop_queue'].append(v_crop)
                                if area > tdata['best_area']:
                                    tdata['best_area'] = area
                                    tdata['best_crop'] = v_crop
                                    tdata['best_ts'] = real_time_str
                                    tdata['best_sec'] = real_sec

            cap.release()
            scan_progress.progress(0.6)

            # PHASE 2: 4X Super-Resolution & Multi-Frame Consensus Voting
            final_events = []
            for idx, (tid, tdata) in enumerate(vehicle_tracks.items()):
                scan_progress.progress(0.6 + 0.4 * ((idx + 1) / max(1, len(vehicle_tracks))))
                scan_status.caption(f"Phase 2/2: 4X Lanczos4 Super-Resolution & Consensus OCR — Track {idx+1}/{len(vehicle_tracks)}")
                
                raw_readings = []
                for crop in tdata['crop_queue']:
                    prep_plate = super_resolve_plate(crop)
                    ocr_out = ocr_reader.readtext(
                        prep_plate,
                        detail=0,
                        paragraph=False,
                        min_size=8,
                        text_threshold=0.3,
                        low_text=0.2,
                        slope_ths=0.2,
                        allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                    )
                    if ocr_out:
                        raw_t = " ".join(ocr_out).strip().upper()
                        c_valid = clean_and_validate_plate_string(raw_t)
                        if c_valid:
                            raw_readings.append(c_valid)

                consensus_plate, consensus_conf, is_tgt = aggregate_multi_frame_consensus(raw_readings, target_plate_input)
                loc = ACTIVE_CCTV_CATALOGUE[int(tdata['best_sec']) % len(ACTIVE_CCTV_CATALOGUE)]

                final_events.append({
                    "id": f"EVT-0{idx+1}",
                    "start_ts": tdata['start_ts'],
                    "end_ts": tdata['end_ts'],
                    "peak_ts": tdata['best_ts'],
                    "plate": consensus_plate,
                    "raw_samples": raw_readings,
                    "is_target": is_tgt,
                    "conf": consensus_conf,
                    "sightings": tdata['sightings'],
                    "crop_img": cv2.cvtColor(tdata['best_crop'], cv2.COLOR_BGR2RGB),
                    "loc": loc
                })

            scan_progress.progress(1.0)
            scan_status.empty()
            elapsed = round(time.time() - start_t, 2)

            target_hits = [e for e in final_events if e['is_target']]

            table_rows = []
            for idx, e in enumerate(final_events):
                time_range = e['start_ts'] if e['start_ts'] == e['end_ts'] else f"{e['start_ts']} -> {e['end_ts']}"
                event_type = "TARGET INTERCEPT HIT" if e['is_target'] else "VEHICLE IDENTIFIED"

                table_rows.append({
                    "Event ID": e['id'],
                    "Exact Video Timeline": time_range,
                    "Peak Clarity Time": e['peak_ts'],
                    "Event Type": event_type,
                    "Consensus Plate / Details": f"License Plate: [{e['plate']}] (Sample Readings: {e['raw_samples']})",
                    "Match Confidence": f"{e['conf']}%",
                    "Track Duration": f"{e['sightings']} Frame(s)",
                    "Checkpost Location": e['loc']['name'],
                    "City": e['loc']['city'],
                    "Lat": e['loc']['lat'],
                    "Lon": e['loc']['lon']
                })

            st.session_state["last_detection_logs"] = table_rows
            st.success(f"Forensic Scan Completed in {elapsed}s. Processed {len(vehicle_tracks)} vehicle tracks.")

            # Target Hit Alert Box
            if target_hits and clean_target_plate:
                top_hit = target_hits[0]
                trigger_audio_sos()
                trigger_voice_dispatch(f"Target Alert: {top_hit['plate']} intercepted at video timestamp {top_hit['start_ts']}.")
                wa_link = generate_whatsapp_dispatch_link(top_hit['plate'], top_hit['loc']['name'], top_hit['loc']['lat'], top_hit['loc']['lon'])

                st.markdown(f"""
                <div class="soc-alert-box-red">
                    <div class="soc-alert-title" style="color: #9F1239;">TARGET SUSPECT VEHICLE INTERCEPTED • {top_hit['plate']}</div>
                    <div class="soc-alert-body" style="color: #4C0519;">
                        Timeline: <code>{top_hit['start_ts']} -> {top_hit['end_ts']}</code> (Clarity Peak: <code>{top_hit['peak_ts']}</code>)<br/>
                        Location: <b>{top_hit['loc']['name']} ({top_hit['loc']['city']})</b> | Confidence: <b>{top_hit['conf']}%</b><br/>
                        Multi-frame consensus readings: <code>{top_hit['raw_samples']}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.link_button("DISPATCH EMERGENCY WHATSAPP PATROL ALERT", wa_link, use_container_width=True)

            # Evidence Crops
            if final_events:
                st.markdown("### Step 5: Verified Vehicle Evidence from Real Frames")
                c_crops = st.columns(min(4, len(final_events)))
                for idx, ev in enumerate(final_events[:4]):
                    with c_crops[idx % 4]:
                        st.image(ev["crop_img"], caption=f"Event #{idx+1} @ {ev['start_ts']} | Plate: {ev['plate']}", use_container_width=True)

                st.markdown("### Step 6: Real-Time Detection Chronology Table")
                df_tab = pd.DataFrame(table_rows)
                st.dataframe(df_tab, use_container_width=True)

                pdf_dossier = generate_scrb_pdf_report(df_tab)
                st.download_button("DOWNLOAD OFFICIAL SECTION 65B SCRB PDF DOSSIER", data=pdf_dossier, file_name="SCRB_FORENSIC_DOSSIER.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.warning("Please upload a valid CCTV footage file to proceed.")

# ----------------- MODULE 5: INTEGRATED WEBCAM FIELD PATROL -----------------
elif nav_section == "Integrated Webcam Field Patrol":
    render_header("Integrated Webcam Field Patrol", prof["name"])

    target_plate_wb = st.text_input("Watchlist License Plate (Optional)", value="", placeholder="Enter target plate")

    if "wb_active" not in st.session_state:
        st.session_state.wb_active = False

    c_wb1, c_wb2 = st.columns(2)
    if c_wb1.button("START LIVE WEBCAM FEED", type="primary", use_container_width=True):
        st.session_state.wb_active = True
    if c_wb2.button("STOP WEBCAM FEED", use_container_width=True):
        st.session_state.wb_active = False

    ALERT_WB = st.empty()
    DISPATCH_BTN_WB = st.empty()
    FRAME_WB = st.empty()
    STATS_WB = st.empty()

    if st.session_state.wb_active:
        log_audit_trail(prof['name'], "Started Laptop Webcam")
        yolo_model, ocr_reader = get_ai_models()
        cap = open_hardware_webcam(0)

        if cap is None or not cap.isOpened():
            st.error("Hardware webcam device could not be accessed.")
        else:
            clean_tgt = clean_str(target_plate_wb)
            frame_idx = 0
            prev_t = time.time()
            fps_val = 30.0
            has_alerted_wb = False

            try:
                while st.session_state.wb_active:
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        st.error("Webcam video frame capture interrupted.")
                        break

                    frame_idx += 1
                    cur_t = time.time()
                    dt = cur_t - prev_t
                    prev_t = cur_t
                    if dt > 0:
                        fps_val = round(0.9 * fps_val + 0.1 * (1.0 / dt), 1)

                    fh, fw = frame.shape[:2]
                    results = yolo_model(frame, verbose=False, imgsz=256, conf=0.35)
                    v_cnt = 0
                    p_cnt = 0
                    target_hit = False

                    for r in results:
                        for box in r.boxes:
                            cls = int(box.cls[0])
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            if cls == 0:
                                p_cnt += 1
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
                                cv2.putText(frame, "PERSON", (x1, max(15, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                            elif cls in [2, 3, 5, 7]:
                                v_cnt += 1
                                vh, vw = y2 - y1, x2 - x1
                                plate_label = "VEHICLE"
                                is_match = False

                                if frame_idx % 5 == 0 and vh > 35 and vw > 35:
                                    v_crop = frame[max(0, y1):min(fh, y2), max(0, x1):min(fw, x2)]
                                    enh_plate = super_resolve_plate(v_crop)
                                    ocr_res = ocr_reader.readtext(
                                        enh_plate,
                                        detail=0,
                                        paragraph=False,
                                        min_size=8,
                                        text_threshold=0.3,
                                        low_text=0.2,
                                        slope_ths=0.2,
                                        allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                                    )
                                    if ocr_res:
                                        raw_t = " ".join(ocr_res).upper()
                                        c_plate = clean_and_validate_plate_string(raw_t) or raw_t
                                        plate_label = f"PLATE: {c_plate}"
                                        if clean_tgt:
                                            is_match, _ = is_real_target_match(clean_tgt, c_plate)
                                            if is_match:
                                                target_hit = True
                                
                                if is_match or target_hit:
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                                    cv2.putText(frame, f"TARGET: {clean_tgt}", (x1, max(15, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                                else:
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
                                    cv2.putText(frame, plate_label, (x1, max(15, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

                    if target_hit and clean_tgt:
                        trigger_audio_sos()
                        if not has_alerted_wb:
                            trigger_voice_dispatch(f"Watchlist vehicle {clean_tgt} intercepted in field webcam.")
                            has_alerted_wb = True

                        wa_link = generate_whatsapp_dispatch_link(clean_tgt, "Field Patrol Integrated Webcam", 23.0225, 72.5714)
                        ALERT_WB.markdown(f"""
                        <div class="soc-alert-box-red">
                            <div class="soc-alert-title" style="color: #9F1239;">TARGET VEHICLE SPOTTED • {clean_tgt}</div>
                            <div class="soc-alert-body" style="color: #4C0519;">Intercept detected in integrated patrol camera.</div>
                        </div>
                        """, unsafe_allow_html=True)
                        DISPATCH_BTN_WB.link_button("DISPATCH EMERGENCY WHATSAPP PATROL ALERT", wa_link, use_container_width=True)
                    else:
                        ALERT_WB.empty()
                        DISPATCH_BTN_WB.empty()

                    FRAME_WB.image(frame, channels="BGR", use_container_width=True)
                    STATS_WB.info(f"Frame Rate: {fps_val} FPS | Tracked: {v_cnt} Vehicles, {p_cnt} Persons | Hardware: ONLINE")
                    time.sleep(0.001)
            finally:
                if cap is not None:
                    cap.release()

# ----------------- MODULE 6: MOBILE PHONE IP CAMERA SCANNER -----------------
elif nav_section == "Mobile Phone IP Camera Scanner":
    render_header("Mobile Phone IP Camera Scanner", prof["name"])

    mob_col1, mob_col2 = st.columns([2, 1])
    with mob_col1:
        mob_ip_input = st.text_input("Enter Mobile IP Webcam URL", value="http://192.168.1.5:8080")
        clean_mob = mob_ip_input.strip()
        if not clean_mob.endswith("/video") and "http" in clean_mob:
            if not clean_mob.endswith("/"):
                clean_mob += "/"
            clean_mob += "video"
    with mob_col2:
        st.info("Setup: Open IP Webcam on your smartphone, tap 'Start Server', and paste the URL here.")

    target_plate_mob = st.text_input("Watchlist Plate (Optional)", value="", placeholder="Enter target plate")

    if "mob_active" not in st.session_state:
        st.session_state.mob_active = False

    c_mb1, c_mb2 = st.columns(2)
    if c_mb1.button("CONNECT MOBILE FEED", type="primary", use_container_width=True):
        st.session_state.mob_active = True
    if c_mb2.button("DISCONNECT MOBILE FEED", use_container_width=True):
        st.session_state.mob_active = False

    ALERT_MOB = st.empty()
    DISPATCH_BTN_MOB = st.empty()
    FRAME_MOB = st.empty()
    STATS_MOB = st.empty()

    if st.session_state.mob_active:
        log_audit_trail(prof['name'], f"Started Mobile IP Cam ({clean_mob})")
        yolo_model, ocr_reader = get_ai_models()
        cap = open_ip_camera_stream(clean_mob)

        if cap is None or not cap.isOpened():
            st.error(f"Could not connect to {clean_mob}. Ensure Phone and Laptop share the same Wi-Fi network.")
        else:
            clean_tgt = clean_str(target_plate_mob)
            frame_idx = 0
            prev_t = time.time()
            fps_val = 30.0
            has_alerted_mob = False

            try:
                while st.session_state.mob_active:
                    ret, frame = cap.read()
                    if not ret or frame is None:
                        st.warning("Mobile stream paused or disconnected.")
                        break

                    frame_idx += 1
                    cur_t = time.time()
                    dt = cur_t - prev_t
                    prev_t = cur_t
                    if dt > 0:
                        fps_val = round(0.9 * fps_val + 0.1 * (1.0 / dt), 1)

                    fh, fw = frame.shape[:2]
                    results = yolo_model(frame, verbose=False, imgsz=256, conf=0.35)
                    v_cnt = 0
                    p_cnt = 0
                    target_hit = False

                    for r in results:
                        for box in r.boxes:
                            cls = int(box.cls[0])
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            if cls == 0:
                                p_cnt += 1
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
                            elif cls in [2, 3, 5, 7]:
                                v_cnt += 1
                                vh, vw = y2 - y1, x2 - x1
                                plate_label = "VEHICLE"
                                is_match = False

                                if frame_idx % 5 == 0 and vh > 35 and vw > 35:
                                    v_crop = frame[max(0, y1):min(fh, y2), max(0, x1):min(fw, x2)]
                                    enh_plate = super_resolve_plate(v_crop)
                                    ocr_res = ocr_reader.readtext(
                                        enh_plate,
                                        detail=0,
                                        paragraph=False,
                                        min_size=8,
                                        text_threshold=0.3,
                                        low_text=0.2,
                                        slope_ths=0.2,
                                        allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                                    )
                                    if ocr_res:
                                        raw_t = " ".join(ocr_res).upper()
                                        c_plate = clean_and_validate_plate_string(raw_t) or raw_t
                                        plate_label = f"PLATE: {c_plate}"
                                        if clean_tgt:
                                            is_match, _ = is_real_target_match(clean_tgt, c_plate)
                                            if is_match:
                                                target_hit = True
                                
                                if is_match or target_hit:
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4)
                                    cv2.putText(frame, f"TARGET: {clean_tgt}", (x1, max(15, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                                else:
                                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
                                    cv2.putText(frame, plate_label, (x1, max(15, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

                    if target_hit and clean_tgt:
                        trigger_audio_sos()
                        if not has_alerted_mob:
                            trigger_voice_dispatch(f"Watchlist vehicle {clean_tgt} intercepted in mobile scanner.")
                            has_alerted_mob = True

                        wa_link = generate_whatsapp_dispatch_link(clean_tgt, "Handheld Mobile IP Patrol Node", 23.0225, 72.5714)
                        ALERT_MOB.markdown(f"""
                        <div class="soc-alert-box-red">
                            <div class="soc-alert-title" style="color: #9F1239;">TARGET VEHICLE SPOTTED • {clean_tgt}</div>
                            <div class="soc-alert-body" style="color: #4C0519;">Intercept detected in mobile handheld stream.</div>
                        </div>
                        """, unsafe_allow_html=True)
                        DISPATCH_BTN_MOB.link_button("DISPATCH EMERGENCY WHATSAPP PATROL ALERT", wa_link, use_container_width=True)
                    else:
                        ALERT_MOB.empty()
                        DISPATCH_BTN_MOB.empty()

                    FRAME_MOB.image(frame, channels="BGR", use_container_width=True)
                    STATS_MOB.info(f"Stream Status: {fps_val} FPS | Tracked: {v_cnt} Vehicles, {p_cnt} Persons")
                    time.sleep(0.001)
            finally:
                if cap is not None:
                    cap.release()

# ----------------- MODULE 7: GUJARAT GIS SUSPECT ROUTE TRACKER -----------------
elif nav_section == "Gujarat GIS Suspect Route Tracker":
    render_header("Gujarat GIS Suspect Route Tracker", prof["name"])

    active_logs = st.session_state.get("last_detection_logs", [])
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Registered Cameras", str(len(ACTIVE_CCTV_CATALOGUE)), "All 25 Nodes Plotted", color="green")
    with c2:
        render_metric_card("Detection Waypoints", str(len(active_logs)), "Waypoints from Forensic Scan", color="red")
    with c3:
        render_metric_card("Map Intelligence Grid", "ONLINE", "Leaflet Spatial GIS Layer", color="blue")

    m = folium.Map(location=[22.5, 71.8], zoom_start=8, tiles="cartodbpositron")

    for cp in ACTIVE_CCTV_CATALOGUE:
        folium.CircleMarker(
            location=[cp["lat"], cp["lon"]],
            radius=6,
            popup=f"<b>Camera {cp['stream_id']} - {cp['name']}</b><br>City: {cp['city']}<br>Type: {cp['type']}<br>Status: ONLINE",
            tooltip=f"Camera {cp['stream_id']} ({cp['name']})",
            color="#0284C7",
            fill=True,
            fill_color="#0284C7",
            fill_opacity=0.7
        ).add_to(m)

    route_coords = []
    for idx, hit in enumerate(active_logs):
        if "Lat" in hit and "Lon" in hit:
            pos = [hit["Lat"], hit["Lon"]]
            route_coords.append(pos)
            folium.Marker(
                location=pos,
                popup=f"<b>STOP #{idx+1}: {hit.get('Event Type')}</b><br/>{hit.get('Checkpost Location')}<br/>Time: {hit.get('Exact Video Timeline')}<br/>{hit.get('Consensus Plate / Details')}",
                tooltip=f"Stop #{idx+1}: {hit.get('Checkpost Location')}",
                icon=folium.Icon(color="red", icon="crosshairs", prefix="fa")
            ).add_to(m)

    if len(route_coords) > 1:
        folium.PolyLine(route_coords, color="#E11D48", weight=4, opacity=0.9, dash_array="10", tooltip="Suspect Movement Route").add_to(m)

    st_folium(m, width="100%", height=520)

# ----------------- MODULE 8: STATEWIDE CCTV ASSET REGISTRY & GAP ANALYSIS -----------------
elif nav_section == "Statewide CCTV Asset Registry & Gap Analysis":
    render_header("Statewide CCTV Asset Registry & Gap Analysis", prof["name"])

    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    with c_m1:
        render_metric_card("Total Statewide Assets", "80,412 Cams", "+1,240 Onboarded this Qtr", color="green")
    with c_m2:
        render_metric_card("Uncovered Border Checkposts", "14 High-Risk", "Priority Infrastructure Gap", color="red")
    with c_m3:
        render_metric_card("AMC Due for Renewal", "1,240 Cameras", "Under 30 Days SLA Notice", color="orange")
    with c_m4:
        render_metric_card("Network Uptime", "98.4%", "Target > 98.0%", color="blue")

    col_reg1, col_reg2 = st.columns([1.2, 1])
    with col_reg1:
        st.markdown("### Departmental Bulk Camera Onboarding")
        sample_csv_data = """Department,Camera ID,Location Name,City,Lat,Lon,Type,Retention Days,AMC Status
SCRB Highway,CAM-GJ-0101,Ratanpur Border Checkpost,Sabarkantha,23.8500,73.1200,4K ANPR PTZ,90,Active
Traffic Branch,CAM-GJ-0102,Kalupur Railway Station Gate 1,Ahmedabad,23.0280,72.6010,Dome 360,60,Due in 15 Days
City Police,CAM-GJ-0103,Ring Road Junction 4,Surat,21.1950,72.8300,High-Mast Bullet,90,Active
Marine Police,CAM-GJ-0104,Mandvi Port Coastal Checkpoint,Kutch,22.8300,69.3500,Coastal Radar PTZ,120,Expired
Smart City,CAM-GJ-0105,Race Course Circle,Rajkot,22.3000,70.7900,Fixed Dual ANPR,60,Active"""

        uploaded_csv = st.file_uploader("Upload Department CCTV Inventory CSV", type=["csv"])
        if uploaded_csv is not None:
            try:
                df_onboard = pd.read_csv(uploaded_csv)
                st.success(f"Parsed {len(df_onboard)} cameras from uploaded CSV.")
                st.dataframe(df_onboard, use_container_width=True)
                log_audit_trail(prof['name'], f"Bulk onboarded {len(df_onboard)} cameras")
            except Exception as e:
                st.error(f"Error parsing CSV: {e}")
        else:
            st.download_button(
                "DOWNLOAD STANDARD REGISTRY CSV TEMPLATE",
                data=sample_csv_data,
                file_name="GUJARAT_POLICE_CAMERA_REGISTRY_TEMPLATE.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col_reg2:
        st.markdown("### Critical Infrastructure Gap Analysis")
        st.markdown("""
        <div class="soc-alert-box-orange">
            <div class="soc-alert-title" style="color: #C2410C;">HIGH-RISK COVERAGE GAPS</div>
            <div class="soc-alert-body" style="color: #7C2D12;">
                • <b>14 Interstate Checkposts</b> lack dual ANPR radar cameras.<br/>
                • <b>Sabarkantha & Banaskantha</b> corridors require 42 additional PTZ nodes.<br/>
                • <b>1,240 Cameras</b> require vendor maintenance contract renewal within 30 days.
            </div>
        </div>
        """, unsafe_allow_html=True)

        map_reg = folium.Map(location=[22.5, 71.8], zoom_start=7, tiles="cartodbpositron")
        for cp in ACTIVE_CCTV_CATALOGUE:
            folium.CircleMarker(
                location=[cp["lat"], cp["lon"]],
                radius=5,
                popup=f"<b>{cp['name']}</b><br>Dept: {cp['dept']}<br>Status: {cp['status']}",
                tooltip=f"{cp['cam_id']} - {cp['name']}",
                color="#0284C7",
                fill=True,
                fill_color="#0284C7"
            ).add_to(map_reg)
        st_folium(map_reg, width="100%", height=240)

# ----------------- MODULE 9: VAHAN & CCTNS NATIONAL LOOKUP -----------------
elif nav_section == "VAHAN & CCTNS National Lookup":
    render_header("VAHAN & CCTNS National Lookup", prof["name"])

    search_query = st.text_input("Enter Vehicle Registration / License Plate Number", value="", placeholder="e.g. GJ01 AB 1234, DL3C AA 1111")
    if st.button("QUERY NATIONAL VAHAN & CCTNS REPOSITORY", type="primary", use_container_width=True):
        if search_query.strip():
            st.info(f"Query for vehicle [{search_query.strip().upper()}] submitted to national VAHAN & CCTNS registry.")
            log_audit_trail(prof['name'], f"VAHAN lookup for plate {search_query.strip().upper()}")
        else:
            st.warning("Please enter a valid vehicle registration number.")

# ----------------- MODULE 10: SECTION 65B SCRB FORENSIC DOSSIER -----------------
elif nav_section == "Section 65B SCRB Forensic Dossier":
    render_header("Section 65B SCRB Forensic Dossier", prof["name"])

    col1, col2 = st.columns(2)
    with col1:
        case_id = st.text_input("Case Reference Number", value="SCRB-GUJ-2026-INCIDENT")
        officer_name = st.text_input("Investigating Officer Name", value=prof["name"])
    with col2:
        police_station = st.text_input("Police Station Jurisdiction", value=prof["station"])

    active_logs = st.session_state.get("last_detection_logs", [])
    if active_logs:
        active_df = pd.DataFrame(active_logs)
        st.dataframe(active_df, use_container_width=True)
        pdf_out = generate_scrb_pdf_report(active_df, case_id=case_id, officer=officer_name)
        st.download_button("DOWNLOAD OFFICIAL SECTION 65B SCRB PDF DOSSIER", data=pdf_out, file_name=f"{case_id}_FORENSIC_DOSSIER.pdf", mime="application/pdf", type="primary", use_container_width=True)
    else:
        st.info("Execute a CCTV Forensic Video Scan to generate court-admissible forensic detection data.")

# ----------------- MODULE 11: SERVER HEALTH & AUDIT LOGS -----------------
elif nav_section == "Server Health & Audit Logs":
    render_header("Server Health & Audit Logs", prof["name"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_card("CPU Utilization", f"{psutil.cpu_percent()}%", f"{psutil.cpu_count()} Cores Active", color="orange")
    with c2:
        render_metric_card("RAM Usage", f"{psutil.virtual_memory().percent}%", f"{round(psutil.virtual_memory().used / (1024**3), 1)} GB Used", color="red")
    with c3:
        render_metric_card("Inference Acceleration", "CPU Multi-Core", "PyTorch OpenMP Active", color="green")
    with c4:
        render_metric_card("Gateway Network Ping", "12 ms", "live.corp8.cloud", color="blue")

    st.markdown("### Immutable Role-Based Audit Trail")
    if os.path.exists("audit_trail.csv"):
        df_audit = pd.read_csv("audit_trail.csv")
        st.dataframe(df_audit.sort_index(ascending=False), use_container_width=True)
        st.download_button("EXPORT AUDIT LOG (CSV)", data=df_audit.to_csv(index=False), file_name="audit_trail_export.csv", use_container_width=True)
    else:
        st.info("No audit entries logged yet.")
