# Job Description Skill Gap Analyzer

A Streamlit app that compares a resume with a job description and reports:
overall match score, matching skills, missing skills, resume strengths, ranked skill gaps,
recommended skills to learn, and relevant job-description keywords.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Click **Load sample data** in the sidebar to try it instantly. Resume/JD can be pasted or uploaded (PDF, DOCX, TXT, MD).

Docker: `docker build -t skill-gap . && docker run -p 8501:8501 skill-gap`

## How it works
1. **Parse and clean** uploads (`file_parsers.py`, `text_processing.py`).
2. **Extract skills** from a ~200-skill ontology with boundary-safe regex matching (`skill_extractor.py`, `skills_db.py`).
   Ambiguous words (Rust, React, SAS) need their capitalisation; `C++`, `C#`, `.NET`, `Node.js` are handled.
3. **Weight JD skills**: "must / required / strong" = 2.0, standard = 1.0, "nice to have / preferred" = 0.5,
   plus a small bonus for repeated mentions. Section headers such as `Nice to have:` are respected.
4. **Reason over the ontology**: implied skills (Pandas -> Python) count as matched; similar tools
   (Power BI <-> Tableau) earn 30% credit and are flagged as quick wins.
5. **Score** = 80% weighted skill coverage + 12% keyword coverage + 8% TF-IDF cosine similarity (`scorer.py`).
   Weights are constants at the top of `scorer.py`.
6. **Recommend**: gaps ranked by priority with time estimates and learning tips (`recommender.py`).

## Project layout
```
app.py                  Streamlit UI
src/skills_db.py        Skill ontology, implications, transferable groups, learning tips
src/skill_extractor.py  Matching + importance weighting
src/scorer.py           Score components
src/keyword_extractor.py, resume_insights.py, recommender.py, analyzer.py, report.py
sample_data/            Example resume and JD
tests/test_analyzer.py  Unit tests
```

## Tests
```bash
python -m unittest discover -s tests      # or: pytest
```

## Customising
- Add skills/aliases in `src/skills_db.py` (e.g. new domains such as finance or marketing).
- Tune score weights in `src/scorer.py`.

## Limitations
Matching is dictionary-based, so skills missing from the ontology are not detected. Scanned-image PDFs need OCR
(paste the text instead). The score is a guide, not a hiring decision.
