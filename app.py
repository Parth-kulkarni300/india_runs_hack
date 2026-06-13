import streamlit as st
import json
import os
import pandas as pd
import numpy as np
import ranker
from pathlib import Path

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
        
        /* Global Streamlit elements overrides */
        .stApp {
            background-color: #0B0E14;
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
            box-shadow: 0 12px 40px 0 rgba(0, 229, 255, 0.15);
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
st.sidebar.image("https://img.icons8.com/clouds/200/brain.png", width=100)
st.sidebar.markdown("### Configuration & Input")

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
st.sidebar.markdown("### Candidate Profile Filters")
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
tab_list, tab_dive, tab_matcher = st.tabs(["📋 Candidate Shortlist", "🔍 Profile Deep Dive", "📄 Resume Matcher"])

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
        # Dropdown selection of candidates
        c_names = [f"Rank {c['rank']}: {c['name']} ({c['candidate_id']})" for c in filtered_ranked[:100]]
        selected_index = st.selectbox("Select Candidate to Inspect:", range(len(c_names)), format_func=lambda x: c_names[x])
        
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
            
            # Color-coded signals dashboard
            # Open to work
            otw = signals.get("open_to_work_flag", False)
            otw_color = "🟢 Available" if otw else "⚪ Passive"
            
            # Response rate
            rrr = signals.get("recruiter_response_rate", 0.0)
            rrr_color = "🟢 Excellent" if rrr >= 0.7 else ("🟡 Medium" if rrr >= 0.4 else "🔴 Low")
            
            # Notice Period
            notice = signals.get("notice_period_days", 90)
            notice_color = "🟢 Short" if notice <= 30 else ("🟡 Standard" if notice <= 60 else "🔴 Long")
            
            # Activity recency
            last_active = signals.get("last_active_date", "")
            active_days = 999
            if last_active:
                active_date = ranker.parse_date(last_active)
                if active_date:
                    active_days = (ranker.CURRENT_REF_DATE - active_date).days
            
            active_color = "🟢 Active Recently" if active_days <= 30 else ("🟡 Inactive" if active_days <= 180 else "🔴 Dormant")
            
            st.markdown(f"""
                **Availability Indicators**:
                - Status: **{otw_color}**
                - Notice Period: **{notice} days** ({notice_color})
                - Recruiter Response Rate: **{rrr*100:.0f}%** ({rrr_color})
                - Last Active: **{last_active}** ({active_color}, {active_days} days ago)
                - Email Verified: {"✅ Yes" if signals.get("verified_email") else "❌ No"}
                - Phone Verified: {"✅ Yes" if signals.get("verified_phone") else "❌ No"}
                - GitHub Score: **{signals.get("github_activity_score")}/100**
            """)
            
            st.write("---")
            
            st.markdown("### Skill Set & Experience Duration")
            skills_data = []
            for s in cand_raw.get("skills", []):
                skills_data.append({
                    "Skill": s.get("name"),
                    "Proficiency": s.get("proficiency").capitalize(),
                    "Months": s.get("duration_months"),
                    "Endorsements": s.get("endorsements")
                })
            
            if skills_data:
                df_skills = pd.DataFrame(skills_data)
                # Sort by months
                df_skills = df_skills.sort_values(by="Months", ascending=False)
                st.dataframe(df_skills, use_container_width=True, hide_index=True)
            else:
                st.write("No skills listed.")

# Tab 3: Resume Matcher
with tab_matcher:
    st.markdown("### Candidate Resume Matching Sandpit")
    st.write("Upload a plain-text resume description to calculate raw matching score and highlight missing requirements.")
    
    resume_text = st.text_area("Paste Resume Text Here:", placeholder="Paste candidates CV content, skills, and experiences here...", height=200)
    
    if st.button("Analyze Resume Match"):
        if not resume_text:
            st.warning("Please paste some text first.")
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
            
            st.markdown(f"## Match Fit Score: `{score*100:.0f}%`")
            
            c1, c2 = st.columns(2)
            with c1:
                st.success("### Found Skills")
                st.write(f"**Vector DBs**: {', '.join(matched_vdb) if matched_vdb else 'None'}")
                st.write(f"**Retrieval**: {', '.join(matched_ret) if matched_ret else 'None'}")
                st.write(f"**Evaluation**: {', '.join(matched_eval) if matched_eval else 'None'}")
                st.write(f"**Python**: {'Yes' if 'python' in resume_lower else 'No'}")
            with c2:
                st.error("### Gaps / Missing Focus")
                missing_vdb = vectordb_skills - set(matched_vdb)
                missing_eval = eval_skills - set(matched_eval)
                
                st.write(f"**Missing Vector DBs**: {', '.join(list(missing_vdb)[:3])}")
                st.write(f"**Missing Eval Metrics**: {', '.join(list(missing_eval)[:3])}")
                
            st.write("---")
            st.info("Note: This sandpit calculates a zero-shot keyword match similarity score. Real candidate profiles from the pool also incorporate platform activity history (notice periods, response rate, etc.) which optimizes the final ranking.")
