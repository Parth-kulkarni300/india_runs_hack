# Redrob AI Recruiter Brain & Dashboard

An intelligent candidate discovery, trap-filtering, and predictive ranking system for the **Senior AI Engineer — Founding Team** role at **Redrob AI**.

This project provides both a command-line ranking script and an interactive Streamlit dashboard for recruiters to analyze profiles, defuse database honeypots, apply filters, and view customized recruiter reasonings.

---

## Folder Structure

- `ranker.py`: Shared core library containing all filters (honeypots, consulting-only, locations), candidate scoring formulas, and programmatic reasoning generation.
- `app.py`: Streamlit Dashboard application code.
- `requirements.txt`: Python package dependencies.
- `.gitignore`: Spec to exclude heavy datasets (`candidates.jsonl`), local logs, and caches from git tracking.

---

## Getting Started

### 1. Installation
Ensure you have Python installed, then open your terminal in this directory and install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Candidate Data
Make sure `candidates.jsonl` (the candidate database) is located in the sibling folder (at `../India_runs_data_and_ai_challenge/candidates.jsonl`). If it is in a different location, you can update the path in the sidebar input in the dashboard.

### 3. Run the Dashboard
Start the local dashboard server:
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501` to view the recruiter cockpit.

---

## Collaboration Guide
- **Adding features**: You and your teammate can collaborate by modifying `app.py` for visual changes or updating the matching formulas in `ranker.py` to change the underlying algorithm.
- **Git Push/Pull**: Ensure your `.gitignore` is active so that the heavy `candidates.jsonl` data file is not committed to GitHub.
