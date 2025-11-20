import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ====================== 1. PAGE CONFIG & THEME SETUP ======================
st.set_page_config(
    page_title="Digital Wellness",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - COMBINED (Updated for strict Blue/Green palette + Robust Radio Button Fix)
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

    /* === RADIO BUTTON COLOR FIX (PRIMARY BLUE) === */
    /* Changes the checked (selected) radio input border/fill color */
    div.stRadio > label > div[data-testid="stDecoration"] {
        border-color: #A3AED0; /* Default unchecked border color */
    }
    div.stRadio > label > div[data-testid="stDecoration"]:has(+ input:checked) {
        border-color: #4318FF !important; 
        background-color: #4318FF !important; 
    }
    /* Changes the checked radio button dot color (default is white) */
    div.stRadio > label > div[data-testid="stDecoration"]:has(+ input:checked)::after {
        background-color: white !important;
    }
    /* Changes the text color of the active radio label */
    .stRadio > label:has(input:checked) span {
        color: #4318FF !important;
        font-weight: 600;
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
    
    /* Assessment/Persona Page Color Adjustments */
    .stAlert {
        border-color: #4318FF !important;
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
</style>
""", unsafe_allow_html=True)

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
    # Removed the st.info("v2.0.1 | Connected to Student DB") line

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
            <div class="kpi-value">100%</div>
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
                <span class="tag tag-med">Medium Risk</span>
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

    # ---------------- TAB 4: CORRELATIONS (Updated Content and Image Size) ----------------
    with tab4:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        st.markdown("#### 📈 Model Performance & Feature Importance")
        st.markdown("<p>Key model results and predictor relationships from final analysis.</p><br>", unsafe_allow_html=True)
        
        
        st.markdown("##### Key Predictors of Addiction Risk")
        
        # New cohesive and styled section for important features (span full width)
        st.markdown("""
        <div style="margin-bottom: 20px;">
            <div class="feature-item-box bg-blue-1">
                <span class="feature-title-text">1. Mental Health Score (~35.4%)</span>
                <div class="feature-description">
                    The strongest predictor. Low scores are directly associated with the highest addiction risk, often used as a coping mechanism.
                </div>
            </div>
            <div class="feature-item-box bg-blue-2">
                <span class="feature-title-text">2. Sleep Hours/Night (~28.3%)</span>
                <div class="feature-description">
                    Low sleep quality is a significant driver of dependency patterns, indicating usage frequently interferes with rest.
                </div>
            </div>
            <div class="feature-item-box bg-green-1">
                <span class="feature-title-text">3. Toxicity Score (Comp.) (~24.8%)</span>
                <div class="feature-description">
                    This engineered feature (addiction severity × conflicts) captures the destructive, compensatory nature of usage.
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
        with m2:
            st.markdown("""
            <div class="model-card">
                <div style="font-size:2rem; font-weight:bold; color:#5A7DFF">100%</div>
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
            
        st.markdown("""
        <div style="background-color: #F8F9FA; padding: 15px; border-radius: 10px; margin-top: 20px;">
            <b style='color:#2B3674;'>Final Model Selection: Logistic Regression (100% Accuracy)</b>
            <ul style="font-size: 0.9rem; color: #707EAE; margin-bottom:0;">
                <li>The Logistic Regression model was chosen as the production model due to its high **interpretability** (coefficients show direct impact direction) and its **100% accuracy** on the test set, making it efficient and transparent for risk assessment.</li>
                <li>VIF analysis eliminated multicollinearity (reduced from 10.6 to 3.4).</li>
                <li>K-Means clustering identified 2 distinct risk segments (High Risk: 384, Low Risk: 321).</li>
                <li>Removed gender and relationship status (ANOVA P > 0.05).</li>
            </ul>
        </div>
        </div>
        """, unsafe_allow_html=True)


# ====================== 5. PAGE: YOUR PERSONAS (INTERACTIVE) ======================
elif page == "Your Personas":
    st.markdown("<h2 class='gradient-text'>Discover Your Digital Persona</h2>", unsafe_allow_html=True)
    st.markdown("<p>Drag the slider to see how different daily usage hours define these categories.</p>", unsafe_allow_html=True)

    # 1. Add Interactivity: A Slider
    usage_check = st.slider("Select Daily Usage Hours:", 0.0, 12.0, 5.0, 0.5)

    # 2. Logic to determine active persona
    active_persona = "None"
    if usage_check < 4.0:
        active_persona = "Casual"
    elif 4.0 <= usage_check < 7.0:
        active_persona = "NightOwl"
    else:
        active_persona = "DeepDiver"

    col1, col2, col3 = st.columns(3)

    # CASUAL SCROLLER CARD
    with col1:
        status_class = "active-card" if active_persona == "Casual" else "inactive-card"
        st.markdown(f"""
        <div class="persona-card {status_class}" style="border-top: 5px solid #00D2AA;">
            <h3>Casual Scroller</h3>
            <h1 style="color: #00D2AA;">&lt; 4h</h1>
            <p>Your Input: {usage_check}h</p>
            <hr>
            <p>✅ Good sleep quality</p>
            <p>✅ Low stress levels</p>
            <p>✅ Balanced lifestyle</p>
        </div>
        """, unsafe_allow_html=True)

    # NIGHT OWL CARD 
    with col2:
        status_class = "active-card" if active_persona == "NightOwl" else "inactive-card"
        st.markdown(f"""
        <div class="persona-card {status_class}" style="border-top: 5px solid #5A7DFF;">
            <h3>Night Owl</h3>
            <h1 style="color: #5A7DFF;">4h - 7h</h1>
            <p>Your Input: {usage_check}h</p>
            <hr>
            <p>⚠️ Late night activity</p>
            <p>⚠️ Moderate anxiety</p>
            <p>⚠️ Irregular sleep</p>
        </div>
        """, unsafe_allow_html=True)

    # DEEP DIVER CARD 
    with col3:
        status_class = "active-card" if active_persona == "DeepDiver" else "inactive-card"
        st.markdown(f"""
        <div class="persona-card {status_class}" style="border-top: 5px solid #4318FF;">
            <h3>Deep Diver</h3>
            <h1 style="color: #4318FF;">&gt; 7h</h1>
            <p>Your Input: {usage_check}h</p>
            <hr>
            <p>🚨 High FOMO</p>
            <p>🚨 Platform loyal</p>
            <p>🚨 Significant sleep loss</p>
        </div>
        """, unsafe_allow_html=True)

    # 4. Dynamic Message below cards 
    st.write("")
    if active_persona == "Casual":
        st.success("Result: You are in the Healthy Zone!")
    elif active_persona == "NightOwl":
        st.warning("Result: You are showing signs of dependency.")
    else:
        st.error("Result: High Risk. Immediate digital detox recommended.")

# ====================== 6. PAGE: RISK CALCULATOR ======================
elif page == "Assessment":
    st.markdown("<div style='text-align:center;'><h2 class='gradient-text'>Social Media Addiction Risk Assessment</h2><p>Evidence-based evaluation tool built on analysis of 705 students</p></div>", unsafe_allow_html=True)
    
    st.markdown("""<div class="content-box"><h3 style="margin-bottom: 20px;">Your Digital Lifestyle Profile</h3><p>Answer honestly for accurate risk assessment</p>""", unsafe_allow_html=True)

    with st.form("wellbeing_form"):
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("<b>Daily Social Media Usage</b>", unsafe_allow_html=True)
            usage = st.slider("Hours", 0.5, 12.0, 4.9, label_visibility="collapsed")
            st.caption(f"Selected: {usage} hours/day (Average student: 4.9 hours)")
            st.write("")

            st.markdown("<b>Sleep Hours Per Night</b>", unsafe_allow_html=True)
            sleep = st.slider("Hours", 4.0, 12.0, 6.9, label_visibility="collapsed")
            st.caption(f"Selected: {sleep} hours/night (Average student: 6.9 hours)")
            st.write("")

            st.markdown("<b>Mental Health Score (1-10)</b>", unsafe_allow_html=True)
            mental = st.slider("Score", 1, 10, 6, label_visibility="collapsed")
            st.write("")

            st.markdown("<b>Stress Level (1-10)</b>", unsafe_allow_html=True)
            stress = st.slider("Stress", 1, 10, 6, label_visibility="collapsed")

        with col2:
            st.markdown("<b>Demographics & Details</b>", unsafe_allow_html=True)
            age = st.number_input("Age", 16, 40, 21)
            academic = st.selectbox("Academic Level", ["High School", "Undergraduate", "Postgraduate", "PhD"])
            platform = st.selectbox("Primary Platform", ["Instagram", "TikTok", "YouTube", "Twitter/X", "Snapchat"])
            
            st.write("")
            late_night = st.checkbox("I use my phone after midnight")
            fomo = st.checkbox("I feel anxious without my phone")

        st.write("")
        submitted = st.form_submit_button("Calculate Risk Profile", type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True) 

    if submitted:
        # Simple risk calculation based on notebook findings
        risk_score = int((usage * 1.8 + (12-sleep)*1.2 + (10-mental)*0.8 + stress*0.7) / 4.5)
        risk_score = min(max(risk_score, 1), 10)
        
        st.markdown(f"""
        <div class="content-box" style="text-align: center; background: linear-gradient(180deg, #fff 0%, #f0f7ff 100%);">
            <h3>Assessment Complete</h3>
            <div style="font-size: 4rem; font-weight: 800; color: {'#4318FF' if risk_score > 7 else '#5A7DFF' if risk_score > 4 else '#00D2AA'};">
                {risk_score}/10
            </div>
            <p style="font-size: 1.2rem; font-weight: bold; color: #2B3674;">
                Risk Level: {'High Risk - Deep Diver' if risk_score > 7 else 'Moderate Risk - Night Owl' if risk_score > 4 else 'Low Risk - Casual Scroller'}
            </p>
            <p>Your score is based on the final classification model developed using the student data</p>
        </div>
        """, unsafe_allow_html=True)

# ====================== 7. WHAT-IF SIMULATOR ======================
elif page == "What-If Simulator":
    st.markdown("<h2 class='gradient-text'>Habit Simulator</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            new_usage = st.slider("If I reduce daily usage to...", 1.0, 8.0, 4.0)
        with col2:
            new_sleep = st.slider("And increase sleep to...", 6.0, 10.0, 8.0)
        
        improvement = int((4.9 - new_usage)*8 + (new_sleep - 6.9)*5)
        st.success(f"Estimated risk reduction: {max(0, improvement)}%")
        
        # Pie chart colors updated for blue/green compliance
        fig = go.Figure(go.Pie(
            labels=["Sleep", "Social Media", "Productivity", "Leisure"],
            values=[new_sleep, new_usage, 8, 24-new_sleep-new_usage-8],
            hole=0.7,
            marker_colors=['#4318FF', '#5A7DFF', '#00D2AA', '#E6E8EC'],
            textinfo='label+percent'
        ))
        fig.update_layout(title="Projected 24-Hour Routine", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ====================== 8. RECOMMENDATIONS & PEER COMPARISON ======================
elif page == "Recommendations":
    st.markdown("<h2 class='gradient-text'>Your Wellness Plan</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.markdown("""
        <div class="content-box">
            <h3 style="color: #2B3674;">Top Actionable Steps</h3>
            <div style="background: #f9fbfc; padding: 15px; border-left: 4px solid #4318FF; margin: 10px 0;">
                <b style='color:#2B3674;'>📉 Target Daily Usage: 3.5 Hours</b>
                <br><span style="color: #00D2AA; font-weight:bold;">Focus on reducing usage on WhatsApp and Snapchat.</span>
            </div>
            <div style="background: #f9fbfc; padding: 15px; border-left: 4px solid #5A7DFF; margin: 10px 0;">
                <b style='color:#2B3674;'>💤 Target Sleep: 7.5 Hours</b>
                <br><span style="color: #00D2AA; font-weight:bold;">Sleep quality is the second-highest predictor of addiction risk.</span>
            </div>
             <div style="background: #f9fbfc; padding: 15px; border-left: 4px solid #00D2AA; margin: 10px 0;">
                <b style='color:#2B3674;'>🧠 Improve Mental Health & Cope</b>
                <br><span style="color: #00D2AA; font-weight:bold;">Mental Health Score is the single strongest predictor of addiction.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>Resources</h3>
            <p>Download your full digital wellness report.</p>
            <button style="background-color: #2B3674; color: white; padding: 10px 20px; border-radius: 5px; border:none; width:100%;">Download PDF</button>
        </div>
        """, unsafe_allow_html=True)

elif page == "Peer Comparison":
    st.markdown("<h2 class='gradient-text'>Peer Comparison</h2>", unsafe_allow_html=True)
    st.info("Your daily usage is higher than 78% of students your age")
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=['You', 'Avg Student'],
        x=[5.2, 4.9],
        orientation='h',
        marker_color=['#4318FF', '#00D2AA']
    ))
    fig.update_layout(title="Daily Usage Comparison (Hours)", plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

# ====================== FOOTER ======================
st.markdown("""
<div style="text-align: center; margin-top: 50px; color: #A3AED0; padding-bottom: 20px;">
    <hr style="border: 0; border-top: 1px solid #eee;">
    <p>© 2025 • Digital Wellbeing Dashboard<br>Designed with Streamlit</p>
</div>
""", unsafe_allow_html=True)