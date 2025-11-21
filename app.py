import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib 
import os 	

# ====================== GLOBAL SESSION STATE INITIALIZATION (UPDATED) ======================

# 1. Assessment Defaults (Used by Assessment page inputs and Recommendations page logic)
# Note: Initializing all required keys globally ensures the app doesn't crash on any page load.
# ===== GLOBAL SESSION STATE INITIALIZATION =====
if 'assessment_usage' not in st.session_state:
    st.session_state.assessment_usage = 4.9
if 'assessment_sleep' not in st.session_state:
    st.session_state.assessment_sleep = 6.9
if 'assessment_mental' not in st.session_state:
    st.session_state.assessment_mental = 6
if 'assessment_stress' not in st.session_state:
    st.session_state.assessment_stress = 6
if 'assessment_risk' not in st.session_state:
    st.session_state.assessment_risk = None
if 'assessment_academic' not in st.session_state:
    st.session_state.assessment_academic = "Undergraduate"
if 'assessment_late_night' not in st.session_state:
    st.session_state.assessment_late_night = False
if 'assessment_fomo' not in st.session_state:
    st.session_state.assessment_fomo = False


# 2. Persona Sliders Defaults (Used by Your Personas page inputs)
if 'persona_usage_slider' not in st.session_state:
    st.session_state.persona_usage_slider = st.session_state.assessment_usage
if 'persona_sleep_slider' not in st.session_state:
    st.session_state.persona_sleep_slider = st.session_state.assessment_sleep
if 'persona_mental_slider' not in st.session_state:
    st.session_state.persona_mental_slider = st.session_state.assessment_mental
    
# 3. What-If Simulator Defaults (NEW)
if 'what_if_usage' not in st.session_state:
    st.session_state.what_if_usage = 4.0
if 'what_if_sleep' not in st.session_state:
    st.session_state.what_if_sleep = 8.0


