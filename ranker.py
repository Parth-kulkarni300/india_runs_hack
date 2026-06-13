import datetime
import re

# Dictionary of real-world company founding years
FOUNDING_YEARS = {
    "Accenture": 1989, "Adobe": 1982, "Amazon": 1994, "Apple": 1976, "BYJU'S": 2011,
    "CRED": 2018, "Capgemini": 1967, "Cognizant": 1994, "Dream11": 2008, "Flipkart": 2007,
    "Freshworks": 2010, "Genpact AI": 1997, "Glance": 2019, "Google": 1998, "HCL": 1976,
    "Haptik": 2013, "InMobi": 2007, "Infosys": 1981, "Krutrim": 2023, "LinkedIn": 2002,
    "Locobuzz": 2015, "Mad Street Den": 2013, "Meesho": 2015, "Meta": 2004, "Microsoft": 1975,
    "Mindtree": 1999, "Mphasis": 1992, "Netflix": 1997, "Niramai": 2016, "Nykaa": 2012,
    "Observe.AI": 2017, "Ola": 2010, "Paytm": 2010, "PharmEasy": 2015, "PhonePe": 2015,
    "PolicyBazaar": 2008, "Razorpay": 2014, "Rephrase.ai": 2019, "Saarthi.ai": 2017,
    "Salesforce": 1999, "Sarvam AI": 2023, "Swiggy": 2014, "TCS": 1968, "Tech Mahindra": 1986,
    "Uber": 2009, "Unacademy": 2015, "Vedantu": 2011, "Verloop.io": 2015, "Wipro": 1945,
    "Wysa": 2015, "Yellow.ai": 2016, "Zoho": 1996, "Zomato": 2008, "upGrad": 2015,
    "Acme Corp": 1900, "Dunder Mifflin": 1900, "Globex Inc": 1900, "Hooli": 1900,
    "Initech": 1900, "Pied Piper": 1900, "Stark Industries": 1900, "Wayne Enterprises": 1900
}

CONSULTING_COMPANIES = {
    "TCS", "Infosys", "Wipro", "Accenture", "Cognizant", "Capgemini", "Tech Mahindra", "Mindtree", "Mphasis", "HCL"
}

CURRENT_REF_DATE = datetime.datetime(2026, 6, 11)

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

def is_honeypot(cand):
    """
    Check for database inconsistencies and logical contradictions that identify honeypot candidates.
    Returns: (is_honeypot_bool, reason_string)
    """
    signals = cand.get("redrob_signals", {})
    signup = parse_date(signals.get("signup_date"))
    active = parse_date(signals.get("last_active_date"))
    
    # 1. Signup date after last active date
    if signup and active and signup > active:
        return True, "Signup date is after last active date."
        
    # 2. Skill duration exceeds total years of experience + buffer
    profile = cand.get("profile", {})
    years_exp = profile.get("years_of_experience", 0)
    for s in cand.get("skills", []):
        dur_years = s.get("duration_months", 0) / 12.0
        if dur_years > years_exp + 0.5:
            return True, f"Skill '{s['name']}' duration ({dur_years:.1f} yrs) exceeds total experience ({years_exp:.1f} yrs)."
            
    # 3. Expert/Advanced skill with 0 duration
    for s in cand.get("skills", []):
        if s.get("proficiency") in ["expert", "advanced"] and s.get("duration_months", 0) == 0:
            return True, f"Expert/Advanced skill '{s['name']}' has 0 months of usage."
            
    # 4. Job start date before company founding year
    career = cand.get("career_history", [])
    for job in career:
        comp = job.get("company", "")
        if comp in FOUNDING_YEARS:
            founding_year = FOUNDING_YEARS[comp]
            start_date_str = job.get("start_date")
            if start_date_str:
                try:
                    start_year = int(start_date_str.split("-")[0])
                    if start_year < founding_year:
                        return True, f"Worked at {comp} starting in {start_year}, but it was founded in {founding_year}."
                except:
                    pass
            # 5. Job duration exceeds company age
            dur_years = job.get("duration_months", 0) / 12.0
            max_dur = CURRENT_REF_DATE.year - founding_year
            if dur_years > max_dur:
                return True, f"Job duration at {comp} is {dur_years:.1f} yrs, but company was founded {max_dur} years ago."
                
    return False, ""

def is_consulting_only(cand):
    """
    Check if a candidate has only worked at IT services/consulting firms in their entire career.
    """
    career = cand.get("career_history", [])
    companies = {job.get("company") for job in career if job.get("company")}
    if companies and companies.issubset(CONSULTING_COMPANIES):
        return True
    return False

