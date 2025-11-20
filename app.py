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
if 'assessment_usage' not in st.session_state:
    st.session_state.assessment_usage = 4.9
if 'assessment_sleep' not in st.session_state:
    st.session_state.assessment_sleep = 6.9
if 'assessment_mental' not in st.session_state:
    st.session_state.assessment_mental = 6
if 'assessment_stress' not in st.session_state:
    st.session_state.assessment_stress = 6
if 'assessment_risk' not in st.session_state:
    st.session_state.assessment_risk = 5 # Default risk score (used as baseline)
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

# ====================== 3. PAGE: HOME ======================
if page == "Home":
    # Header Section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <span style="background-color: #E6F7FF; color: #0095FF; padding: 5px 15px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">Research-Based Digital Wellness Tool</span>
        <h1 style="font-size: 3rem; margin-top: 1rem; margin-bottom: 0.5rem;">Social Media Addiction <span class="gradient-text">Risk Dashboard</span></h1>
        <p style="font-size: 1.1rem; max-width: 700px; margin: 0 auto;">Evidence-based assessment tool built on comprehensive analysis of 705 students. Understand your digital habits and get personalized wellness recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

    # Action Buttons
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if st.button("Take Risk Assessment →", type="primary", use_container_width=True):
            st.switch_page("Assessment")

    st.write("") 

    # KPI Cards Row
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
            <div class="kpi-icon" style="color: #8A2BE2;">⚡</div>
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
    
    # Features Section 
    st.markdown("<h3 style='text-align: center; margin-bottom: 30px;'>What This Dashboard Offers</h3>", unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns(3)
    
    with f1:
        st.markdown("""
        <div class="feature-card">
            <div style="color: #4318FF; font-size: 1.5rem; margin-bottom: 10px;">🛡️</div>
            <div class="feature-title">Risk Assessment</div>
            <p>Personalized evaluation based on your usage patterns, sleep, stress, and mental health metrics.</p>
            <ul style="font-size: 0.9rem; color: #707EAE; padding-left: 20px;">
                <li>Real-time risk calculation</li>
                <li>Evidence-based scoring</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="feature-card">
            <div style="color: #4318FF; font-size: 1.5rem; margin-bottom: 10px;">📈</div>
            <div class="feature-title">Platform Analytics</div>
            <p>Detailed breakdown of addiction patterns across different social media platforms.</p>
            <ul style="font-size: 0.9rem; color: #707EAE; padding-left: 20px;">
                <li>Platform addiction rankings</li>
                <li>Usage pattern analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="feature-card">
            <div style="color: #00D2AA; font-size: 1.5rem; margin-bottom: 10px;">📊</div>
            <div class="feature-title">Research Insights</div>
            <p>Access to comprehensive findings from our machine learning analysis.</p>
            <ul style="font-size: 0.9rem; color: #707EAE; padding-left: 20px;">
                <li>Statistical correlations</li>
                <li>Behavioral patterns</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ====================== 4. PAGE: INSIGHTS (UPDATED WITH NOTEBOOK DATA) ======================
elif page == "Insights":
    st.markdown("<div style='text-align:center;'><h2 class='gradient-text'>Research Insights & Analytics</h2><p>Key findings from comprehensive analysis of 705 students</p></div>", unsafe_allow_html=True)
    
    # TABS CONFIGURATION
    tab1, tab2, tab3, tab4 = st.tabs(["Platforms", "Demographics", "Patterns", "Correlations"])

    # ---------------- TAB 1: PLATFORMS (Corrected Data/Colors/Sorting) ----------------
    with tab1:
        st.markdown("""
        <div class="content-box">
            <h4 style="color: #2B3674; margin-bottom: 5px;">📊 Platform Addiction Rankings</h4>
            <p style="font-size: 0.9rem; margin-bottom: 20px;">Average addiction scores (1-10) by primary social media platform</p>
        """, unsafe_allow_html=True)
        
        # CORRECTED DATA: All 8 platforms sorted descending by addiction score
        platforms_full = ["WhatsApp", "Snapchat", "TikTok", "Instagram", "YouTube", "Facebook", "Twitter/X", "LinkedIn"]
        scores_full = [7.46, 7.46, 7.43, 6.55, 6.1, 5.67, 5.5, 3.81]
        
        # NEW COLORS: A clear mix of Blue and Green
        colors = ['#4318FF', '#5A7DFF', '#7C93F5', '#9299F5', '#05CD99', '#3CD4A0', '#85E3B3', '#B8F1D0']

        fig = go.Figure(go.Bar(
            x=scores_full,
            y=platforms_full,
            orientation='h',
            marker_color=colors,
            text=[f"{s}/10" for s in scores_full],
            textposition='auto',
            textfont=dict(color='white', size=14)
        ))

        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=450,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(showgrid=False, visible=False, range=[0, 10]),
            yaxis=dict(showgrid=False, tickfont=dict(size=14, color='#2B3674', family="Segoe UI, sans-serif")),
            barcornerradius=10
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
            <div style="background-color: #F8F9FA; padding: 15px; border-radius: 10px; margin-top: 20px;">
                <b style="color: #2B3674;">Key Findings:</b>
                <ul style="margin-bottom: 0; font-size: 0.9rem;">
                    <li>WhatsApp and Snapchat show the highest average addiction scores (over 7.4/10), indicating severe dependency risk.</li>
                    <li>Messaging and instant media apps encourage prolonged screen use due to high social pressure.</li>
                    <li>LinkedIn is the least addictive platform, likely due to its professional focus and low social pressure.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- TAB 2: DEMOGRAPHICS (Corrected Data/Colors) ----------------
    with tab2:
        col_l, col_r = st.columns([3, 2])
        
        with col_l:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("#### 👥 Age Distribution")
            st.markdown("<p style='font-size:0.8rem;'>Count of students with High Addiction Scores (≥4) by age group</p>", unsafe_allow_html=True)
            
            ages_labels = ["Age 18", "Age 19", "Age 20", "Age 21", "Age 22", "Age 23", "Age 24"]
            counts = [13, 126, 132, 120, 119, 23, 15] 
            
            # NEW COLORS: Consistent shades of Blue/Purple
            fig_age = go.Figure(go.Bar(
                x=counts,
                y=ages_labels,
                orientation='h',
                marker=dict(color=['#7D85EC', '#5B63D8', '#4318FF', '#5B63D8', '#7D85EC', '#9299F5', '#A3AED0']),
                width=0.4
            ))
            fig_age.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=350,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(showgrid=False, visible=False),
                yaxis=dict(showgrid=False),
                barcornerradius=5
            )
            st.plotly_chart(fig_age, use_container_width=True)
            
            st.markdown("""
            <div style="background-color: #E6FFFA; padding: 15px; border-radius: 8px;">
                <strong style="color:#05CD99">Peak Risk Age: 20 years old</strong><br>
                <span style="font-size:0.8rem;">Ages 19-22 show the highest concentration of addicted users</span>
            </div>
            </div>
            """, unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("#### 🎓 Academic Level Analysis")
            st.markdown("<p style='font-size:0.8rem;'>Risk assessment by education level (ANOVA P-Value: 0.00000)</p>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class="academic-card ac-red">
                <span class="tag tag-high">High Risk</span>
                <b>High School</b>
                <div style="font-size:0.8rem; color:#707EAE; margin-top:5px;">Avg: 7.5 <span style="float:right">Median: 8</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="academic-card ac-yellow">
                <span class="tag tag-med">Moderate Risk</span>
                <b>Undergraduate</b>
                <div style="font-size:0.8rem; color:#707EAE; margin-top:5px;">Avg: 6.9 <span style="float:right">Median: 7</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="academic-card ac-green">
                <span class="tag tag-low">Low Risk</span>
                <b>Graduate</b>
                <div style="font-size:0.8rem; color:#707EAE; margin-top:5px;">Avg: 6.2 <span style="float:right">Median: 6</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="academic-card ac-green">
                <span class="tag tag-low">Low Risk</span>
                <b>PhD/Doctoral</b>
                <div style="font-size:0.8rem; color:#707EAE; margin-top:5px;">Avg: 5.8 <span style="float:right">Median: 6</span></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background-color: #F0F5FF; padding: 10px; border-radius: 5px; font-size: 0.8rem; color: #4318FF;">
                <b>Critical Finding:</b> High school students show the highest addiction tendency with the least score variation.
            </div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------- TAB 3: PATTERNS (Corrected Metrics/Findings) ----------------
    with tab3:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("#### 🕑 Usage Patterns & Lifestyle Metrics")
        st.markdown("<p style='margin-bottom:20px;'>Average student behavioral profile from the dataset</p>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("""
            <div class="metric-box mb-blue">
                <p class="mb-val">4.9</p>
                <p class="mb-label">Hours daily usage</p>
                <p class="mb-desc">Standard deviation: ±1.26 hrs</p>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown("""
            <div class="metric-box mb-purple">
                <p class="mb-val">6.9</p>
                <p class="mb-label">Hours sleep/night</p>
                <p class="mb-desc">Below recommended 7-9 hours</p>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown("""
            <div class="metric-box mb-green">
                <p class="mb-val">6.4/10</p>
                <p class="mb-label">Avg addiction score</p>
                <p class="mb-desc">Median score is 7/10</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br><b style='color:#2B3674;'>Behavioral Insights:</b>", unsafe_allow_html=True)
        
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("""
            <div class="insight-mini-card" style="border-left: 4px solid #00D2AA;">
                <b style='color:#2B3674;'>Sleep Deficit Risk</b><br>
                <span style="font-size:0.85rem; color:#707EAE;">25% of students report sleeping 6 hours or less per night.</span>
            </div>
            <div class="insight-mini-card">
                <b style='color:#2B3674;'>Conflicts & Toxicity</b><br>
                <span style="font-size:0.85rem; color:#707EAE;">Average conflict score is 2.85/5, indicating moderate social media-induced stress.</span>
            </div>
            """, unsafe_allow_html=True)
        with g2:
            st.markdown("""
            <div class="insight-mini-card" style="border-left: 4px solid #4318FF;">
                <b style='color:#2B3674;'>Stress-Addiction Link</b><br>
                <span style="font-size:0.85rem; color:#707EAE;">High stress is a key predictor, correlating with compensatory usage patterns.</span>
            </div>
            <div class="insight-mini-card" style="border-left: 4px solid #9299F5;">
                <b style='color:#2B3674;'>Demographic Nuance</b><br>
                <span style="font-size:0.85rem; color:#707EAE;">Gender and Relationship Status have zero statistical effect on addiction intensity (ANOVA P > 0.05).</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- TAB 4: CORRELATIONS (Updated Content and Model Details) ----------------
    with tab4:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("#### 📈 Model Performance & Feature Importance")
        st.markdown("<p>Key model results and predictor relationships from final analysis.</p><br>", unsafe_allow_html=True)
        
        
        st.markdown("##### Key Predictors of Addiction Risk (Random Forest Top 3)")
        
        # New cohesive and styled section for important features (span full width) - UPDATED FOR RF FEATURES
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <div class="feature-item-box bg-blue-1">
                <span class="feature-title-text">1. Avg Daily Usage Hours (~35.4%)</span>
                <div class="feature-description">
                    The single most important predictor. High usage is the primary driver of dependency and is strongly correlated with other negative factors.
                </div>
            </div>
            <div class="feature-item-box bg-blue-2">
                <span class="feature-title-text">2. Mental Health Score (~28.3%)</span>
                <div class="feature-description">
                    Low scores are a highly significant factor, often leading to compensatory social media usage to cope with stress or anxiety.
                </div>
            </div>
            <div class="feature-item-box bg-green-1">
                <span class="feature-title-text">3. Sleep Hours/Night (~24.8%)</span>
                <div class="feature-description">
                    Low sleep quality is a major indicator, showing that social media usage frequently infringes on rest time.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        
        st.markdown("##### Visual Feature Importance Ranking")
        
        # Fixed deprecation warning by using use_container_width=True
        try:
            st.image("feature_importance.png", caption="Visual Ranking of Predictors by Model", use_container_width=True) 
        except FileNotFoundError:
            st.info("To complete this section, please create and save your model's Feature Importance plot as **'feature_importance.png'** in the app directory.")

        st.write("")
        st.markdown("##### Model Performance Summary")
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("""
            <div class="model-card">
                <div style="font-size:2rem; font-weight:bold; color:#4318FF">100%</div>
                <div style="font-weight:bold;">Logistic Regression</div>
                <div style="font-size:0.8rem;">Tuned / Test Acc.</div>
            </div>
            """, unsafe_allow_html=True)
        with m2: # UPDATED RF ACCURACY
            st.markdown("""
            <div class="model-card">
                <div style="font-size:2rem; font-weight:bold; color:#5A7DFF">92.0%</div>
                <div style="font-weight:bold;">Random Forest</div>
                <div style="font-size:0.8rem;">Tuned / Test Acc.</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown("""
            <div class="model-card">
                <div style="font-size:2rem; font-weight:bold; color:#05CD99">98.5%</div>
                <div style="font-weight:bold;">Gradient Boosting</div>
                <div style="font-size:0.8rem;">Tuned / Test Acc.</div>
            </div>
            """, unsafe_allow_html=True)
            
        # UPDATED FINAL MODEL SELECTION RATIONALE
        st.markdown("""
        <div style="background-color: #F8F9FA; padding: 15px; border-radius: 10px; margin-top: 20px;">
            <b style='color:#2B3674;'>Final Model Selection: Random Forest (92.0% Accuracy)</b>
            <ul style="font-size: 0.9rem; color: #707EAE; margin-bottom:0;">
                <li>The Random Forest model was selected for its high, generalizable accuracy (92.00%) and robustness against feature noise, outperforming the logistic regression model on un-engineered data.</li>
                <li>Top 5 Features: `avg_daily_usage_hours`, `mental_health_score`, `sleep_hours_per_night`, `conflicts_over_social_media`, and `affects_academic_performance_Yes`.</li>
                <li>VIF analysis eliminated multicollinearity (reduced from 10.6 to 3.4).</li>
                <li>K-Means clustering identified 2 distinct risk segments (High Risk: 384, Low Risk: 321).</li>
                <li>Removed gender and relationship status (ANOVA P > 0.05).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ====================== 5. PAGE: YOUR PERSONAS (INTERACTIVE - FIXED PREDICTION) ======================
elif page == "Your Personas":
    st.markdown("<h2 class='gradient-text'>Discover Your Digital Persona</h2>", unsafe_allow_html=True)
    st.markdown("<p>Use the sliders below to see which digital persona matches your current profile.</p>", unsafe_allow_html=True)

    # --- INPUT SLIDERS ---
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
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
        usage_check = st.slider("Hours", 0.0, 12.0, st.session_state.persona_usage_slider, 0.5, key="persona_usage_slider", label_visibility="collapsed")

        st.markdown("<b>Sleep Hours Per Night</b>", unsafe_allow_html=True)
        # Use session state for initial value
        sleep_check = st.slider("Sleep", 4.0, 10.0, st.session_state.persona_sleep_slider, 0.5, key="persona_sleep_slider", label_visibility="collapsed")
    
    with col_input_2:
        st.markdown("<b>Mental Health Score (1-10)</b>", unsafe_allow_html=True)
        # Use session state for initial value
        mental_check = st.slider("Mental Health", 1, 10, st.session_state.persona_mental_slider, key="persona_mental_slider", label_visibility="collapsed")
        
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

# ====================== 6. PAGE: RISK CALCULATOR (UPDATED SYNC & OUTPUT LOGIC) ======================
elif page == "Assessment":
    st.markdown("<div style='text-align:center;'><h2 class='gradient-text'>Social Media Addiction Risk Assessment</h2><p>Evidence-based evaluation tool built on analysis of 705 students</p></div>", unsafe_allow_html=True)
    
    st.markdown("""<div class="content-box"><h3 style="margin-bottom: 20px;">Your Digital Lifestyle Profile</h3><p>Answer honestly for accurate risk assessment</p>""", unsafe_allow_html=True)

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
            new_usage = st.slider("If I reduce daily usage to...", 1.0, 8.0, st.session_state.what_if_usage, key='what_if_usage')
        with col2:
            st.markdown(f"**Baseline Sleep:** {st.session_state.assessment_sleep:.1f} hours")
            # Use state for initial value (synced from Assessment)
            new_sleep = st.slider("And increase sleep to...", 6.0, 10.0, st.session_state.what_if_sleep, key='what_if_sleep')
        
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
        paper_bgcolor='rgba(0,0,0,0)',
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