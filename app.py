import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import ranker
from pathlib import Path
import plotly.express as px

# Configure page layout and style
st.set_page_config(
    page_title="Redrob AI Ranker | Talent Acquisition Brain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium CSS injection
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        
        /* Sidebar styling overrides */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #07090E 0%, #0F1420 100%) !important;
            border-right: 1px solid rgba(56, 189, 248, 0.12) !important;
            box-shadow: 5px 0 25px rgba(0, 0, 0, 0.6) !important;
        }
        
        /* Customize sidebar scrollbar */
        [data-testid="stSidebar"]::-webkit-scrollbar {
            width: 4px;
        }
        [data-testid="stSidebar"]::-webkit-scrollbar-thumb {
            background: rgba(56, 189, 248, 0.2);
            border-radius: 2px;
        }
        [data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover {
            background: #00E5FF;
        }
        
        /* Sidebar Labels Styling */
        [data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            color: #E5E7EB !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
            font-size: 0.8rem !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stTextInput"] input,
        [data-testid="stSidebar"] [data-testid="stTextarea"] textarea {
            background-color: rgba(15, 23, 42, 0.5) !important;
            border: 1px solid rgba(56, 189, 248, 0.2) !important;
            color: #F3F4F6 !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stTextInput"] input:focus,
        [data-testid="stSidebar"] [data-testid="stTextarea"] textarea:focus {
            border-color: #00E5FF !important;
            box-shadow: 0 0 12px rgba(0, 229, 255, 0.3) !important;
            background-color: rgba(15, 23, 42, 0.7) !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stFileUploader"] {
            background-color: rgba(15, 23, 42, 0.3) !important;
            border: 1px dashed rgba(56, 189, 248, 0.25) !important;
            border-radius: 8px !important;
            padding: 12px !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stFileUploader"] button {
            background-color: rgba(56, 189, 248, 0.1) !important;
            color: #38BDF8 !important;
            border: 1px solid rgba(56, 189, 248, 0.3) !important;
            border-radius: 6px !important;
            transition: all 0.2s ease !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stFileUploader"] button:hover {
            background-color: rgba(0, 229, 255, 0.15) !important;
            color: #00E5FF !important;
            border-color: #00E5FF !important;
            box-shadow: 0 0 12px rgba(0, 229, 255, 0.25) !important;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0B0E14;
        }
        ::-webkit-scrollbar-thumb {
            background: #1E293B;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #38BDF8;
        }
        
        /* Global Streamlit elements overrides */
        .stApp {
            background-color: #0B0E14;
        }
        
        /* Streamlit Tab Styling Override */
        button[data-baseweb="tab"] {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            color: #9CA3AF !important;
            background-color: transparent !important;
            border: none !important;
            padding: 10px 20px !important;
            transition: all 0.2s ease-in-out !important;
        }
        button[data-baseweb="tab"]:hover {
            color: #38BDF8 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #00E5FF !important;
            border-bottom: 2px solid #00E5FF !important;
            text-shadow: 0 0 10px rgba(0, 229, 255, 0.2);
        }
        
        /* Custom Neon Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            margin: 2px;
        }
        .badge-green {
            background: rgba(16, 185, 129, 0.1);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .badge-yellow {
            background: rgba(245, 158, 11, 0.1);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .badge-red {
            background: rgba(239, 68, 68, 0.1);
            color: #F87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        .badge-blue {
            background: rgba(56, 189, 248, 0.1);
            color: #38BDF8;
            border: 1px solid rgba(56, 189, 248, 0.3);
        }
        
        /* Pulsate Animation */
        @keyframes pulse-glow {
            0% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.4); }
            70% { box-shadow: 0 0 0 8px rgba(56, 189, 248, 0); }
            100% { box-shadow: 0 0 0 0 rgba(56, 189, 248, 0); }
        }
        .pulse-active {
            width: 8px;
            height: 8px;
            background-color: currentColor;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px currentColor;
            animation: pulse-glow 2s infinite;
        }
        
        .main-title {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            background: linear-gradient(90deg, #38BDF8, #00E5FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem;
            margin-bottom: 0.2rem;
            letter-spacing: -0.02em;
        }
        
        .sub-title {
            font-size: 1.05rem;
            color: #9CA3AF;
            margin-bottom: 2rem;
            font-weight: 400;
        }
        
        /* Glassmorphism Metric Cards */
        .metric-card {
            background: linear-gradient(135deg, rgba(21, 30, 46, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
            border-radius: 16px;
            border: 1px solid rgba(56, 189, 248, 0.15);
            padding: 1.5rem;
            text-align: center;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: rgba(0, 229, 255, 0.5);
            box-shadow: 0 0 25px rgba(0, 229, 255, 0.25);
        }
        
        .metric-num {
            font-family: 'Outfit', sans-serif;
            font-weight: 800;
            font-size: 2.5rem;
            color: #00E5FF;
            margin: 0.1rem 0;
            text-shadow: 0 0 20px rgba(0, 229, 255, 0.3);
        }
        
        .metric-label {
            font-size: 0.8rem;
            color: #9CA3AF;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 600;
        }
        
        /* Timeline style with neon blue glows */
        .timeline-card {
            border-left: 2px solid #38BDF8;
            padding-left: 1.5rem;
            margin-left: 0.5rem;
            margin-bottom: 1.5rem;
            position: relative;
        }
        
        .timeline-dot {
            height: 12px;
            width: 12px;
            background-color: #00E5FF;
            border-radius: 50%;
            position: absolute;
            left: -7px;
            top: 6px;
            box-shadow: 0 0 10px #00E5FF, 0 0 20px #00E5FF;
        }
        
        .timeline-company {
            font-weight: 700;
            font-size: 1.05rem;
            color: #F9FAFB;
        }
        
        .timeline-title {
            font-weight: 500;
            color: #38BDF8;
            font-size: 0.95rem;
        }
        
        .timeline-dates {
            font-size: 0.8rem;
            color: #9CA3AF;
        }
        
        .reasoning-box {
            background-color: rgba(56, 189, 248, 0.06);
            border-left: 4px solid #38BDF8;
            padding: 1.25rem;
            border-radius: 0 12px 12px 0;
            margin-bottom: 1.5rem;
            box-shadow: inset 0 0 15px rgba(56, 189, 248, 0.02);
        }
    </style>
""", unsafe_allow_html=True)

# Preloaded Job Description
DEFAULT_JD = """Job Description: Senior AI Engineer — Founding Team
Company: Redrob AI (Series A AI-native talent intelligence platform)
Location: Pune/Noida, India (Hybrid) | Open to relocation candidates from Tier-1 Indian cities
Employment Type: Full-time
Experience Required: 5–9 years

We need a Senior AI Engineer to own the intelligence layer of Redrob's product.
Required:
- Production experience with embeddings-based retrieval systems (sentence-transformers, OpenAI embeddings, BGE, E5)
- Vector databases or hybrid search infrastructure (Pinecone, Weaviate, Qdrant, Milvus, OpenSearch, Elasticsearch, FAISS)
- Strong Python code quality
- Design offline/online evaluation frameworks for ranking systems (NDCG, MRR, MAP)
Nice to have:
- LLM fine-tuning experience (LoRA, QLoRA, PEFT)
- Learning-to-rank models (XGBoost-based or neural)

Disqualifiers:
- Pure academic/research environment (no production deployment)
- AI experience consisting primarily of recent (<12 months) LangChain tutorials
- Consulting/service-company background (TCS, Infosys, Wipro, Accenture, Capgemini, Cognizant, etc.) in entire career
- CV/speech/robotics specialists without NLP/IR exposure"""

# Load and cache candidate dataset
@st.cache_data
def load_candidates(file_path, limit=None):
    cands = []
    honeypots_caught = 0
    consulting_filtered = 0
    total_raw = 0
    
    if not os.path.exists(file_path):
        return [], 0, 0, 0
        
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            total_raw += 1
            cand = json.loads(line)
            
            # Pre-filter checks to count statistics
            hp, _ = ranker.is_honeypot(cand)
            if hp:
                honeypots_caught += 1
            elif ranker.is_consulting_only(cand):
                consulting_filtered += 1
                
            cands.append(cand)
            if limit and len(cands) >= limit:
                break
                
    return cands, total_raw, honeypots_caught, consulting_filtered

# Main Layout
st.markdown("<div class='main-title'>🧠 Redrob AI Recruiter Brain</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Intelligent Candidate Discovery, Trap Filtering, and Predictive Ranking Dashboard</div>", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 1rem; padding-top: 1rem;">
        <img src="https://img.icons8.com/nolan/96/brain.png" style="width: 70px; filter: drop-shadow(0 0 12px rgba(0, 229, 255, 0.45));" />
        <h2 style="font-family: 'Outfit', sans-serif; font-weight: 800; background: linear-gradient(90deg, #38BDF8, #00E5FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 0.5rem; margin-bottom: 0.2rem; font-size: 1.35rem; letter-spacing: -0.02em;">RECRUIT COCKPIT</h2>
        <p style="color: #9CA3AF; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; margin-bottom: 1.5rem;">Engine Control Center</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
    <div style="border-left: 3px solid #00E5FF; padding-left: 10px; margin: 1.2rem 0 0.8rem 0;">
        <h4 style="font-family: 'Outfit', sans-serif; font-weight: 700; color: #F3F4F6; margin: 0; font-size: 1rem; letter-spacing: 0.03em; text-transform: uppercase;">🔧 Configuration & Data</h4>
    </div>
""", unsafe_allow_html=True)

# 1. Dataset File Path Input
default_dataset_path = "../[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"
dataset_path = st.sidebar.text_input("Candidate Database Path (.jsonl)", value=default_dataset_path)

# Let user upload a smaller sample file if they wish (Required by Sandbox Spec)
uploaded_file = st.sidebar.file_uploader("Or Upload Custom Candidate Sample (.jsonl)", type=["jsonl"])

# Limit candidates for UI performance toggle
limit_toggle = st.sidebar.checkbox("Limit analysis to first 10,000 candidates for speed", value=True)
load_limit = 10000 if limit_toggle else None

# Handle loading data
file_to_load = dataset_path
if uploaded_file:
    # Save uploaded file temporarily
    temp_path = "temp_uploaded_candidates.jsonl"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    file_to_load = temp_path

with st.spinner("Loading candidate database and scanning for traps..."):
    candidates_list, total_raw, total_hp, total_consulting = load_candidates(file_to_load, limit=load_limit)

if not candidates_list:
    st.error(f"Could not load candidates from path '{file_to_load}'. Please check the path or upload a file.")
    st.stop()

# 2. Interactive JD input
jd_text = st.sidebar.text_area("Target Job Description", value=DEFAULT_JD, height=250)

# 3. Interactive Filters
st.sidebar.markdown("""
    <div style="border-left: 3px solid #38BDF8; padding-left: 10px; margin: 1.5rem 0 0.8rem 0;">
        <h4 style="font-family: 'Outfit', sans-serif; font-weight: 700; color: #F3F4F6; margin: 0; font-size: 1rem; letter-spacing: 0.03em; text-transform: uppercase;">🎯 Candidate Filters</h4>
    </div>
""", unsafe_allow_html=True)
experience_range = st.sidebar.slider("Years of Experience", 0.0, 20.0, (5.0, 9.0), step=0.5)
max_notice_period = st.sidebar.slider("Max Notice Period (days)", 0, 180, 90, step=15)
only_relocate = st.sidebar.checkbox("Include only Noida/Pune or willing to relocate", value=True)

# Run Ranking Core
with st.spinner("Analyzing profiles and computing scores..."):
    # Rank candidates using our shared library
    ranked_candidates = ranker.rank_candidates(candidates_list)

# Filter ranked results based on slider controls (dynamic UI overrides)
filtered_ranked = []
for c in ranked_candidates:
    # Experience filter
    if not (experience_range[0] <= c["years_exp"] <= experience_range[1]):
        continue
    # Notice period filter
    notice = c["candidate_raw"].get("redrob_signals", {}).get("notice_period_days", 90)
    if notice > max_notice_period:
        continue
    # Relocation filter
    if only_relocate:
        location = c["location"].lower()
        is_pune_noida = any(l in location for l in ["pune", "noida", "gurgaon", "delhi", "ncr"])
        willing_relocate = c["candidate_raw"].get("redrob_signals", {}).get("willing_to_relocate", False)
        if not is_pune_noida and not willing_relocate:
            continue
            
    filtered_ranked.append(c)

# Layout Metrics Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Scanned Database</div><div class='metric-num'>{total_raw:,}</div><div class='metric-label'>Total Candidates</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Traps Defused</div><div class='metric-num' style='color: #EF4444;'>{total_hp:,}</div><div class='metric-label'>Honeypots Eliminated</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Consulting Filtered</div><div class='metric-num' style='color: #F59E0B;'>{total_consulting:,}</div><div class='metric-label'>Service Profiles Blocked</div></div>", unsafe_allow_html=True)
with m4:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Ranked Shortlist</div><div class='metric-num'>{len(filtered_ranked)}</div><div class='metric-label'>Matches After Filters</div></div>", unsafe_allow_html=True)

st.write("")
st.write("")

# Create Tabs
tab_list, tab_dive, tab_matcher, tab_traps = st.tabs(["📋 Candidate Shortlist", "🔍 Profile Deep Dive", "📄 Resume Matcher", "🛡️ Defused Traps Audit"])

# Tab 1: Shortlist
with tab_list:
    st.markdown("### Top Candidate Matches")
    st.write("Candidates are ranked by title relevance, skill envelopes, experience match, and availability signals.")
    
    if not filtered_ranked:
        st.warning("No candidates matched your filters. Try widening your experience or notice period criteria.")
    else:
        # Build dataframe for nice tabular display
        df_display = []
        for i, c in enumerate(filtered_ranked[:100]):
            signals = c["candidate_raw"].get("redrob_signals", {})
            df_display.append({
                "Rank": c["rank"],
                "ID": c["candidate_id"],
                "Name": c["name"],
                "Current Title": c["current_title"],
                "Current Company": c["current_company"],
                "Experience": f"{c['years_exp']:.1f} Yrs",
                "Location": c["location"],
                "Score": f"{c['score']:.3f}",
                "Notice Period": f"{signals.get('notice_period_days')} days",
                "Reasoning Summary": c["reasoning"]
            })
            
        st.dataframe(
            pd.DataFrame(df_display),
            use_container_width=True,
            column_config={
                "Rank": st.column_config.NumberColumn(width=60),
                "ID": st.column_config.TextColumn(width=100),
                "Score": st.column_config.TextColumn(width=80),
                "Notice Period": st.column_config.TextColumn(width=100),
                "Reasoning Summary": st.column_config.TextColumn(width=450),
            },
            hide_index=True
        )
        
        # Show Shortlist Analytics
        st.write("")
        st.markdown("### 📊 Shortlist Cohort Analytics")
        if filtered_ranked:
            top_100 = filtered_ranked[:100]
            avg_exp = np.mean([c["years_exp"] for c in top_100])
            avg_notice = np.mean([c["candidate_raw"].get("redrob_signals", {}).get("notice_period_days", 90) for c in top_100])
            
            # Count locations
            loc_counts = {}
            for c in top_100:
                loc = c["location"].split(",")[0].strip()
                loc_counts[loc] = loc_counts.get(loc, 0) + 1
                
            # Count top skills
            skill_counts = {}
            for c in top_100:
                for s in c["candidate_raw"].get("skills", []):
                    sname = s.get("name")
                    skill_counts[sname] = skill_counts.get(sname, 0) + 1
            sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:4]
            
            sa1, sa2, sa3 = st.columns([1, 1.2, 1.2])
            with sa1:
                avg_score = np.mean([c["score"] for c in top_100])
                st.markdown(f"<div style='margin-bottom: 1rem;'>💼 <b>Average Experience</b><br><span style='font-size: 1.5rem; font-weight: 700; color: #38BDF8;'>{avg_exp:.1f} Years</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='margin-bottom: 1rem;'>📅 <b>Average Notice Period</b><br><span style='font-size: 1.5rem; font-weight: 700; color: #38BDF8;'>{avg_notice:.1f} Days</span></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='margin-bottom: 1rem;'>📈 <b>Average Fit Score</b><br><span style='font-size: 1.5rem; font-weight: 700; color: #00E5FF;'>{avg_score:.3f}</span></div>", unsafe_allow_html=True)
            with sa2:
                st.markdown("**📍 Top Locations**")
                df_loc = pd.DataFrame(list(loc_counts.items()), columns=["Location", "Candidates"]).sort_values(by="Candidates", ascending=True).tail(5)
                fig_loc = px.bar(
                    df_loc, 
                    x="Candidates", 
                    y="Location", 
                    orientation="h",
                    color="Candidates",
                    color_continuous_scale=["#1E3A8A", "#38BDF8", "#00E5FF"],
                    text="Candidates"
                )
                fig_loc.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#F3F4F6",
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=200,
                    coloraxis_showscale=False,
                    xaxis=dict(showgrid=False, zeroline=False, visible=False),
                    yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=11))
                )
                fig_loc.update_traces(
                    textposition="inside",
                    marker_line_color="rgba(0,0,0,0)",
                    hovertemplate="<b>%{y}</b><br>Candidates: %{x}<extra></extra>"
                )
                st.plotly_chart(fig_loc, use_container_width=True, config={'displayModeBar': False})
            with sa3:
                st.markdown("**⚡ Core Skill Coverage**")
                df_skills = pd.DataFrame(sorted_skills, columns=["Skill", "Candidates"]).sort_values(by="Candidates", ascending=False)
                fig_skills = px.bar(
                    df_skills,
                    x="Skill",
                    y="Candidates",
                    color="Candidates",
                    color_continuous_scale=["#1E3A8A", "#38BDF8", "#00E5FF"],
                    text="Candidates"
                )
                fig_skills.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#F3F4F6",
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=200,
                    coloraxis_showscale=False,
                    yaxis=dict(showgrid=False, zeroline=False, visible=False),
                    xaxis=dict(showgrid=False, zeroline=False, tickangle=-15, tickfont=dict(size=11))
                )
                fig_skills.update_traces(
                    textposition="inside",
                    marker_line_color="rgba(0,0,0,0)",
                    hovertemplate="<b>%{x}</b><br>Candidates: %{y}<extra></extra>"
                )
                st.plotly_chart(fig_skills, use_container_width=True, config={'displayModeBar': False})
        st.write("")
        
        # Download Shortlist CSV Button
        # Create CSV text
        csv_data = "candidate_id,rank,score,reasoning\n"
        for c in ranked_candidates[:100]:
            csv_data += f"{c['candidate_id']},{c['rank']},{c['score']:.4f},\"{c['reasoning']}\"\n"
            
        st.download_button(
            label="💾 Download Validated Shortlist CSV",
            data=csv_data,
            file_name="team_submission.csv",
            mime="text/csv",
            help="Download the verified top-100 shortlist ready for portal submission."
        )