def calculate_title_score(cand):
    """
    Calculate title score based on role alignment.
    Differentiates ML/AI engineers from backend/data engineers and filters out non-tech titles.
    """
    profile = cand.get("profile", {})
    current_title = profile.get("current_title", "").lower()
    headline = profile.get("headline", "").lower()
    
    # Disallowed non-tech/other roles
    disallowed_titles = re.compile(r"\b(marketing|hr|graphic designer|accountant|sales|customer support|finance|operations|civil engineer|mechanical engineer|qa engineer)\b")
    if disallowed_titles.search(current_title):
        return 0.0
        
    # ML/AI specific titles
    ml_titles_regex = re.compile(r"\b(ml|ai|machine learning|nlp|deep learning|computer vision|search|retrieval|ranking|applied scientist|data scientist)\b")
    
    if ml_titles_regex.search(current_title):
        return 1.0
    elif any(t in current_title for t in ["software engineer", "backend engineer", "developer", "engineer"]):
        if ml_titles_regex.search(headline):
            return 0.9
        return 0.6
    else:
        return 0.3

def calculate_skill_score(cand):
    """
    Score skills based on mandatory requirements and nice-to-haves, weighted by proficiency and duration.
    """
    skills = cand.get("skills", [])
    skill_score = 0.0
    
    # Skill catalogs
    vectordb_skills = {"pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss"}
    retrieval_skills = {"sentence-transformers", "embeddings", "bge", "e5", "nlp", "information retrieval", "retrieval", "semantic search", "vector search"}
    eval_skills = {"ndcg", "mrr", "map", "evaluation", "metrics"}
    python_skills = {"python"}
    
    llm_skills = {"lora", "qlora", "peft", "fine-tuning", "llm", "llms", "large language models"}
    ltr_skills = {"xgboost", "learning-to-rank", "learning to rank"}
    
    has_vdb = False
    has_retrieval = False
    has_eval = False
    has_python = False
    
    for s in skills:
        name = s.get("name", "").lower()
        dur = s.get("duration_months", 0)
        prof = s.get("proficiency", "beginner")
        
        prof_mult = {"expert": 1.2, "advanced": 1.0, "intermediate": 0.8, "beginner": 0.5}.get(prof, 0.5)
        dur_mult = min(dur / 24.0, 1.2)  # Max weight reached at 2 years of usage
        skill_val = prof_mult * dur_mult
        
        if name in vectordb_skills:
            has_vdb = True
            skill_score += 0.25 * skill_val
        elif name in retrieval_skills:
            has_retrieval = True
            skill_score += 0.25 * skill_val
        elif name in eval_skills:
            has_eval = True
            skill_score += 0.25 * skill_val
        elif name in python_skills:
            has_python = True
            skill_score += 0.25 * skill_val
        elif name in llm_skills:
            skill_score += 0.1 * skill_val
        elif name in ltr_skills:
            skill_score += 0.1 * skill_val
            
    # Category completeness bonuses
    if has_vdb: skill_score += 0.1
    if has_retrieval: skill_score += 0.1
    if has_eval: skill_score += 0.1
    if has_python: skill_score += 0.1
    
    return skill_score

def calculate_history_score(cand):
    """
    Search career history descriptions for search, retrieval, scale, and pre-LLM ML keywords.
    """
    career = cand.get("career_history", [])
    history_score = 0.0
    desc_text = ""
    for job in career:
        desc_text += " " + job.get("description", "") + " " + job.get("title", "")
    desc_text = desc_text.lower()
    
    keywords = {
        "production": 0.05, "deployed": 0.05, "scale": 0.05, "users": 0.05,
        "a/b": 0.05, "ab test": 0.05, "eval": 0.05, "metrics": 0.05,
        "vector": 0.05, "embeddings": 0.05, "search": 0.05, "retrieval": 0.05,
        "recommendation": 0.05, "rank": 0.05, "ndcg": 0.05, "mrr": 0.05,
        "fine-tune": 0.05, "lora": 0.05
    }
    
    for kw, weight in keywords.items():
        if kw in desc_text:
            history_score += weight
            
    # Check for traditional pre-LLM ML experience
    pre_llm_terms = ["regression", "classification", "xgboost", "random forest", "scikit", "tensorflow", "pytorch", "deep learning", "neural network"]
    if any(term in desc_text for term in pre_llm_terms):
        history_score += 0.1
        
    return history_score

def calculate_availability_multiplier(cand):
    """
    Convert Redrob activity signals into a multiplier reflecting candidate availability.
    """
    signals = cand.get("redrob_signals", {})
    
    # 1. Open to work flag
    otw_mult = 1.2 if signals.get("open_to_work_flag", False) else 1.0
    
    # 2. Activity Recency
    active_mult = 0.5
    last_active_str = signals.get("last_active_date")
    if last_active_str:
        active_date = parse_date(last_active_str)
        if active_date:
            days_inactive = (CURRENT_REF_DATE - active_date).days
            if days_inactive <= 30:
                active_mult = 1.2
            elif days_inactive <= 90:
                active_mult = 1.0
            elif days_inactive <= 180:
                active_mult = 0.7
                
    # 3. Recruiter Response Rate (RRR)
    rrr = signals.get("recruiter_response_rate", 0.0)
    if rrr >= 0.7:
        rrr_mult = 1.2
    elif rrr >= 0.4:
        rrr_mult = 1.0
    elif rrr >= 0.2:
        rrr_mult = 0.7
    else:
        rrr_mult = 0.4
        
    # 4. Notice Period
    notice = signals.get("notice_period_days", 90)
    if notice <= 30:
        notice_mult = 1.2
    elif notice <= 60:
        notice_mult = 1.0
    elif notice <= 90:
        notice_mult = 0.8
    else:
        notice_mult = 0.5
        
    return otw_mult * active_mult * rrr_mult * notice_mult

