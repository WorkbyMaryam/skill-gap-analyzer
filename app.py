"""Streamlit UI for the Job Description Skill Gap Analyzer.

Run:  streamlit run app.py
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analyzer import analyze
from src.file_parsers import SUPPORTED_EXTENSIONS, extract_text
from src.report import gaps_to_csv, to_markdown

SAMPLE_DIR = Path(__file__).parent / "sample_data"

st.set_page_config(page_title="Skill Gap Analyzer", page_icon="🎯", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,700&display=swap');
h1, h2, h3 { font-family: 'Newsreader', Georgia, serif !important; letter-spacing: -0.01em; }
.gauge { --pct: 0; width: 170px; height: 170px; border-radius: 50%;
  background: conic-gradient(var(--c) calc(var(--pct) * 1%), #E3E8EF 0);
  display: grid; place-items: center; margin: 0 auto; }
.gauge > div { width: 128px; height: 128px; border-radius: 50%; background: var(--bg, #fff);
  display: grid; place-items: center; text-align: center; }
.gauge b { font-family: 'Newsreader', Georgia, serif; font-size: 2.4rem; line-height: 1; }
.pill { display: inline-block; padding: 3px 11px; margin: 3px 4px 3px 0; border-radius: 999px;
  font-size: 0.86rem; border: 1px solid; }
.pill.ok { background: #E8F5EE; color: #0B5D3B; border-color: #A9D8BE; }
.pill.no { background: #FDECEA; color: #8F1D14; border-color: #F2B8B2; }
.pill.mid { background: #FFF4DB; color: #7A4B00; border-color: #EBCB85; }
.pill.neutral { background: #EEF1F6; color: #2B3A55; border-color: #CBD3E1; }
.callout { border-left: 4px solid #0F766E; background: #F0F7F6; padding: 14px 18px; border-radius: 6px; color: #12332F; }
</style>
""",
    unsafe_allow_html=True,
)


# ---------- helpers ----------
def pills(items: list[str], kind: str) -> None:
    if not items:
        st.caption("None")
        return
    st.markdown("".join(f"<span class='pill {kind}'>{html.escape(i)}</span>" for i in items), unsafe_allow_html=True)


def gauge(score: float) -> None:
    color = "#0B7A4B" if score >= 65 else ("#C77D0A" if score >= 40 else "#B42318")
    st.markdown(
        f"<div class='gauge' style='--pct:{score:.0f};--c:{color}'><div><b>{score:.0f}%</b></div></div>",
        unsafe_allow_html=True,
    )


def load_sample() -> None:
    st.session_state["resume_text"] = (SAMPLE_DIR / "resume.txt").read_text(encoding="utf-8")
    st.session_state["jd_text"] = (SAMPLE_DIR / "job_description.txt").read_text(encoding="utf-8")


def resolve_text(label: str, key: str, upload) -> str:
    """Prefer an uploaded file; fall back to pasted text."""
    if upload is not None:
        try:
            return extract_text(upload.name, upload.getvalue())
        except ValueError as exc:
            st.error(f"{label}: {exc}")
            return ""
    return st.session_state.get(key, "")


# ---------- header ----------
st.title("Job Description Skill Gap Analyzer")
st.write("Compare your resume with a job description to see your match score, the skills you already "
         "have, what is missing, and what to learn next.")

with st.sidebar:
    st.header("How scoring works")
    st.markdown(
        "- **80%** weighted skill coverage (*must-have* skills count more than *nice-to-have*)\n"
        "- **12%** keyword coverage of JD phrases\n"
        "- **8%** TF-IDF text similarity\n\n"
        "Similar tools (e.g. Power BI vs Tableau) earn partial credit and are flagged as quick wins."
    )
    st.button("Load sample data", on_click=load_sample, use_container_width=True)
    st.caption("Your text is processed in memory and never stored.")

# ---------- inputs ----------
col_r, col_j = st.columns(2)
with col_r:
    st.subheader("Your resume")
    t1, t2 = st.tabs(["Paste text", "Upload file"])
    with t1:
        st.text_area("Resume text", key="resume_text", height=300, label_visibility="collapsed",
                     placeholder="Paste your resume here...")
    with t2:
        resume_file = st.file_uploader("Resume file", type=list(SUPPORTED_EXTENSIONS), key="resume_file",
                                       label_visibility="collapsed")
with col_j:
    st.subheader("Job description")
    t3, t4 = st.tabs(["Paste text", "Upload file"])
    with t3:
        st.text_area("Job description text", key="jd_text", height=300, label_visibility="collapsed",
                     placeholder="Paste the job description here...")
    with t4:
        jd_file = st.file_uploader("Job description file", type=list(SUPPORTED_EXTENSIONS), key="jd_file",
                                   label_visibility="collapsed")

if st.button("Analyze match", type="primary", use_container_width=True):
    resume_text = resolve_text("Resume", "resume_text", resume_file)
    jd_text = resolve_text("Job description", "jd_text", jd_file)
    try:
        with st.spinner("Analyzing..."):
            st.session_state["result"] = analyze(resume_text, jd_text)
    except ValueError as exc:
        st.session_state.pop("result", None)
        st.error(str(exc))