# Tab 2: Profile Deep Dive
with tab_dive:
    st.markdown("### Profile Inspection & Signals Audit")
    
    if not filtered_ranked:
        st.info("Please adjust filters to view matching profiles.")
    else:
        # Select box and Compare checkbox side-by-side
        col_select, col_compare = st.columns([2.2, 1.0])
        with col_select:
            c_names = [f"Rank {c['rank']}: {c['name']} ({c['candidate_id']})" for c in filtered_ranked[:100]]
            selected_index = st.selectbox("Select Candidate to Inspect:", range(len(c_names)), format_func=lambda x: c_names[x])
        with col_compare:
            st.write("") # spacing
            st.write("")
            compare_mode = st.checkbox("📊 Compare Candidates", value=False, help="Select and compare up to 3 candidates side-by-side.")
            
        if compare_mode:
            compare_selected = st.multiselect(
                "Select up to 3 candidates to compare:",
                options=range(len(c_names)),
                default=[selected_index],
                format_func=lambda x: c_names[x],
                max_selections=3
            )
            if len(compare_selected) < 2:
                st.info("Please select at least 2 candidates from the list to compare side-by-side.")
            else:
                st.write("---")
                cols = st.columns(len(compare_selected))
                comparison_data = []
                for idx, col_idx in enumerate(compare_selected):
                    comp_cand = filtered_ranked[col_idx]
                    comp_raw = comp_cand["candidate_raw"]
                    comp_profile = comp_raw.get("profile", {})
                    comp_signals = comp_raw.get("redrob_signals", {})
                    
                    t_score = ranker.calculate_title_score(comp_raw)
                    s_score = ranker.calculate_skill_score(comp_raw)
                    availability_mult = ranker.calculate_availability_multiplier(comp_raw)
                    
                    comparison_data.append({
                        "Candidate": comp_cand["name"],
                        "Title Fit (40%)": t_score * 0.4,
                        "Skills Fit (30%)": s_score * 0.3,
                        "Availability Index": availability_mult * 0.5,
                        "Overall Score": comp_cand["score"]
                    })
                    
                    with cols[idx]:
                        st.markdown(f"### Rank {comp_cand['rank']}: {comp_cand['name']}")
                        st.write(f"**ID**: `{comp_cand['candidate_id']}`")
                        st.write(f"**Current Title**: {comp_cand['current_title']}")
                        st.write(f"**Current Company**: {comp_cand['current_company']}")
                        st.write(f"💼 **Experience**: {comp_cand['years_exp']:.1f} Years")
                        st.write(f"📍 **Location**: {comp_cand['location']}")
                        
                        st.markdown(f"""
                            <div style="text-align: center; margin: 1rem 0; padding: 0.75rem; border-radius: 12px; background: rgba(56, 189, 248, 0.05); border: 1px solid rgba(56, 189, 248, 0.25);">
                                <div style="font-size: 0.75rem; color:#9CA3AF; letter-spacing:0.05em; font-weight:600;">FIT SCORE</div>
                                <div style="font-size: 1.8rem; font-weight: 800; color: #00E5FF; text-shadow: 0 0 10px rgba(0, 229, 255, 0.3);">{comp_cand['score']:.3f}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        skills_list = [s.get("name") for s in comp_raw.get("skills", [])][:5]
                        skills_str = ", ".join(skills_list) if skills_list else "None listed"
                        st.write(f"⚡ **Top Skills**: {skills_str}")
                        
                        notice_days = comp_signals.get("notice_period_days", 90)
                        otw_status = "🟢 Available" if comp_signals.get("open_to_work_flag", False) else "⚪ Passive"
                        st.write(f"📅 **Notice**: {notice_days} days ({otw_status})")
                        st.write(f"💬 **Response Rate**: {comp_signals.get('recruiter_response_rate', 0.0)*100:.0f}%")
                        
                        st.write("---")
                        st.markdown("**AI Fit Analysis:**")
                        st.markdown(f"<div class='reasoning-box'>{comp_cand['reasoning']}</div>", unsafe_allow_html=True)
                        
                st.write("")
                st.markdown("### 📊 Fit Component Comparison")
                df_comp = pd.DataFrame(comparison_data)
                fig_comp = px.bar(
                    df_comp,
                    x="Candidate",
                    y=["Title Fit (40%)", "Skills Fit (30%)", "Availability Index", "Overall Score"],
                    barmode="group",
                    color_discrete_sequence=["#1E3A8A", "#38BDF8", "#00E5FF", "#FBBF24"]
                )
                fig_comp.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#F3F4F6",
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=300,
                    xaxis=dict(showgrid=False, title=""),
                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Component Scores"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})
        else:
            cand_data = filtered_ranked[selected_index]
            cand_raw = cand_data["candidate_raw"]
            profile = cand_raw.get("profile", {})
            signals = cand_raw.get("redrob_signals", {})
            
            st.write("---")
            
            c1, c2 = st.columns([1.8, 1.2])
            
            with c1:
                st.markdown(f"## {profile.get('anonymized_name')}")
                st.markdown(f"**Headline**: {profile.get('headline')}")
                st.write(f"📍 **Location**: {profile.get('location')}, {profile.get('country')} | 💼 **Experience**: {profile.get('years_of_experience')} Years")
                
                # Recruiter reasoning
                st.markdown("#### AI Recruiter Fit Analysis")
                st.markdown(f"<div class='reasoning-box'>{cand_data['reasoning']}</div>", unsafe_allow_html=True)
                
                # Career History Timeline
                st.markdown("#### Professional Timeline")
                for job in cand_raw.get("career_history", []):
                    start = job.get("start_date", "N/A")
                    end = job.get("end_date") or "Present"
                    dur = job.get("duration_months", 0)
                    
                    st.markdown(f"""
                        <div class='timeline-card'>
                            <div class='timeline-dot'></div>
                            <div class='timeline-company'>{job.get('company')} <span style='font-size:0.8rem; color:#9CA3AF;'>({job.get('company_size')} employees)</span></div>
                            <div class='timeline-title'>{job.get('title')}</div>
                            <div class='timeline-dates'>{start} to {end} ({dur} months) | Industry: {job.get('industry')}</div>
                            <p style='margin-top:0.5rem; font-size:0.9rem; color:#D1D5DB;'>{job.get('description')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                # Education Timeline
                st.markdown("#### Education")
                for edu in cand_raw.get("education", []):
                    tier_badge = f"<span style='color:#3B82F6;'>[{edu.get('tier', 'unknown').upper()}]</span>"
                    st.markdown(f"""
                        <div class='timeline-card' style='border-left-color: #3B82F6;'>
                            <div class='timeline-dot' style='background-color: #3B82F6;'></div>
                            <div class='timeline-company'>{edu.get('institution')} {tier_badge}</div>
                            <div class='timeline-title'>{edu.get('degree')} in {edu.get('field_of_study')}</div>
                            <div class='timeline-dates'>{edu.get('start_year')} - {edu.get('end_year')} | Grade: {edu.get('grade')}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
            with c2:
                st.markdown("### Platform Availability Envelope")
                
                # Custom neon styled availability badges
                otw = signals.get("open_to_work_flag", False)
                if otw:
                    otw_badge = '<span class="badge badge-green"><span class="pulse-active"></span>Active Open-To-Work</span>'
                else:
                    otw_badge = '<span class="badge badge-yellow">Passive Searcher</span>'
                    
                rrr = signals.get("recruiter_response_rate", 0.0)
                if rrr >= 0.7:
                    rrr_badge = f'<span class="badge badge-green">{rrr*100:.0f}% Response Rate</span>'
                elif rrr >= 0.4:
                    rrr_badge = f'<span class="badge badge-yellow">{rrr*100:.0f}% Response Rate</span>'
                else:
                    rrr_badge = f'<span class="badge badge-red">{rrr*100:.0f}% Response Rate</span>'
                    
                notice = signals.get("notice_period_days", 90)
                if notice <= 30:
                    notice_badge = f'<span class="badge badge-green">{notice}d Notice Period</span>'
                elif notice <= 60:
                    notice_badge = f'<span class="badge badge-yellow">{notice}d Notice Period</span>'
                else:
                    notice_badge = f'<span class="badge badge-red">{notice}d Notice Period</span>'
                    
                last_active = signals.get("last_active_date", "")
                active_days = 999
                if last_active:
                    active_date = ranker.parse_date(last_active)
                    if active_date:
                        active_days = (ranker.CURRENT_REF_DATE - active_date).days
                
                if active_days <= 30:
                    active_badge = f'<span class="badge badge-green">Active {active_days}d ago</span>'
                elif active_days <= 90:
                    active_badge = f'<span class="badge badge-yellow">Active {active_days}d ago</span>'
                else:
                    active_badge = f'<span class="badge badge-red">Inactive {active_days}d ago</span>'
                    
                email_badge = '<span class="badge badge-blue">📧 Email Verified</span>' if signals.get("verified_email") else '<span class="badge badge-red">📧 Email Unverified</span>'
                phone_badge = '<span class="badge badge-blue">📱 Phone Verified</span>' if signals.get("verified_phone") else '<span class="badge badge-red">📱 Phone Unverified</span>'
                github_badge = f'<span class="badge badge-blue">💻 GitHub Score: {signals.get("github_activity_score", 0)}/100</span>'
                
                st.markdown(f"""
                    <div style="margin-bottom: 1.5rem;">
                        <p style="font-weight: 600; color: #9CA3AF; margin-bottom: 0.5rem;">Candidate Signals:</p>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            {otw_badge}
                            {notice_badge}
                            {rrr_badge}
                            {active_badge}
                            {email_badge}
                            {phone_badge}
                            {github_badge}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.write("---")
                
                st.markdown("### Skill Set & Experience Duration")
                skills_data = []
                for s in cand_raw.get("skills", []):
                    skills_data.append({
                        "Skill": s.get("name"),
                        "Proficiency": s.get("proficiency").capitalize(),
                        "Months": s.get("duration_months", 0),
                        "Endorsements": s.get("endorsements", 0)
                    })
                
                if skills_data:
                    df_skills = pd.DataFrame(skills_data)
                    df_skills = df_skills.sort_values(by="Months", ascending=True)
                    
                    color_map = {
                        "Expert": "#00E5FF",
                        "Advanced": "#38BDF8",
                        "Intermediate": "#1E3A8A",
                        "Beginner": "#1E293B"
                    }
                    
                    fig_skills = px.bar(
                        df_skills,
                        x="Months",
                        y="Skill",
                        orientation="h",
                        color="Proficiency",
                        color_discrete_map=color_map,
                        hover_data=["Proficiency", "Endorsements"],
                        text="Months"
                    )
                    fig_skills.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font_color="#F3F4F6",
                        margin=dict(l=10, r=10, t=10, b=10),
                        height=max(200, len(skills_data) * 32),
                        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", title="Experience (Months)"),
                        yaxis=dict(showgrid=False, title="", tickfont=dict(size=11)),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    fig_skills.update_traces(
                        textposition="inside",
                        marker_line_color="rgba(0,0,0,0)",
                        hovertemplate="<b>%{y}</b><br>Experience: %{x} months<br>Proficiency: %{customdata[0]}<br>Endorsements: %{customdata[1]}<extra></extra>"
                    )
                    st.plotly_chart(fig_skills, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.write("No skills listed.")

# Tab 3: Resume Matcher
with tab_matcher:
    st.markdown("### Candidate Resume Matching Sandpit")
    st.write("Upload a PDF/TXT resume description to calculate raw matching score and highlight missing requirements.")
    
    # PDF/TXT Resume uploader
    uploaded_resume = st.file_uploader("Upload Candidate Resume (PDF or TXT):", type=["pdf", "txt"])
    
    resume_text = ""
    if uploaded_resume:
        if uploaded_resume.name.endswith(".pdf"):
            try:
                from pypdf import PdfReader
                reader = PdfReader(uploaded_resume)
                text_parts = []
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_parts.append(extracted)
                resume_text = "\n".join(text_parts)
                st.success("Successfully extracted text from uploaded PDF resume!")
            except Exception as e:
                st.error(f"Error parsing PDF file: {e}. Please try another file or copy-paste the text.")
        else:
            try:
                resume_text = uploaded_resume.getvalue().decode("utf-8")
                st.success("Successfully loaded TXT resume!")
            except Exception as e:
                st.error(f"Error reading TXT file: {e}")
                
    resume_text = st.text_area(
        "Or Paste/Edit Resume Text Here:",
        value=resume_text,
        placeholder="Paste candidates CV content, skills, and experiences here...",
        height=200
    )
    
    if st.button("Analyze Resume Match"):
        if not resume_text:
            st.warning("Please upload a file or paste some text first.")
        else:
            resume_lower = resume_text.lower()
            
            # Extract skills and check relevance
            vectordb_skills = {"pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss"}
            retrieval_skills = {"sentence-transformers", "embeddings", "bge", "e5", "nlp", "information retrieval", "retrieval"}
            eval_skills = {"ndcg", "mrr", "map", "evaluation", "metrics"}
            
            matched_vdb = [s for s in vectordb_skills if s in resume_lower]
            matched_ret = [s for s in retrieval_skills if s in resume_lower]
            matched_eval = [s for s in eval_skills if s in resume_lower]
            
            score = 0.0
            if matched_vdb: score += 0.35
            if matched_ret: score += 0.35
            if matched_eval: score += 0.2
            if "python" in resume_lower: score += 0.1
            
            # Render layout columns
            g1, g2 = st.columns([1.2, 1.8])
            
            with g1:
                # Speedometer Gauge Chart using go.Indicator
                import plotly.graph_objects as go
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Match Suitability %", 'font': {'size': 15, 'color': '#9CA3AF'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#F3F4F6"},
                        'bar': {'color': "#00E5FF"},
                        'bgcolor': "rgba(30, 41, 59, 0.5)",
                        'borderwidth': 1,
                        'bordercolor': "rgba(56, 189, 248, 0.3)",
                        'steps': [
                            {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.1)'},
                            {'range': [40, 75], 'color': 'rgba(245, 158, 11, 0.1)'},
                            {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
                        ],
                        'threshold': {
                            'line': {'color': "#38BDF8", 'width': 3},
                            'thickness': 0.75,
                            'value': 75
                        }
                    }
                ))
                fig_gauge.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#F3F4F6",
                    height=200,
                    margin=dict(l=10, r=10, t=30, b=10)
                )
                st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
                
            with g2:
                # Skill breakdown
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.success("#### Found Skills")
                    st.write(f"**Vector DBs**: {', '.join(matched_vdb) if matched_vdb else 'None'}")
                    st.write(f"**Retrieval**: {', '.join(matched_ret) if matched_ret else 'None'}")
                    st.write(f"**Evaluation**: {', '.join(matched_eval) if matched_eval else 'None'}")
                    st.write(f"**Python**: {'Yes' if 'python' in resume_lower else 'No'}")
                with sc2:
                    st.error("#### Gaps / Missing Focus")
                    missing_vdb = vectordb_skills - set(matched_vdb)
                    missing_eval = eval_skills - set(matched_eval)
                    
                    st.write(f"**Missing Vector DBs**: {', '.join(list(missing_vdb)[:3]) if missing_vdb else 'None'}")
                    st.write(f"**Missing Eval Metrics**: {', '.join(list(missing_eval)[:3]) if missing_eval else 'None'}")
            
            st.write("---")
            st.info("Note: This sandpit calculates a zero-shot keyword match similarity score. Real candidate profiles from the pool also incorporate platform activity history (notice periods, response rate, etc.) which optimizes the final ranking.")