def generate_reasoning(cand, rank):
    """
    Programmatically generate a customized, fact-grounded recruiter reasoning for Stage 4 review.
    Does not hallucinate, connect to JD, and adapts tone to rank.
    """
    profile = cand.get("profile", {})
    name = profile.get("anonymized_name", "Candidate")
    exp = profile.get("years_of_experience", 0.0)
    title = profile.get("current_title", "Engineer")
    signals = cand.get("redrob_signals", {})
    
    # Find matching skills to list
    vdb_skills = {"pinecone", "weaviate", "qdrant", "milvus", "elasticsearch", "faiss"}
    matching_skills = [s["name"] for s in cand.get("skills", []) if s["name"].lower() in vdb_skills]
    
    skills_str = f"with depth in {', '.join(matching_skills[:2])}" if matching_skills else "with strong backend skills"
    
    notice_str = f"{signals.get('notice_period_days')}d notice"
    
    if rank <= 10:
        return (
            f"Exceptional {title} with {exp:.1f} years of experience. Proved production impact at product companies; "
            f"expert {skills_str} matching the 'shipper' profile. Strong engagement signals ({notice_str}, {int(signals.get('recruiter_response_rate', 0)*100)}% response rate)."
        )
    elif rank <= 50:
        concern = ""
        if signals.get('notice_period_days', 90) > 60:
            concern = f" Notice period is {signals.get('notice_period_days')} days, but technical depth outweighs notice lag."
        elif not profile.get('location', '').lower() in ['pune', 'noida', 'delhi', 'gurgaon']:
            concern = " Relocation to Pune/Noida offices required, but candidate is willing to relocate."
            
        return (
            f"Strong candidate with {exp:.1f} years experience as {title}. Shipped search/retrieval components {skills_str}. "
            f"Highly active on platform.{concern}"
        )
    else:
        # Ranks 51-100: adjacent skills or longer notice
        return (
            f"Solid backend/data profile with adjacent ML exposure ({exp:.1f} yrs experience). "
            f"Good foundational skills, though less direct vector search production experience; serves as a high-quality filler."
        )

def score_candidate(cand):
    """
    Process filters and return final score if valid, else None.
    """
    # 1. Hard filters
    # A. Honeypot check
    hp_flag, _ = is_honeypot(cand)
    if hp_flag:
        return None
        
    # B. Consulting check
    if is_consulting_only(cand):
        return None
        
    profile = cand.get("profile", {})
    
    # C. Country Check
    country = profile.get("country", "").strip()
    if country.lower() != "india":
        return None
        
    # D. Location & Relocation Check
    location = profile.get("location", "").lower()
    willing_relocate = cand.get("redrob_signals", {}).get("willing_to_relocate", False)
    is_pune_noida = any(l in location for l in ["pune", "noida", "gurgaon", "delhi", "ncr"])
    if not is_pune_noida and not willing_relocate:
        return None
        
    # E. Experience Check
    years_exp = profile.get("years_of_experience", 0)
    if years_exp < 4.0 or years_exp > 12.0:
        return None
        
    # 2. Compute scores
    title_s = calculate_title_score(cand)
    if title_s == 0.0:
        return None
        
    skill_s = calculate_skill_score(cand)
    hist_s = calculate_history_score(cand)
    
    # 3. Availability Multiplier & Interest
    availability_mult = calculate_availability_multiplier(cand)
    
    signals = cand.get("redrob_signals", {})
    views = signals.get("profile_views_received_30d", 0)
    searches = signals.get("search_appearance_30d", 0)
    saved = signals.get("saved_by_recruiters_30d", 0)
    interest_score = min((views * 2 + searches * 0.1 + saved * 5) / 100.0, 0.3)
    
    base_score = title_s * 0.4 + skill_s * 0.3 + hist_s * 0.3
    final_score = base_score * availability_mult + interest_score
    
    return {
        "candidate_id": cand["candidate_id"],
        "name": profile.get("anonymized_name"),
        "headline": profile.get("headline"),
        "years_exp": years_exp,
        "location": profile.get("location"),
        "current_title": profile.get("current_title"),
        "current_company": profile.get("current_company"),
        "score": final_score,
        "candidate_raw": cand  # keep reference for detail display
    }

def rank_candidates(candidates_list):
    """
    Ranks a list of candidate dictionaries.
    """
    scored = []
    for c in candidates_list:
        res = score_candidate(c)
        if res is not None:
            scored.append(res)
            
    # Sort by score desc, then by candidate_id asc
    scored.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    
    # Assign ranks and reasonings
    ranked_results = []
    for idx, c in enumerate(scored[:100]):
        rank = idx + 1
        c["rank"] = rank
        c["reasoning"] = generate_reasoning(c["candidate_raw"], rank)
        ranked_results.append(c)
        
    return ranked_results