# ---------- results ----------
result = st.session_state.get("result")
if result:
    st.divider()
    for w in result.warnings:
        st.warning(w)

    head_l, head_r = st.columns([1, 2])
    with head_l:
        gauge(result.score)
        st.markdown(f"<h3 style='text-align:center;margin-top:8px'>{result.label}</h3>", unsafe_allow_html=True)
    with head_r:
        st.subheader("Recommendation")
        st.markdown(f"<div class='callout'>{html.escape(result.recommendation)}</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Skill coverage", f"{result.components['skill_coverage']:.0f}%")
        c2.metric("Keyword coverage", f"{result.components['keyword_coverage']:.0f}%")
        c3.metric("Text similarity", f"{result.components['text_similarity']:.0f}%")
        st.caption(f"{len(result.matching_skills)} of {result.jd_skill_count} job skills matched.")

    tab_skills, tab_gaps, tab_strengths, tab_kw, tab_tips = st.tabs(
        ["Skills", "Gaps & roadmap", "Strengths", "Keywords", "Resume tips"])

    with tab_skills:
        a, b = st.columns(2)
        with a:
            st.subheader("✓ Matching skills")
            for m in result.matching_skills:
                tag = " (implied)" if m["implied"] else ""
                st.markdown(f"<span class='pill ok'>✓ {html.escape(m['skill'])}{tag}</span>"
                            f"<span class='pill neutral'>{m['importance']}</span>", unsafe_allow_html=True)
            if not result.matching_skills:
                st.caption("No overlapping skills detected.")
        with b:
            st.subheader("✗ Missing skills")
            for m in result.missing_skills:
                extra = f" - similar to your {', '.join(m['transferable_from'])}" if m["transferable_from"] else ""
                st.markdown(f"<span class='pill no'>✗ {html.escape(m['skill'])}</span>"
                            f"<span class='pill {'mid' if m['transferable_from'] else 'neutral'}'>"
                            f"{m['priority']} priority{html.escape(extra)}</span>", unsafe_allow_html=True)
            if not result.missing_skills:
                st.success("No missing skills - great coverage!")
        cats: dict[str, dict[str, int]] = {}
        for m in result.matching_skills:
            cats.setdefault(m["category"], {"Matched": 0, "Missing": 0})["Matched"] += 1
        for m in result.missing_skills:
            cats.setdefault(m["category"], {"Matched": 0, "Missing": 0})["Missing"] += 1
        if cats:
            st.subheader("Coverage by category")
            st.bar_chart(pd.DataFrame(cats).T, color=["#0B7A4B", "#B42318"])

    with tab_gaps:
        st.subheader("Top skill gaps")
        if not result.gaps:
            st.success("No gaps found for the skills listed in this job description.")
        for g in result.gaps:
            covers = f" (also covers {', '.join(g['also_covers'])})" if g.get("also_covers") else ""
            with st.expander(f"{g['rank']}. {g['skill']}{covers} - {g['priority']} priority", expanded=g["rank"] <= 3):
                st.markdown(f"**Why it matters:** {g['importance']} in the JD, mentioned {g['jd_mentions']}x.")
                st.markdown(f"**Estimated time:** {g['estimated_time']}")
                if g["transferable_from"]:
                    st.markdown(f"**Head start:** your {', '.join(g['transferable_from'])} experience transfers.")
                st.markdown(f"**How to learn:** {g['how_to_learn']}")
        if result.gaps:
            st.dataframe(pd.DataFrame(result.gaps)[["rank", "skill", "category", "priority", "estimated_time"]],
                         hide_index=True, use_container_width=True)

    with tab_strengths:
        st.subheader("Resume strengths")
        for s in result.strengths:
            st.markdown(f"**{s['title']}** - {s['detail']}")
        if not result.strengths:
            st.info("No standout strengths for this role were detected.")
        st.subheader("Other skills on your resume")
        pills(result.extra_skills, "neutral")

    with tab_kw:
        st.subheader("Job description keywords")
        pills([k["keyword"] for k in result.keywords if k["in_resume"]], "ok")
        st.markdown("**Not found in your resume**")
        pills([k["keyword"] for k in result.keywords if not k["in_resume"]], "no")

    with tab_tips:
        st.subheader("Improve your resume")
        for t in result.resume_tips:
            st.markdown(f"- {t}")
        if not result.resume_tips:
            st.success("Your resume structure looks solid.")

    st.divider()
    d1, d2, d3 = st.columns(3)
    d1.download_button("Download report (.md)", to_markdown(result), "skill_gap_report.md", use_container_width=True)
    d2.download_button("Download gaps (.csv)", gaps_to_csv(result), "skill_gaps.csv", use_container_width=True)
    d3.download_button("Download data (.json)", json.dumps(result.to_dict(), indent=2), "analysis.json",
                       use_container_width=True)
