# this is ui part
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st

from resume_parser import parser_resume
from jd_parser import parse_jd
from matching_engine import analyze_match
from gap_analysis import find_gaps
from suggestion_generator import generate_suggestions


st.set_page_config(
    page_title = "AI-Powered-Resume-Analyzer",
    page_icon="🎯",
    layout="wide"
)

st.title("AI-Powered Resume Analyzer")
st.markdown("Upload your resume & paste a job description to see how well they match.")
st.divider()

col1, col2 = st.columns([1,1])

with col1:
    st.subheader("Your Resume")
    uploaded_file = st.file_uploader("Upload your resume(PDF)", type = ["pdf"])

with col2:
    st.subheader("Job Description")
    jd_input = st.text_area("Paste Job Description Here", height=200)


st.divider()

analyze_bth = st.button("Analyze my Resume", use_container_width=True)

if analyze_bth:
    if not uploaded_file:
        st.error("Please upload a PDF resume first")
    elif not jd_input.strip():
        st.error("Please paste a job descrpption")
    else:
        with st.spinner("Analyzing your resume....."):

            resume_text = parser_resume(uploaded_file)
            jd_text = parse_jd(jd_input)

            match_result = analyze_match(resume_text, jd_text)
            gaps = find_gaps(resume_text, jd_text)
            suggestions = generate_suggestions(gaps, resume_text)



        st.success("Analysis Complete!")
        st.divider()

        score = match_result.get("score", 0)
        matched_skills = match_result.get("matched_skills", [])
        summary = match_result.get("summary", "")

        r1, r2 = st.columns([1,2])

        with r1:
            st.metric(label = "Match Score", value = f"{score}%")
        with r2:
            st.markdown("Summary")
            st.write(summary)

        st.divider()

        st.subheader("matched skills")
        if matched_skills:
            for skill in matched_skills:
                st.markdown(f"- **{skill}**")
        else:
            st.write("No matching skills found.")

        st.divider()

        st.subheader("Skill gaps")

        if gaps:
            for gap in gaps:
                st.markdown(f"- ❌ {gap}")
        else:
            st.success("No Major gaps detected!")

        st.divider()

        st.subheader("How to improve your Resume")

        for i, suggestion in enumerate(suggestions, start = 1): 
            st.write(f"{i}. {suggestion}")

        with st.expander("view extracted resume text"):
            st.text(resume_text)
                