# Tab 4: Defused Traps Audit
with tab_traps:
    st.markdown("### 🛡️ Programmatic Trap Filtering Audit Log")
    st.write("Our AI Engine runs multiple physical and logical consistency audits to catch honeypot trap accounts and IT services consulting profiles.")
    
    # Check for honeypot count stats
    # Let's count trap types
    trap_counts = {
        "Date Conflict (Signup > Active)": 0,
        "Skill Duration Mismatch (Skill > Exp)": 0,
        "Proficiency Contradiction (Expert with 0 mo)": 0,
        "Timeline Contradiction (Job pre-founding)": 0,
        "Job Duration Mismatch (Job > Comp age)": 0,
        "IT Consulting Entire Career": 0
    }
    
    caught_details = []
    
    # Let's scan candidates to classify traps
    for cand in candidates_list:
        # check consulting
        is_c = ranker.is_consulting_only(cand)
        hp, hp_reason = ranker.is_honeypot(cand)
        
        if hp:
            # Identify sub-reason
            signals = cand.get("redrob_signals", {})
            signup = ranker.parse_date(signals.get("signup_date"))
            active = ranker.parse_date(signals.get("last_active_date"))
            profile = cand.get("profile", {})
            years_exp = profile.get("years_of_experience", 0)
            
            if signup and active and signup > active:
                trap_counts["Date Conflict (Signup > Active)"] += 1
            
            skills_mismatch = False
            expert_zero = False
            for s in cand.get("skills", []):
                dur_years = s.get("duration_months", 0) / 12.0
                if dur_years > years_exp + 0.5:
                    skills_mismatch = True
                if s.get("proficiency") in ["expert", "advanced"] and s.get("duration_months", 0) == 0:
                    expert_zero = True
                    
            if skills_mismatch:
                trap_counts["Skill Duration Mismatch (Skill > Exp)"] += 1
            if expert_zero:
                trap_counts["Proficiency Contradiction (Expert with 0 mo)"] += 1
                
            timeline_pre = False
            timeline_dur = False
            career = cand.get("career_history", [])
            for job in career:
                comp = job.get("company", "")
                if comp in ranker.FOUNDING_YEARS:
                    f_year = ranker.FOUNDING_YEARS[comp]
                    start_str = job.get("start_date")
                    if start_str:
                        try:
                            start_year = int(start_str.split("-")[0])
                            if start_year < f_year:
                                timeline_pre = True
                        except:
                            pass
                    dur_years = job.get("duration_months", 0) / 12.0
                    max_dur = ranker.CURRENT_REF_DATE.year - f_year
                    if dur_years > max_dur:
                        timeline_dur = True
                        
            if timeline_pre:
                trap_counts["Timeline Contradiction (Job pre-founding)"] += 1
            if timeline_dur:
                trap_counts["Job Duration Mismatch (Job > Comp age)"] += 1
                
            if not (signup and active and signup > active) and not skills_mismatch and not expert_zero and not timeline_pre and not timeline_dur:
                trap_counts["Timeline Contradiction (Job pre-founding)"] += 1
                
            if len(caught_details) < 50:
                caught_details.append({
                    "ID": cand["candidate_id"],
                    "Name": profile.get("anonymized_name", "Anonymous"),
                    "Type": "Honeypot Account",
                    "Reason": hp_reason
                })
        elif is_c:
            trap_counts["IT Consulting Entire Career"] += 1
            if len(caught_details) < 50:
                caught_details.append({
                    "ID": cand["candidate_id"],
                    "Name": cand.get("profile", {}).get("anonymized_name", "Anonymous"),
                    "Type": "Consulting Filter",
                    "Reason": "Entire career spent at IT consulting/services firms (disallowed by JD)."
                })
                
    # Display breakdown pie chart
    t_cols = st.columns([1.2, 1.8])
    with t_cols[0]:
        st.markdown("#### Trap Category Distribution")
        non_zero_traps = {k: v for k, v in trap_counts.items() if v > 0}
        if non_zero_traps:
            df_traps = pd.DataFrame(list(non_zero_traps.items()), columns=["Category", "Blocked Profiles"])
            fig_traps = px.pie(
                df_traps,
                names="Category",
                values="Blocked Profiles",
                hole=0.4,
                color_discrete_sequence=["#EF4444", "#F59E0B", "#38BDF8", "#00E5FF", "#1E3A8A", "#4B5563"]
            )
            fig_traps.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#F3F4F6",
                margin=dict(l=10, r=10, t=10, b=10),
                height=250,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_traps, use_container_width=True, config={'displayModeBar': False})
        else:
            st.write("No threats recorded.")
            
    with t_cols[1]:
        st.markdown("#### Real-time Threats Defused Audit Log")
        st.write("Flagged profiles caught by the Redrob Recruiter system:")
        df_caught = pd.DataFrame(caught_details)
        if not df_caught.empty:
            st.dataframe(
                df_caught,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.TextColumn(width=100),
                    "Name": st.column_config.TextColumn(width=120),
                    "Type": st.column_config.TextColumn(width=120),
                    "Reason": st.column_config.TextColumn(width=300),
                }
            )
        else:
            st.write("No defused traps in sample.")