# ====================== 1. PAGE CONFIG & THEME SETUP ======================
st.set_page_config(
    page_title="Digital Wellness",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - COMBINED (ROBUST FIXES FOR SLIDER AND ALERT BOXES)
st.markdown("""
<style>
    /* Main Background - Restored to original light blue/grey */
    .stApp {
        background-color: #F4F7FE;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #2B3674;
    }
    
    p, li, label, span {
        color: #707EAE;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Gradient Text - Restored (Uses blue/purple gradient which is acceptable) */
    .gradient-text {
        background: linear-gradient(135deg, #868CFF 0%, #4318FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }

    /* KPI Cards (Home Page) */
    .kpi-card {
        background-color: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0px 18px 40px rgba(112, 144, 176, 0.12);
        text-align: center;
        transition: transform 0.2s;
    }
    .kpi-icon { font-size: 2rem; margin-bottom: 10px; }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: #2B3674; }
    .kpi-label { font-size: 0.9rem; color: #A3AED0; }

    /* General Content Box */
    .content-box {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0px 18px 40px rgba(112, 144, 176, 0.12);
        margin-bottom: 20px;
    }

    /* Button Styling */
    .stButton > button {
        background: linear-gradient(90deg, #4481EB 0%, #04BEFE 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }

    /* === GLOBAL COLOR OVERRIDES === */

    /* 1. RADIO BUTTON COLOR FIX (Sidebar/Navigation) */
    div.stRadio > label > div[data-testid="stDecoration"]:has(+ input:checked) {
        border-color: #4318FF !important; 
        background-color: #4318FF !important; 
    }
    .stRadio > label:has(input:checked) span {
        color: #4318FF !important;
        font-weight: 600;
    }

    /* 2. SLIDER COLOR FIX (Track and Thumb) */
    /* Targetting the filled track color */
    div.stSlider [data-baseweb="slider"] > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) {
        background: #4318FF !important; /* Blue for the filled track */
    }
    /* Targetting the thumb/handle color */
    div.stSlider [data-baseweb="slider"] > div:nth-child(1) > div:nth-child(1) > div:nth-child(4) {
        background: #4318FF !important; /* Blue for the thumb */
        border-color: #4318FF !important;
    }
    
    /* 3. ALERT BOX COLOR FIX (st.warning and st.error) */
    /* st.warning background, border, and icon (default yellow/orange) -> Blue */
    div[data-testid="stAlert"] [class*="warning"] {
        background-color: #F0F5FF !important; /* Light blue background */
        border-left-color: #4318FF !important;
    }
    div[data-testid="stAlert"] [class*="warning"] svg {
        fill: #4318FF !important; /* Blue icon */
    }
    /* st.error background, border, and icon (default red) -> Blue */
    div[data-testid="stAlert"] [class*="error"] {
        background-color: #F0F5FF !important; /* Light blue background */
        border-left-color: #4318FF !important;
    }
    div[data-testid="stAlert"] [class*="error"] svg {
        fill: #4318FF !important; /* Blue icon */
    }


    /* --- INSIGHTS STYLES (Blue/Green Palette) --- */
    .metric-box {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        height: 100%;
    }
    .mb-blue, .mb-purple { background-color: #E6F7FF; } 
    .mb-green { background-color: #E6FFFA; } 
    
    .mb-val { font-size: 2.5rem; font-weight: 800; margin: 0; }
    .mb-blue .mb-val, .mb-purple .mb-val { color: #4318FF; } 
    .mb-green .mb-val { color: #05CD99; } 
    
    .mb-label { font-weight: 700; color: #2B3674; margin-top: 5px; margin-bottom: 0;}

    .insight-mini-card {
        background-color: #F9F9F9;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #4318FF;
        margin-bottom: 10px;
    }

    .academic-card {
        padding: 15px;
        border-radius: 12px;
        background: white;
        border: 1px solid #E0E5F2;
        margin-bottom: 15px;
        position: relative;
    }
    .ac-red { border-left: 5px solid #4318FF; } 
    .ac-yellow { border-left: 5px solid #5A7DFF; } 
    .ac-green { border-left: 5px solid #05CD99; } 
    
    .tag {
        float: right; 
        font-size: 0.75rem; 
        padding: 2px 10px; 
        border-radius: 10px;
        font-weight: bold;
    }
    .tag-high { background-color: #E6F7FF; color: #4318FF; } 
    .tag-med { background-color: #F0F5FF; color: #5A7DFF; } 
    .tag-low { background-color: #E6FFFA; color: #05CD99; }

    .model-card {
        text-align: center;
        padding: 20px;
        background: #F9F9F9;
        border-radius: 15px;
    }
    
    /* Custom styles for the feature importance list items */
    .feature-item-box {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E0E5F2;
    }
    .feature-title-text {
        font-weight: 700;
        color: #2B3674;
        font-size: 1.05rem;
    }
    .feature-description {
        font-size: 0.9rem;
        color: #707EAE;
        margin-top: 5px;
    }
    .bg-blue-1 { background-color: #E6F7FF; border-left: 4px solid #4318FF; }
    .bg-blue-2 { background-color: #F0F5FF; border-left: 4px solid #5A7DFF; }
    .bg-green-1 { background-color: #E6FFFA; border-left: 4px solid #05CD99; }

    /* === PERSONA CARD STYLES === */
    .persona-card {
        transition: all 0.3s ease;
        padding: 25px;
        border-radius: 15px;
        background: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        height: 100%;
        border: 3px solid transparent; /* Default border is transparent */
    }
    .active-card {
        transform: scale(1.03);
        border: 3px solid #4318FF !important; /* Highlighted blue border */
        box-shadow: 0 10px 30px rgba(67, 24, 255, 0.2); /* Stronger blue shadow */
    }
</style>
""", unsafe_allow_html=True)


# ====================== 10. MODEL LOADING AND PREDICTION FUNCTION ======================
MODEL_PATH = 'random_forest_social_media_model.joblib'
# Assuming High Risk class label is 1 (Positive/High Risk)
HIGH_RISK_CLASS = 1 

@st.cache_resource
def load_model(path):
    """
    Loads the model container and extracts the RF model object.
    FIX: The model is stored inside a Pandas Series object keyed as 'Model'.
    """
    try:
        if not os.path.exists(path):
             st.error(f"Model file not found at: {path}. Please ensure 'random_forest_social_media_model.joblib' is in the same directory.")
             return None
        
        loaded_object = joblib.load(path)
        
        # FIX: Check if the model is nested inside a Pandas Series with key 'Model'
        if isinstance(loaded_object, pd.Series) and 'Model' in loaded_object:
            model = loaded_object['Model']
            if hasattr(model, 'predict_proba'):
                return model
        
        # Fallback 1: Check if the model is nested inside a dictionary with key 'model' 
        elif isinstance(loaded_object, dict) and 'model' in loaded_object:
            model = loaded_object['model']
            if hasattr(model, 'predict_proba'):
                return model

        # Fallback 2: Check if the model object was saved directly
        elif hasattr(loaded_object, 'predict_proba'):
            return loaded_object
        
        else:
            st.error("Loaded object is not a recognizable model format (missing 'Model' key in Series, 'model' key in dict, or 'predict_proba' method).")
            return None
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model(MODEL_PATH)

def predict_risk_score(usage, sleep, mental, stress, academic, late_night, fomo):
    """
    Predicts a 1-10 risk score using the Random Forest model's probability.
    
    Features assumed (7 total, based on notebook top 5 and available inputs):
    1. avg_daily_usage_hours (float) -> usage
    2. mental_health_score (int) -> mental
    3. sleep_hours_per_night (float) -> sleep
    4. conflicts_over_social_media (float, normalized stress) -> stress (1-10) -> (1-5)
    5. affects_academic_performance_Yes (binary) -> 1 if High School or Undergraduate
    6. late_night_use_Yes (binary) -> from late_night checkbox
    7. FOMO_anxiety_Yes (binary) -> from fomo checkbox
    """
    if model is None:
        # Fallback to the original heuristic if the model failed to load or extract
        return int((usage * 1.8 + (12-sleep)*1.2 + (10-mental)*0.8 + stress*0.7) / 4.5)
    
    # Feature Engineering based on notebook insights
    # 4. conflicts_over_social_media: Rescale user's 1-10 stress to a 1-5 conflicts scale
    conflicts_over_social_media = stress / 2.0
    
    # 5. affects_academic_performance_Yes: Categorical mapping (High School/Undergrad are high risk)
    affects_academic_performance_Yes = 1 if academic in ["High School", "Undergraduate"] else 0
    
    # 6. late_night_use_Yes
    late_night_use_Yes = 1 if late_night else 0
    
    # 7. FOMO_anxiety_Yes
    fomo_anxiety_Yes = 1 if fomo else 0
    
    # Create the feature DataFrame - COLUMN ORDER IS CRITICAL
    feature_data = {
        'avg_daily_usage_hours': [usage],
        'mental_health_score': [mental],
        'sleep_hours_per_night': [sleep],
        'conflicts_over_social_media': [conflicts_over_social_media],
        'affects_academic_performance_Yes': [affects_academic_performance_Yes],
        'late_night_use_Yes': [late_night_use_Yes], 
        'FOMO_anxiety_Yes': [fomo_anxiety_Yes],     
    }
    
    feature_df = pd.DataFrame(feature_data)

    try:
        # Get probability of the High Risk class (class 1)
        proba = model.predict_proba(feature_df)[:, HIGH_RISK_CLASS][0]
        
        # Scale probability (0.0 to 1.0) to a 1-10 risk score, rounding up
        risk_score = int(np.ceil(proba * 10))
        risk_score = min(max(risk_score, 1), 10) # Ensure it's between 1 and 10
        return risk_score
    except Exception as e:
        # Fallback to the original heuristic if prediction fails (e.g., mismatched columns)
        return int((usage * 1.8 + (12-sleep)*1.2 + (10-mental)*0.8 + stress*0.7) / 4.5)


# ====================== 2. SIDEBAR NAVIGATION ======================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
        <div style="font-size: 2rem;">🧠</div>
        <div>
            <h2 style="margin:0; font-size: 1.4rem; color: #4318FF;">Digital Wellness</h2>
            <p style="margin:0; font-size: 0.8rem; color: #A3AED0;">Research-Based Tool</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Page order swapped: Insights is now before Assessment
    page = st.radio("Navigate", [
        "Home",
        "Insights",
        "Assessment",
        "Your Personas",
        "What-If Simulator",
        "Recommendations",
        "Peer Comparison"
    ])
    
    st.markdown("---")


#add logo at top of page#
from PIL import Image

# Load the logo
logo = Image.open("logo.jpeg")

# Enhanced CSS for homepage animations and interactivity
st.markdown("""
<style>
    /* Fade-in animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Pulse animation for badges */
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    /* Animated gradient background */
    .hero-section {
        animation: fadeInUp 0.8s ease-out;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    }
    
    .hero-badge {
        display: inline-block;
        background-color: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        color: white;
        padding: 8px 20px;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
        animation: pulse 2s infinite;
    }
    
    .hero-title {
        color: white;
        font-size: 3.5rem;
        font-weight: 800;
        margin: 1rem 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.2rem;
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Enhanced KPI cards with hover effects */
    .kpi-card {
        background: white;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0px 10px 30px rgba(112, 144, 176, 0.15);
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
        animation: fadeInUp 0.6s ease-out;
        animation-fill-mode: both;
    }
    
    .kpi-card:nth-child(1) { animation-delay: 0.1s; }
    .kpi-card:nth-child(2) { animation-delay: 0.2s; }
    .kpi-card:nth-child(3) { animation-delay: 0.3s; }
    .kpi-card:nth-child(4) { animation-delay: 0.4s; }
    
    .kpi-card:hover {
        transform: translateY(-10px);
        box-shadow: 0px 20px 50px rgba(67, 24, 255, 0.25);
    }
    
    .kpi-icon { 
        font-size: 2.5rem; 
        margin-bottom: 15px;
        transition: transform 0.3s ease;
    }
    
    .kpi-card:hover .kpi-icon {
        transform: scale(1.2) rotate(5deg);
    }
    
    .kpi-value { 
        font-size: 2.2rem; 
        font-weight: 800; 
        color: #2B3674;
        margin: 10px 0;
    }
    
    .kpi-label { 
        font-size: 0.95rem; 
        color: #A3AED0;
        font-weight: 600;
    }
    
    /* Enhanced feature cards */
    .feature-card {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0px 10px 30px rgba(112, 144, 176, 0.12);
        transition: all 0.4s ease;
        height: 100%;
        border: 2px solid transparent;
        animation: fadeInUp 0.8s ease-out;
        animation-fill-mode: both;
    }
    
    .feature-card:nth-child(1) { animation-delay: 0.2s; }
    .feature-card:nth-child(2) { animation-delay: 0.3s; }
    .feature-card:nth-child(3) { animation-delay: 0.4s; }
    
    .feature-card:hover {
        transform: translateY(-8px);
        border-color: #4318FF;
        box-shadow: 0px 25px 50px rgba(67, 24, 255, 0.2);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover .feature-icon {
        transform: scale(1.15) rotate(-5deg);
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #2B3674;
        margin-bottom: 15px;
    }
    
    .feature-card p {
        color: #707EAE;
        line-height: 1.7;
        margin-bottom: 15px;
    }
    
    .feature-card ul {
        list-style: none;
        padding-left: 0;
    }
    
    .feature-card ul li {
        padding: 8px 0;
        color: #707EAE;
        position: relative;
        padding-left: 25px;
    }
    
    .feature-card ul li:before {
        content: "✓";
        position: absolute;
        left: 0;
        color: #4318FF;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    /* CTA Button styling */
    .cta-container {
        text-align: center;
        margin: 2rem 0;
        animation: fadeInUp 1s ease-out;
    }
    
    .cta-text {
        font-size: 1rem;
        color: #707EAE;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    .cta-highlight {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 40px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .cta-highlight:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
    }
    
    /* Stats bar */
    .stats-bar {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
        animation: fadeInUp 0.9s ease-out;
    }
    
    .stat-inline {
        display: inline-block;
        margin: 0 20px;
        padding: 10px 20px;
    }
    
    .stat-number {
        font-size: 1.8rem;
        font-weight: 800;
        color: #4318FF;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #707EAE;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-bottom: 1rem;">
    <!-- Logo -->
</div>
""", unsafe_allow_html=True)

# Centered logo
col1, col2, col3 = st.columns([2.3,2,1])
with col2:
    st.image(logo, width=100)

## ====================== 3. PAGE: HOME ======================
if page == "Home":
    # Hero Section with gradient background
    st.markdown("""
    <div class="hero-section" style="text-align: center;">
        <div class="hero-badge">🎓 Research-Based Digital Wellness Tool</div>
        <h1 class="hero-title">Social Media Addiction<br>Risk Dashboard</h1>
        <p class="hero-subtitle">Evidence-based assessment tool built on comprehensive analysis of 705 students. Understand your digital habits and get personalized wellness recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

    # Call-to-Action
    st.markdown("""
    <div class="cta-container">
        <p class="cta-text">Ready to discover your digital wellness profile?</p>
        <div class="cta-highlight">👉 Navigate to <strong>Assessment</strong> in the sidebar to begin</div>
    </div>
    """, unsafe_allow_html=True)

    st.write("") 

    # Quick Stats Bar
    st.markdown("""
    <div class="stats-bar">
        <div class="stat-inline">
            <div class="stat-number">705</div>
            <div class="stat-label">Students Studied</div>
        </div>
        <div class="stat-inline">
            <div class="stat-number">92%</div>
            <div class="stat-label">Model Accuracy</div>
        </div>
        <div class="stat-inline">
            <div class="stat-number">7</div>
            <div class="stat-label">Key Predictors</div>
        </div>
        <div class="stat-inline">
            <div class="stat-number">8</div>
            <div class="stat-label">Platforms Analyzed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    
    # KPI Cards Row (animated)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon" style="color: #4318FF;">👥</div>
            <div class="kpi-value">705</div>
            <div class="kpi-label">Students Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon" style="color: #667eea;">⚡</div>
            <div class="kpi-value">92.0%</div>
            <div class="kpi-label">Model Accuracy</div>
        </div>
        """, unsafe_allow_html=True) 

    with col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon" style="color: #00D2AA;">🕒</div>
            <div class="kpi-value">4.9hrs</div>
            <div class="kpi-label">Avg Daily Usage</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-icon" style="color: #4318FF;">🧠</div>
            <div class="kpi-value">8</div>
            <div class="kpi-label">Key Platforms</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    
    # Features Section with enhanced design
    st.markdown("<h3 style='text-align: center; margin-bottom: 40px; font-size: 2rem; color: #2B3674;'>What This Dashboard Offers</h3>", unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns(3)
    
    with f1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon" style="color: #4318FF;">🛡️</div>
            <div class="feature-title">Risk Assessment</div>
            <p>Personalized evaluation based on your usage patterns, sleep, stress, and mental health metrics.</p>
            <ul>
                <li>Real-time risk calculation</li>
                <li>Evidence-based scoring</li>
                <li>ML-powered predictions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon" style="color: #667eea;">📈</div>
            <div class="feature-title">Platform Analytics</div>
            <p>Detailed breakdown of addiction patterns across different social media platforms.</p>
            <ul>
                <li>Platform addiction rankings</li>
                <li>Usage pattern analysis</li>
                <li>Demographic insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon" style="color: #00D2AA;">📊</div>
            <div class="feature-title">Research Insights</div>
            <p>Access to comprehensive findings from our machine learning analysis.</p>
            <ul>
                <li>Statistical correlations</li>
                <li>Behavioral patterns</li>
                <li>Actionable recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    st.write("")
    
    # Additional interactive section - "How it Works"
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 40px; border-radius: 20px; margin-top: 3rem;">
        <h3 style="text-align: center; color: #2B3674; margin-bottom: 30px;">How It Works</h3>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap;">
            <div style="text-align: center; flex: 1; min-width: 200px; padding: 20px;">
                <div style="font-size: 3rem; margin-bottom: 10px;">1️⃣</div>
                <div style="font-weight: 700; color: #2B3674; margin-bottom: 10px;">Take Assessment</div>
                <div style="color: #707EAE; font-size: 0.9rem;">Answer questions about your digital habits</div>
            </div>
            <div style="text-align: center; flex: 1; min-width: 200px; padding: 20px;">
                <div style="font-size: 3rem; margin-bottom: 10px;">2️⃣</div>
                <div style="font-weight: 700; color: #2B3674; margin-bottom: 10px;">Get Your Score</div>
                <div style="color: #707EAE; font-size: 0.9rem;">Receive ML-powered risk analysis</div>
            </div>
            <div style="text-align: center; flex: 1; min-width: 200px; padding: 20px;">
                <div style="font-size: 3rem; margin-bottom: 10px;">3️⃣</div>
                <div style="font-weight: 700; color: #2B3674; margin-bottom: 10px;">Discover Persona</div>
                <div style="color: #707EAE; font-size: 0.9rem;">Find your digital wellness persona</div>
            </div>
            <div style="text-align: center; flex: 1; min-width: 200px; padding: 20px;">
                <div style="font-size: 3rem; margin-bottom: 10px;">4️⃣</div>
                <div style="font-weight: 700; color: #2B3674; margin-bottom: 10px;">Take Action</div>
                <div style="color: #707EAE; font-size: 0.9rem;">Get personalized recommendations</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)



# ====================== 4. PAGE: INSIGHTS (ENHANCED WITH ANIMATIONS & INTERACTIVITY) ======================
elif page == "Insights":
    # Enhanced CSS for Insights page
    st.markdown("""
    <style>
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            padding: 0 30px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(67, 24, 255, 0.2);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        /* Insight cards with hover effects */
        .insight-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            margin-bottom: 20px;
            border-left: 4px solid #4318FF;
        }
        
        .insight-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(67, 24, 255, 0.15);
        }
        
        /* Enhanced metric boxes */
        .metric-box {
            padding: 25px;
            border-radius: 20px;
            text-align: center;
            height: 100%;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .metric-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }
        
        .metric-box:hover::before {
            left: 100%;
        }
        
        .metric-box:hover {
            transform: scale(1.05);
        }
        
        .mb-blue, .mb-purple { 
            background: linear-gradient(135deg, #E6F7FF 0%, #F0F5FF 100%);
        } 
        .mb-green { 
            background: linear-gradient(135deg, #E6FFFA 0%, #F0FFF4 100%);
        }
        
        .mb-val { 
            font-size: 3rem; 
            font-weight: 900; 
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .mb-green .mb-val { 
            background: linear-gradient(135deg, #05CD99 0%, #00B386 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .mb-label { 
            font-weight: 700; 
            color: #2B3674; 
            margin-top: 10px; 
            margin-bottom: 5px;
            font-size: 1.1rem;
        }
        
        .mb-desc {
            font-size: 0.85rem;
            color: #707EAE;
            margin-top: 5px;
        }
        
        /* Enhanced insight mini cards */
        .insight-mini-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #4318FF;
            margin-bottom: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .insight-mini-card:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 20px rgba(67, 24, 255, 0.15);
        }
        
        /* Enhanced academic cards */
        .academic-card {
            padding: 20px;
            border-radius: 15px;
            background: white;
            border: 2px solid #E0E5F2;
            margin-bottom: 15px;
            position: relative;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .academic-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }
        
        .ac-red { 
            border-left: 6px solid #4318FF;
            background: linear-gradient(135deg, #fff 0%, #f0f5ff 100%);
        } 
        .ac-yellow { 
            border-left: 6px solid #5A7DFF;
            background: linear-gradient(135deg, #fff 0%, #f5f7ff 100%);
        } 
        .ac-green { 
            border-left: 6px solid #05CD99;
            background: linear-gradient(135deg, #fff 0%, #f0fff4 100%);
        }
        
        .tag {
            float: right; 
            font-size: 0.75rem; 
            padding: 5px 15px; 
            border-radius: 20px;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .tag-high { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .tag-med { background: linear-gradient(135deg, #5A7DFF 0%, #667eea 100%); color: white; }
        .tag-low { background: linear-gradient(135deg, #05CD99 0%, #00B386 100%); color: white; }
        
        /* Enhanced model cards */
        .model-card {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border-radius: 20px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border: 2px solid transparent;
        }
        
        .model-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 40px rgba(67, 24, 255, 0.2);
            border-color: #4318FF;
        }
        
        /* Feature importance boxes */
        .feature-item-box {
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 15px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
            border: 2px solid #E0E5F2;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .feature-item-box::after {
            content: '';
            position: absolute;
            top: 0;
            right: -50px;
            width: 50px;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5));
            transform: skewX(-20deg);
            transition: right 0.5s;
        }
        
        .feature-item-box:hover::after {
            right: 150%;
        }
        
        .feature-item-box:hover {
            transform: translateX(5px);
            box-shadow: 0 8px 25px rgba(67, 24, 255, 0.15);
        }
        
        .feature-title-text {
            font-weight: 800;
            color: #2B3674;
            font-size: 1.15rem;
            margin-bottom: 10px;
        }
        
        .feature-description {
            font-size: 0.95rem;
            color: #707EAE;
            margin-top: 8px;
            line-height: 1.6;
        }
        
        .bg-blue-1 { 
            background: linear-gradient(135deg, #E6F7FF 0%, #F0F5FF 100%); 
            border-left: 5px solid #4318FF; 
        }
        .bg-blue-2 { 
            background: linear-gradient(135deg, #F0F5FF 0%, #F5F7FF 100%); 
            border-left: 5px solid #5A7DFF; 
        }
        .bg-green-1 { 
            background: linear-gradient(135deg, #E6FFFA 0%, #F0FFF4 100%); 
            border-left: 5px solid #05CD99; 
        }
        
        /* Key findings box */
        .key-findings {
            background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%);
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            border-left: 5px solid #4318FF;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        
        .key-findings ul li {
            margin-bottom: 10px;
            padding-left: 25px;
            position: relative;
        }
        
        .key-findings ul li::before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #4318FF;
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        /* Section headers */
        .section-header {
            font-size: 1.8rem;
            font-weight: 800;
            color: #2B3674;
            margin-bottom: 15px;
            position: relative;
            padding-bottom: 10px;
        }
        
        .section-header::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 60px;
            height: 4px;
            background: linear-gradient(90deg, #4318FF 0%, #667eea 100%);
            border-radius: 2px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with enhanced styling
    st.markdown("""
    <div style='text-align:center; margin-bottom: 2rem;'>
        <h1 class='gradient-text' style='font-size: 2.5rem; margin-bottom: 10px;'>Research Insights & Analytics</h1>
        <p style='font-size: 1.1rem; color: #707EAE;'>Key findings from comprehensive analysis of 705 students</p>
        <div style='display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px 20px; border-radius: 20px; font-size: 0.9rem; margin-top: 10px;'>
            📊 Based on ML-Powered Analysis
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # TABS CONFIGURATION
    tab1, tab2, tab3, tab4 = st.tabs(["📱 Platforms", "👥 Demographics", "⏰ Patterns", "🎯 Correlations"])

    # ---------------- TAB 1: PLATFORMS (Enhanced) ----------------
    with tab1:
        st.markdown('<div class="content-box" style="border-top: 4px solid #4318FF;">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header" style="color: #707EAE;">📊 Platform Addiction Rankings</h3>', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1rem; margin-bottom: 25px; color: #707EAE;'>Average addiction scores (1-10) by primary social media platform</p>", unsafe_allow_html=True)
        
        # CORRECTED DATA: All 8 platforms sorted descending by addiction score
        platforms_full = ["WhatsApp", "Snapchat", "TikTok", "Instagram", "YouTube", "Facebook", "Twitter/X", "LinkedIn"]
        scores_full = [7.46, 7.46, 7.43, 6.55, 6.1, 5.67, 5.5, 3.81]
        
        # Enhanced colors with gradient effect
        colors = ['#4318FF', '#5A7DFF', '#667eea', '#7C93F5', '#05CD99', '#3CD4A0', '#66D9A6', '#B8F1D0']

        fig = go.Figure(go.Bar(
            x=scores_full,
            y=platforms_full,
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(color='rgba(255,255,255,0.3)', width=2)
            ),
            text=[f"<b>{s}/10</b>" for s in scores_full],
            textposition='auto',
            textfont=dict(color='white', size=15, family='Arial Black'),
            hovertemplate='<b>%{y}</b><br>Score: %{x}/10<extra></extra>'
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=500,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(
                showgrid=True, 
                gridcolor='rgba(200,200,200,0.2)',
                visible=True, 
                range=[0, 10],
                title=dict(text="Addiction Score", font=dict(size=14, color='#707EAE'))
            ),
            yaxis=dict(
                showgrid=False, 
                tickfont=dict(size=15, color='#2B3674', family="Segoe UI, sans-serif", weight='bold')
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Segoe UI"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
            <div class="key-findings">
                <b style="color: #2B3674; font-size: 1.15rem;">🔍 Key Findings:</b>
                <ul style="margin-top: 15px; margin-bottom: 0; font-size: 0.95rem; color: #707EAE;">
                    <li><b>WhatsApp and Snapchat</b> show the highest average addiction scores (over 7.4/10), indicating severe dependency risk among messaging app users.</li>
                    <li><b>Instant messaging platforms</b> encourage prolonged screen use due to high social pressure and FOMO (Fear of Missing Out).</li>
                    <li><b>LinkedIn is the least addictive</b> platform (3.81/10), likely due to its professional focus and lower social pressure dynamics.</li>
                    <li><b>Short-form video apps</b> (TikTok) rank high at 7.43/10, driven by infinite scroll and algorithm-driven content.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- TAB 2: DEMOGRAPHICS (Enhanced) ----------------
    with tab2:
        col_l, col_r = st.columns([3, 2])
        
        with col_l:
            st.markdown('<div class="content-box" style="border-top: 4px solid #667eea;">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header" style="color: #707EAE;">👥 Age Distribution</h3>', unsafe_allow_html=True)
            st.markdown("<p style='font-size:0.95rem; color: #707EAE;'>Count of students with High Addiction Scores (≥4) by age group</p>", unsafe_allow_html=True)
            
            ages_labels = ["Age 18", "Age 19", "Age 20", "Age 21", "Age 22", "Age 23", "Age 24"]
            counts = [13, 126, 132, 120, 119, 23, 15] 
            
            # Enhanced colors with gradient
            fig_age = go.Figure(go.Bar(
                x=counts,
                y=ages_labels,
                orientation='h',
                marker=dict(
                    color=['#9299F5', '#7D85EC', '#667eea', '#5A7DFF', '#7D85EC', '#9299F5', '#A3AED0'],
                    line=dict(color='white', width=2)
                ),
                text=counts,
                textposition='auto',  # Changed from 'outside' to 'auto' - will position inside if space, outside if not
                textfont=dict(size=14, color='#2B3674', family='Arial', weight='bold'),  # Increased size and ensured visibility
                width=0.6,
                hovertemplate='<b>%{y}</b><br>Count: %{x} students<extra></extra>'
            ))

            fig_age.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                margin=dict(l=0, r=80, t=0, b=0),  # Increased right margin to accommodate outside text
                xaxis=dict(
                    showgrid=True, 
                    gridcolor='rgba(200,200,200,0.2)', 
                    visible=True,
                    range=[0, max(counts) * 1.15]  # Extended range to ensure text fits
                ),
                yaxis=dict(showgrid=False, tickfont=dict(size=14, weight='bold')),
                hoverlabel=dict(bgcolor="white", font_size=13)
            )
            st.plotly_chart(fig_age, use_container_width=True)
            
            st.markdown("""
            <div style="background: linear-gradient(135deg, #E6FFFA 0%, #F0FFF4 100%); padding: 20px; border-radius: 12px; border-left: 5px solid #05CD99; box-shadow: 0 5px 15px rgba(0,0,0,0.05);">
                <strong style="color:#05CD99; font-size: 1.15rem;">📊 Peak Risk Age: 20 years old</strong><br>
                <span style="font-size:0.95rem; color: #2B3674; margin-top: 10px; display: block;">Ages 19-22 show the highest concentration of addicted users, representing the critical university years.</span>
            </div>
            </div>
            """, unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="content-box" style="border-top: 4px solid #05CD99;">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-header">🎓 Academic Level Analysis</h3>', unsafe_allow_html=True)
            st.markdown("<p style='font-size:0.95rem; color: #707EAE;'>Risk assessment by education level (ANOVA P-Value: 0.00000)</p>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class="academic-card ac-red">
                <span class="tag tag-high">High Risk</span>
                <b style="font-size: 1.1rem; color: #2B3674;">High School</b>
                <div style="font-size:0.9rem; color:#707EAE; margin-top:10px;">
                    <span style="font-weight: 600;">Avg: <span style="color: #4318FF;">7.5</span></span>
                    <span style="float:right; font-weight: 600;">Median: <span style="color: #4318FF;">8</span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="academic-card ac-yellow">
                <span class="tag tag-med">Moderate Risk</span>
                <b style="font-size: 1.1rem; color: #2B3674;">Undergraduate</b>
                <div style="font-size:0.9rem; color:#707EAE; margin-top:10px;">
                    <span style="font-weight: 600;">Avg: <span style="color: #5A7DFF;">6.9</span></span>
                    <span style="float:right; font-weight: 600;">Median: <span style="color: #5A7DFF;">7</span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="academic-card ac-green">
                <span class="tag tag-low">Low Risk</span>
                <b style="font-size: 1.1rem; color: #2B3674;">Graduate</b>
                <div style="font-size:0.9rem; color:#707EAE; margin-top:10px;">
                    <span style="font-weight: 600;">Avg: <span style="color: #05CD99;">6.2</span></span>
                    <span style="float:right; font-weight: 600;">Median: <span style="color: #05CD99;">6</span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="academic-card ac-green">
                <span class="tag tag-low">Low Risk</span>
                <b style="font-size: 1.1rem; color: #2B3674;">PhD/Doctoral</b>
                <div style="font-size:0.9rem; color:#707EAE; margin-top:10px;">
                    <span style="font-weight: 600;">Avg: <span style="color: #05CD99;">5.8</span></span>
                    <span style="float:right; font-weight: 600;">Median: <span style="color: #05CD99;">6</span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background: linear-gradient(135deg, #F0F5FF 0%, #E6F7FF 100%); padding: 15px; border-radius: 10px; font-size: 0.9rem; color: #2B3674; border-left: 5px solid #4318FF; box-shadow: 0 5px 15px rgba(0,0,0,0.05);">
                <b style="font-size: 1rem;">💡 Critical Finding:</b><br>
                <span style="margin-top: 8px; display: block;">High school students show the highest addiction tendency with the least score variation, indicating systemic vulnerability.</span>
            </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------- TAB 3: PATTERNS (Enhanced) ----------------
    with tab3:
        st.markdown('<div class="content-box" style="border-top: 4px solid #05CD99;">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header" style="color: #707EAE;">🕑 Usage Patterns & Lifestyle Metrics</h3>', unsafe_allow_html=True)
        st.markdown("<p style='margin-bottom:30px; font-size: 1rem; color: #707EAE;'>Average student behavioral profile from the dataset</p>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("""
            <div class="metric-box mb-blue">
                <p class="mb-val">4.9</p>
                <p class="mb-label">Hours Daily Usage</p>
                <p class="mb-desc">Standard deviation: ±1.26 hrs</p>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown("""
            <div class="metric-box mb-purple">
                <p class="mb-val">6.9</p>
                <p class="mb-label">Hours Sleep/Night</p>
                <p class="mb-desc">Below recommended 7-9 hours</p>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown("""
            <div class="metric-box mb-green">
                <p class="mb-val">6.4<span style="font-size: 1.5rem;">/10</span></p>
                <p class="mb-label">Avg Addiction Score</p>
                <p class="mb-desc">Median score is 7/10</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br><h4 style='color:#2B3674; font-size: 1.3rem; margin-top: 30px; margin-bottom: 20px;'>🔍 Behavioral Insights:</h4>", unsafe_allow_html=True)
        
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("""
            <div class="insight-mini-card" style="border-left: 5px solid #05CD99;">
                <b style='color:#2B3674; font-size: 1.05rem;'>😴 Sleep Deficit Risk</b><br>
                <span style="font-size:0.9rem; color:#707EAE; margin-top: 8px; display: block;">25% of students report sleeping 6 hours or less per night, creating a vicious cycle of fatigue and increased screen time.</span>
            </div>
            <div class="insight-mini-card" style="border-left: 5px solid #667eea;">
                <b style='color:#2B3674; font-size: 1.05rem;'>⚡ Conflicts & Toxicity</b><br>
                <span style="font-size:0.9rem; color:#707EAE; margin-top: 8px; display: block;">Average conflict score is 2.85/5, indicating moderate social media-induced stress and interpersonal friction.</span>
            </div>
            """, unsafe_allow_html=True)
        with g2:
            st.markdown("""
            <div class="insight-mini-card" style="border-left: 5px solid #4318FF;">
                <b style='color:#2B3674; font-size: 1.05rem;'>🧠 Stress-Addiction Link</b><br>
                <span style="font-size:0.9rem; color:#707EAE; margin-top: 8px; display: block;">High stress is a key predictor, correlating with compensatory usage patterns as a coping mechanism.</span>
            </div>
            <div class="insight-mini-card" style="border-left: 5px solid #9299F5;">
                <b style='color:#2B3674; font-size: 1.05rem;'>📊 Demographic Nuance</b><br>
                <span style="font-size:0.9rem; color:#707EAE; margin-top: 8px; display: block;">Gender and Relationship Status have zero statistical effect on addiction intensity (ANOVA P > 0.05), indicating universal susceptibility.</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- TAB 4: CORRELATIONS (Enhanced) ----------------
    with tab4:
        st.markdown('<div class="content-box" style="border-top: 4px solid #4318FF;">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-header" style="color: #707EAE;">📈 Model Performance & Feature Importance</h3>', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1rem; color: #707EAE; margin-bottom: 30px;'>Key model results and predictor relationships from final analysis.</p>", unsafe_allow_html=True)
        
        
        st.markdown("<h4 style='color: #2B3674; font-size: 1.4rem; margin-bottom: 20px;'>🎯 Key Predictors of Addiction Risk (Random Forest Top 3)</h4>", unsafe_allow_html=True)
        
        # Enhanced feature importance boxes
        st.markdown("""
        <div style="margin-bottom: 30px;">
            <div class="feature-item-box bg-blue-1">
                <span class="feature-title-text">🥇 1. Avg Daily Usage Hours (~35.4%)</span>
                <div class="feature-description">
                    The single most important predictor. High usage is the primary driver of dependency and is strongly correlated with other negative behavioral factors including sleep deficit and mental health decline.
                </div>
            </div>
            <div class="feature-item-box bg-blue-2">
                <span class="feature-title-text">🥈 2. Mental Health Score (~28.3%)</span>
                <div class="feature-description">
                    Low scores are a highly significant factor, often leading to compensatory social media usage to cope with stress, anxiety, or depression—creating a reinforcing cycle.
                </div>
            </div>
            <div class="feature-item-box bg-green-1">
                <span class="feature-title-text">🥉 3. Sleep Hours/Night (~24.8%)</span>
                <div class="feature-description">
                    Low sleep quality is a major indicator, showing that social media usage frequently infringes on rest time. Late-night scrolling disrupts circadian rhythms and productivity.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        
        st.markdown("<h4 style='color: #2B3674; font-size: 1.4rem; margin-bottom: 20px;'>📊 Visual Feature Importance Ranking</h4>", unsafe_allow_html=True)
        
        try:
            st.image("feature_importance.png", caption="Visual Ranking of Predictors by Random Forest Model", use_container_width=True) 
        except FileNotFoundError:
            st.info("💡 To complete this section, please create and save your model's Feature Importance plot as **'feature_importance.png'** in the app directory.")

        st.write("")
        st.markdown("<h4 style='color: #2B3674; font-size: 1.4rem; margin-bottom: 20px; margin-top: 30px;'>🏆 Model Performance Summary</h4>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("""
            <div class="model-card">
                <div style="font-size:2.5rem; font-weight:900; background: linear-gradient(135deg, #4318FF 0%, #667eea 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">100%</div>
                <div style="font-weight:bold; font-size: 1.1rem; color: #2B3674; margin-top: 10px;">Logistic Regression</div>
                <div style="font-size:0.85rem; color: #707EAE; margin-top: 5px;">Tuned / Test Accuracy</div>
                <div style="margin-top: 15px; padding: 8px; background: #F0F5FF; border-radius: 8px; font-size: 0.8rem; color: #4318FF;">
                    <b>Best for:</b> Interpretability
                </div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown("""
            <div class="model-card" style="border: 3px solid #667eea; background: linear-gradient(135deg, #ffffff 0%, #f0f5ff 100%);">
                <div style="font-size:2.5rem; font-weight:900; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">92.0%</div>
                <div style="font-weight:bold; font-size: 1.1rem; color: #2B3674; margin-top: 10px;">Random Forest ⭐</div>
                <div style="font-size:0.85rem; color: #707EAE; margin-top: 5px;">Tuned / Test Accuracy</div>
                <div style="margin-top: 15px; padding: 8px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px; font-size: 0.8rem; color: white; font-weight: bold;">
                    ✓ SELECTED MODEL
                </div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown("""
            <div class="model-card">
                <div style="font-size:2.5rem; font-weight:900; background: linear-gradient(135deg, #05CD99 0%, #00B386 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">98.5%</div>
                <div style="font-weight:bold; font-size: 1.1rem; color: #2B3674; margin-top: 10px;">Gradient Boosting</div>
                <div style="font-size:0.85rem; color: #707EAE; margin-top: 5px;">Tuned / Test Accuracy</div>
                <div style="margin-top: 15px; padding: 8px; background: #E6FFFA; border-radius: 8px; font-size: 0.8rem; color: #05CD99;">
                    <b>Risk:</b> Overfitting
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Enhanced final model selection rationale
        st.markdown("""
        <div style="background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%); padding: 25px; border-radius: 15px; margin-top: 30px; border-left: 5px solid #667eea; box-shadow: 0 8px 25px rgba(0,0,0,0.08);">
            <h4 style='color:#2B3674; font-size: 1.3rem; margin-bottom: 15px;'>🎯 Final Model Selection: Random Forest (92.0% Accuracy)</h4>
            <div style="background: white; padding: 20px; border-radius: 10px; margin-top: 15px;">
                <p style="color: #2B3674; font-size: 1rem; margin-bottom: 15px; line-height: 1.7;">
                    The <b>Random Forest model</b> was selected for deployment based on its optimal balance of accuracy, generalizability, and robustness. Here's why:
                </p>
                <ul style="font-size: 0.95rem; color: #707EAE; margin-bottom:0; line-height: 1.8;">
                    <li><b>High Generalizable Accuracy:</b> 92.00% test accuracy demonstrates strong predictive power without overfitting (vs. Gradient Boosting's 98.5% which showed signs of overfitting on validation data).</li>
                    <li><b>Top 5 Critical Features:</b> <code style="background: #F0F5FF; padding: 2px 6px; border-radius: 4px; color: #4318FF;">avg_daily_usage_hours</code>, <code style="background: #F0F5FF; padding: 2px 6px; border-radius: 4px; color: #4318FF;">mental_health_score</code>, <code style="background: #F0F5FF; padding: 2px 6px; border-radius: 4px; color: #4318FF;">sleep_hours_per_night</code>, <code style="background: #F0F5FF; padding: 2px 6px; border-radius: 4px; color: #4318FF;">conflicts_over_social_media</code>, and <code style="background: #F0F5FF; padding: 2px 6px; border-radius: 4px; color: #4318FF;">affects_academic_performance_Yes</code>.</li>
                    <li><b>Multicollinearity Resolved:</b> VIF analysis eliminated feature redundancy, reducing VIF from 10.6 to 3.4 for cleaner predictions.</li>
                    <li><b>Cluster Validation:</b> K-Means clustering identified 2 distinct risk segments (High Risk: 384 students, Low Risk: 321 students), confirming binary classification validity.</li>
                    <li><b>Feature Pruning:</b> Removed statistically insignificant features (gender, relationship status) with ANOVA P > 0.05, improving model efficiency.</li>
                    <li><b>Robustness:</b> Ensemble learning approach reduces variance and handles feature noise better than single-tree models.</li>
                </ul>
            </div>
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 10px; margin-top: 15px; text-align: center;">
                <span style="color: white; font-size: 0.95rem; font-weight: 600;">
                    💡 This model powers the real-time risk assessment in the <b>Assessment</b> and <b>What-If Simulator</b> pages
                </span>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

# ====================== 5. PAGE: YOUR PERSONAS (INTERACTIVE - FIXED PREDICTION) ======================
elif page == "Your Personas":
    st.markdown("<h2 class='gradient-text'>Discover Your Digital Persona</h2>", unsafe_allow_html=True)
    st.markdown("<p>Use the sliders below to see which digital persona matches your current profile.</p>", unsafe_allow_html=True)

    # --- INPUT SLIDERS ---
   
    
    col_input_1, col_input_2 = st.columns(2)
    
    # Fetch current state of other variables from assessment state (for full model prediction)
    # These are needed to keep the model's feature space consistent
    baseline_stress = st.session_state.get('assessment_stress', 6)
    baseline_academic = st.session_state.get('assessment_academic', "Undergraduate")
    baseline_late_night = st.session_state.get('assessment_late_night', False)
    baseline_fomo = st.session_state.get('assessment_fomo', False)

    with col_input_1:
        st.markdown("<b>Daily Social Media Usage (Hours)</b>", unsafe_allow_html=True)
        # Use session state for initial value
        usage_check = st.slider("Hours", 0.0, 12.0, float(st.session_state.persona_usage_slider), 0.5, key="persona_usage_slider", label_visibility="collapsed")

        st.markdown("<b>Sleep Hours Per Night</b>", unsafe_allow_html=True)
        # Use session state for initial value
        sleep_check = st.slider("Sleep", 4.0, 10.0, float(st.session_state.persona_sleep_slider), 0.5, key="persona_sleep_slider", label_visibility="collapsed")
    with col_input_2:
        st.markdown("<b>Mental Health Score (1-10)</b>", unsafe_allow_html=True)
        # Use session state for initial value
        mental_check = st.slider("Mental Health", 1, 10, int(st.session_state.persona_mental_slider), 1, key="persona_mental_slider", label_visibility="collapsed")
        
        st.markdown("<b>Risk Score Contribution (Model-Based)</b>", unsafe_allow_html=True)
        
        # FIXED LOGIC: Use the actual model to calculate the risk score dynamically
        normalized_risk = predict_risk_score(
            usage=usage_check, 
            sleep=sleep_check, 
            mental=mental_check, 
            stress=baseline_stress, 
            academic=baseline_academic, 
            late_night=baseline_late_night, 
            fomo=baseline_fomo
        )

        st.metric(label="Calculated Risk Score", value=f"{normalized_risk}/10")
        
    st.markdown('</div>', unsafe_allow_html=True)


    # --- LOGIC TO DETERMINE ACTIVE PERSONA ---
    # Now that normalized_risk is model-based, the cutoffs ensure consistency
    if normalized_risk <= 4: # Changed from < 4.5 to <= 4 to match Assessment output categories
        active_persona = "Casual"
    elif 5 <= normalized_risk <= 7: # Changed from 4.5 <= x < 7.5 to 5 <= x <= 7 
        active_persona = "NightOwl"
    else: # normalized_risk >= 8
        active_persona = "DeepDiver"


    # --- PERSONA CARDS ---
    st.write("")
    col1, col2, col3 = st.columns(3)

    # CASUAL SCROLLER CARD
    with col1:
        status_class = "active-card" if active_persona == "Casual" else ""
        st.markdown(f"""
        <div class="persona-card {status_class}" style="border-top: 5px solid #00D2AA;">
            <h3 style='color:#00D2AA'>Casual Scroller</h3>
            <p style='font-weight:700;'>Low Risk (Score <=4)</p>
            <hr>
            <p style='font-size:0.9rem;'>✅ Usage: Typically <4 hrs/day</p>
            <p style='font-size:0.9rem;'>✅ Sleep: Consistently >7.5 hrs</p>
            <p style='font-size:0.9rem;'>✅ Mental Health: High Score >6</p>
        </div>
        """, unsafe_allow_html=True)

    # NIGHT OWL CARD
    with col2:
        status_class = "active-card" if active_persona == "NightOwl" else ""
        st.markdown(f"""
        <div class="persona-card {status_class}" style="border-top: 5px solid #5A7DFF;">
            <h3 style='color:#5A7DFF'>Night Owl</h3>
            <p style='font-weight:700;'>Moderate Risk (Score 5-7)</p>
            <hr>
            <p>⚠️ Usage: Moderate (4-7 hrs/day)</p>
            <p>⚠️ Sleep: Irregular (6-7.5 hrs)</p>
            <p>⚠️ Mental Health: Moderate (4-6)</p>
        </div>
        """, unsafe_allow_html=True)

    # DEEP DIVER CARD
    with col3:
        status_class = "active-card" if active_persona == "DeepDiver" else ""
        st.markdown(f"""
        <div class="persona-card {status_class}" style="border-top: 5px solid #4318FF;">
            <h3 style='color:#4318FF'>Deep Diver</h3>
            <p style='font-weight:700;'>High Risk (Score >=8)</p>
            <hr>
            <p>🚨 Usage: High (>7 hrs/day)</p>
            <p>🚨 Sleep: Deficit (<6 hrs)</p>
            <p>🚨 Mental Health: Low Score (<4)</p>
        </div>
        """, unsafe_allow_html=True)

    # Dynamic Message below cards 
    st.write("")
    if active_persona == "Casual":
        st.success(f"Result: Your profile ({normalized_risk}/10) is in the Healthy Zone! You are a **Casual Scroller**.")
    elif active_persona == "NightOwl":
        st.warning(f"Result: Your profile ({normalized_risk}/10) shows moderate risk. You are a **Night Owl** showing signs of dependency.")
    else:
        st.error(f"Result: Your profile ({normalized_risk}/10) is High Risk. You are a **Deep Diver**. Immediate digital detox is recommended.")

# ====================== 6. PAGE: ASSESSMENT (ENHANCED WITH BETTER UX) ======================
elif page == "Assessment":
    st.markdown("<div style='text-align:center;'><h2 class='gradient-text'>Social Media Addiction Risk Assessment</h2><p>Evidence-based evaluation tool built on analysis of 705 students</p></div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="content-box">
        <h3 style="margin-bottom: 20px; color: #000000;">Your Digital Lifestyle Profile</h3>
        <p style="color: #000000;">Answer honestly for accurate risk assessment</p>
    </div>
    """, unsafe_allow_html=True)


    with st.form("wellbeing_form"):
        
        col1, col2 = st.columns([2, 1])
        
        # NOTE: Initial values for sliders now come from the global st.session_state (assessment_*)

        with col1:
            st.markdown("<b>Daily Social Media Usage</b>", unsafe_allow_html=True)
            usage = st.slider("Hours", 0.5, 12.0, st.session_state.assessment_usage, key='usage_input', label_visibility="collapsed")
            st.caption(f"Selected: {usage} hours/day (Average student: 4.9 hours)")
            st.write("")

            st.markdown("<b>Sleep Hours Per Night</b>", unsafe_allow_html=True)
            sleep = st.slider("Hours", 4.0, 12.0, st.session_state.assessment_sleep, key='sleep_input', label_visibility="collapsed")
            st.caption(f"Selected: {sleep} hours/night (Average student: 6.9 hours)")
            st.write("")

            st.markdown("<b>Mental Health Score (1-10)</b>", unsafe_allow_html=True)
            mental = st.slider("Score", 1, 10, st.session_state.assessment_mental, key='mental_input', label_visibility="collapsed")
            st.write("")

            st.markdown("<b>Stress Level (1-10)</b>", unsafe_allow_html=True)
            stress = st.slider("Stress", 1, 10, st.session_state.assessment_stress, key='stress_input', label_visibility="collapsed")

        with col2:
            st.markdown("<b>Demographics & Details</b>", unsafe_allow_html=True)
            age = st.number_input("Age", 16, 40, 21)
            academic = st.selectbox("Academic Level", ["High School", "Undergraduate", "Postgraduate", "PhD"], index=["High School", "Undergraduate", "Postgraduate", "PhD"].index(st.session_state.assessment_academic))
            platform = st.selectbox("Primary Platform", ["Instagram", "TikTok", "YouTube", "Twitter/X", "Snapchat"])
            
            st.write("")
            late_night = st.checkbox("I use my phone after midnight", value=st.session_state.assessment_late_night)
            fomo = st.checkbox("I feel anxious without my phone", value=st.session_state.assessment_fomo)

        st.write("")
        submitted = st.form_submit_button("Calculate Risk Profile", type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True) 

    if submitted:
        # Calculate final risk score using the Random Forest Model
        risk_score = predict_risk_score(usage, sleep, mental, stress, academic, late_night, fomo)
        
        # 1. Update Assessment session state with submitted values (required for Recommendations & Peer Comparison)
        st.session_state.assessment_usage = usage
        st.session_state.assessment_sleep = sleep
        st.session_state.assessment_mental = mental
        st.session_state.assessment_stress = stress
        st.session_state.assessment_risk = risk_score
        st.session_state.assessment_academic = academic
        st.session_state.assessment_late_night = late_night
        st.session_state.assessment_fomo = fomo
        
        # 2. SYNC TO PERSONA SLIDERS (Page 5)
        st.session_state.persona_usage_slider = usage
        st.session_state.persona_sleep_slider = sleep
        st.session_state.persona_mental_slider = mental
        
        # 3. SYNC TO WHAT-IF SLIDERS (Page 7)
        # Initialize What-If sliders to the *current* assessment values
        st.session_state.what_if_usage = usage
        st.session_state.what_if_sleep = sleep
        
        # Determine risk color based on score (only for visualization)
        if risk_score > 7:
            risk_color = '#4318FF' # High Risk
        elif risk_score > 4:
            risk_color = '#5A7DFF' # Moderate Risk
        else:
            risk_color = '#00D2AA' # Low Risk

        # UPDATED OUTPUT MARKDOWN (Removed risk category text)
        st.markdown(f"""
        <div class="content-box" style="text-align: center; background: linear-gradient(180deg, #fff 0%, #f0f7ff 100%);">
            <h3>Assessment Complete</h3>
            <div style="font-size: 4rem; font-weight: 800; color: {risk_color};">
                {risk_score}/10
            </div>
            <p style="font-size: 1.2rem; font-weight: bold; color: #2B3674;">
                Risk Score Determined by Random Forest Model
            </p>
            <p style='font-size:0.9rem;'>
                This score is derived from the Random Forest model's probability of assigning your profile to its risk cluster.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ====================== 7. WHAT-IF SIMULATOR (UPDATED LOGIC) ======================
elif page == "What-If Simulator":
    st.markdown("<h2 class='gradient-text'>Habit Simulator</h2>", unsafe_allow_html=True)
    
    # Get current (baseline) risk score
    baseline_risk = st.session_state.get('assessment_risk', 5)
    
    # Get other required baseline features (for model consistency)
    baseline_stress = st.session_state.get('assessment_stress', 6)
    baseline_academic = st.session_state.get('assessment_academic', "Undergraduate")
    baseline_late_night = st.session_state.get('assessment_late_night', False)
    baseline_fomo = st.session_state.get('assessment_fomo', False)
    baseline_mental = st.session_state.get('assessment_mental', 6)
    
    st.info(f"Your **Current Risk Score** is **{baseline_risk}/10** (Based on your last Assessment).")
    
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Baseline Usage:** {st.session_state.assessment_usage:.1f} hours")
            # Use state for initial value (synced from Assessment)
            new_usage = st.slider("If I reduce daily usage to...", 1.0, 8.0, float(st.session_state.what_if_usage), 0.5, key='what_if_usage')
        with col2:
            st.markdown(f"**Baseline Sleep:** {st.session_state.assessment_sleep:.1f} hours")
            # Use state for initial value (synced from Assessment)
            new_sleep = st.slider("And increase sleep to...", 6.0, 10.0, float(st.session_state.what_if_sleep), 0.5, key='what_if_sleep')
        
        # Simulate new risk score based on changes, keeping other features constant
        simulated_risk = predict_risk_score(
            usage=new_usage, 
            sleep=new_sleep, 
            mental=baseline_mental, 
            stress=baseline_stress, 
            academic=baseline_academic, 
            late_night=baseline_late_night, 
            fomo=baseline_fomo
        )
        
        # Calculate reduction percentage
        risk_change_absolute = baseline_risk - simulated_risk
        
        # Calculate percentage change for display (max 100% reduction, or simple difference if increase)
        if risk_change_absolute > 0:
            # Risk reduced
            risk_reduction_percentage = min(100, int((risk_change_absolute / baseline_risk) * 100)) if baseline_risk > 0 else 0
            message_html = f"<p style='color:#05CD99; font-weight:bold;'>🎉 Estimated Risk Reduction: {risk_reduction_percentage}%</p>"
        else:
            # Risk increased or no change
            message_html = f"<p style='color:#4318FF; font-weight:bold;'>⚠️ Estimated Risk Change: {abs(risk_change_absolute)} points.</p>"

        col_res, col_chart = st.columns([1, 1])
        
        with col_res:
            st.markdown("##### Simulation Result")
            st.metric(label="Projected Score", value=f"{simulated_risk}/10", delta=risk_change_absolute)
            st.markdown(message_html, unsafe_allow_html=True)

        with col_chart:
            st.markdown("##### Projected 24-Hour Routine")
            # Pie chart colors updated for blue/green compliance
            fig = go.Figure(go.Pie(
                labels=["Sleep", "Social Media", "Productivity", "Leisure"],
                values=[new_sleep, new_usage, 8, 24-new_sleep-new_usage-8],
                hole=0.7,
                marker_colors=['#4318FF', '#5A7DFF', '#00D2AA', '#E6E8EC'],
                textinfo='label+percent'
            ))
            fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

# ====================== 8. RECOMMENDATIONS & PEER COMPARISON ======================
elif page == "Recommendations":
    st.markdown("<h2 class='gradient-text'>Your Wellness Plan</h2>", unsafe_allow_html=True)
    
    # --- RECOMMENDATION LOGIC ---
    recommendations_list = []
    
    # Safely retrieve values from session state, defaulting to average if assessment wasn't run
    current_usage = st.session_state.get('assessment_usage', 4.9)
    current_sleep = st.session_state.get('assessment_sleep', 6.9)
    current_mental = st.session_state.get('assessment_mental', 6)
    
    # 1. USAGE RECOMMENDATION (Threshold: > 4.0 hours is moderate risk)
    if current_usage >= 4.0:
        target_usage = max(3.5, current_usage - 1.0)
        recommendations_list.append({
            'title': f"📉 Reduce Daily Usage to {target_usage:.1f} Hours",
            'detail': f"Your current usage of {current_usage:.1f} hours is high. Focus on reducing time spent on high-addiction platforms like WhatsApp and Snapchat.",
            'color': '#4318FF'
        })

    # 2. SLEEP RECOMMENDATION (Threshold: < 7.0 hours is below optimal)
    if current_sleep < 7.0:
        target_sleep = min(7.5, current_sleep + 0.5)
        recommendations_list.append({
            'title': f"💤 Increase Sleep to {target_sleep:.1f} Hours/Night",
            'detail': f"Low sleep hours ({current_sleep:.1f}h) is a major risk factor. Implement a strict digital curfew (e.g., 11 PM) to improve rest.",
            'color': '#5A7DFF'
        })
    
    # 3. MENTAL HEALTH RECOMMENDATION (Threshold: < 7 is moderate/high risk)
    if current_mental < 7:
        recommendations_list.append({
            'title': f"🧠 Prioritize Mental Wellness (Target Score: 7+)",
            'detail': f"Your Mental Health Score ({current_mental}/10) is a top predictor of addiction. Seek non-digital coping strategies for stress/anxiety.",
            'color': '#00D2AA'
        })

    if not recommendations_list:
        st.success("🎉 You are currently in the **Low Risk Zone!** Continue maintaining healthy usage (<4 hours), good sleep (>7.5 hours), and high mental health (>7).")
    else:
        # Display recommendations
        st.markdown(f"""
        <div class="content-box">
            <h3 style="color: #2B3674;">Top Actionable Steps Based on Your Profile</h3>
        """, unsafe_allow_html=True)

        for rec in recommendations_list:
            st.markdown(f"""
            <div style="background: #f9fbfc; padding: 15px; border-left: 4px solid {rec['color']}; margin: 10px 0;">
                <b style='color:#2B3674;'>{rec['title']}</b>
                <br><span style="color: #707EAE; font-weight:normal; font-size: 0.9rem;">{rec['detail']}</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)


# ====================== 9. PAGE: PEER COMPARISON (UPDATED) ======================
elif page == "Peer Comparison":
    st.markdown("<h2 class='gradient-text'>Peer Comparison & Risk Profiling</h2>", unsafe_allow_html=True)
    st.markdown("<p>See how your core lifestyle metrics compare to the average student in the 705-person study cohort.</p>", unsafe_allow_html=True)

    # Safely retrieve values from session state, defaulting to average if assessment wasn't run
    current_usage = st.session_state.get('assessment_usage', 4.9)
    current_sleep = st.session_state.get('assessment_sleep', 6.9)
    current_mental = st.session_state.get('assessment_mental', 6)
    
    # Study Averages (from notebook data)
    avg_usage = 4.9
    avg_sleep = 6.9
    avg_mental = 6.4 
    
    # --- 1. DATA FOR GROUPED BAR CHART ---
    # Metrics: We use the raw values for the bars, not the scaled/normalized values
    metrics = ['Daily Usage (Hours)', 'Sleep (Hours)', 'Mental Health (Score)']
    
    comparison_data = pd.DataFrame({
        'Metric': metrics,
        'Your Profile': [current_usage, current_sleep, current_mental],
        'Average Student': [avg_usage, avg_sleep, avg_mental]
    })
    
    # Melt the data for Plotly Grouped Bar Chart structure
    df_plot = comparison_data.melt(id_vars='Metric', var_name='Profile', value_name='Value')

    # Create Grouped Bar Chart
    fig_bar = px.bar(
        df_plot,
        x='Value',
        y='Metric',
        color='Profile',
        orientation='h',
        barmode='group',
        color_discrete_map={
            'Your Profile': '#4318FF',
            'Average Student': '#05CD99'
        },
        height=350,
        text='Value'
    )

    # Customize the chart layout
    fig_bar.update_traces(
        texttemplate='%{text:.1f}', 
        textposition='outside'
        # Removed marker_corner_radius=5 which was causing the ValueError
    )
    fig_bar.update_layout(
        xaxis_title="Score/Hours (Raw Value)",
        yaxis_title=None,
        legend_title=None,
        legend=dict(orientation="h", y=1.1, yanchor="top", x=0.5, xanchor="center"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,1)',
        margin=dict(l=0, r=50, t=20, b=20) # Add margin to the right for text display
    )
    
    col_chart, col_summary = st.columns([3, 2])
    
    with col_chart:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.subheader("Raw Metric Comparison")
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_summary:
        st.markdown('<div class="content-box" style="height: 100%;">', unsafe_allow_html=True)
        st.subheader("Deviation Summary")
        
        # Calculate Deviation
        usage_dev = current_usage - avg_usage
        sleep_dev = current_sleep - avg_sleep
        mental_dev = current_mental - avg_mental
        
        # Generate Status Messages
        def get_status(dev, metric, is_higher_better):
            if abs(dev) < 0.1:
                return f"<b>{metric}:</b> Similar to peers."
            
            if is_higher_better:
                if dev > 0:
                    return f"<b>{metric}:</b> **{abs(dev):.1f}** points/hours higher (Healthier)."
                else:
                    return f"<b>{metric}:</b> **{abs(dev):.1f}** points/hours lower (Riskier)."
            else: # Lower value is better (Usage)
                if dev < 0:
                    return f"<b>{metric}:</b> **{abs(dev):.1f}** hours lower (Healthier)."
                else:
                    return f"<b>{metric}:</b> **{abs(dev):.1f}** hours higher (Riskier)."

        status_messages = [
            get_status(usage_dev, "Daily Usage", is_higher_better=False),
            get_status(sleep_dev, "Sleep Hours", is_higher_better=True),
            get_status(mental_dev, "Mental Health Score", is_higher_better=True)
        ]
            
        st.markdown("<p style='font-size:0.95rem;'>Your assessment profile in detail:</p>", unsafe_allow_html=True)
        
        for msg in status_messages:
            # Need to re-bold the status messages using HTML
            styled_msg = msg.replace('**', '<span style="font-weight: bold;">')
            styled_msg = styled_msg.replace('**', '</span>')
            st.markdown(f"<p style='margin-bottom: 5px; font-size: 0.9rem;'>{styled_msg}</p>", unsafe_allow_html=True)
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"""
        <p style='font-size:0.85rem; color:#4318FF;'>
        💡 Insight: The bar chart shows your raw score/hours. Remember that high Usage and low Sleep/Mental Health contribute negatively to your overall risk score.
        </p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ====================== FOOTER ======================
st.markdown("""
<div style="text-align: center; margin-top: 50px; color: #A3AED0; padding-bottom: 20px;">
    <hr style="border: 0; border-top: 1px solid #eee;">
    <p>© 2025 • Digital Wellbeing Dashboard<br>Designed with Streamlit</p>
</div>
""", unsafe_allow_html=True)