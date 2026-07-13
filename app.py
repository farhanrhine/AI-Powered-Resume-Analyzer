# this is ui part
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import streamlit as st

import time
from resume_parser import parser_resume
from jd_parser import parse_jd
from matching_engine import analyze_match
from gap_analysis import find_gaps
from suggestion_generator import generate_suggestions

def stream_text(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


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

        # Custom CSS for glassmorphism styling
        st.markdown("""
            <style>
            .badge-green {
                display: inline-block;
                background-color: rgba(46, 204, 113, 0.15);
                color: #2ecc71;
                padding: 6px 14px;
                border-radius: 20px;
                margin: 5px;
                font-weight: 600;
                font-size: 14px;
                border: 1px solid rgba(46, 204, 113, 0.3);
            }
            .badge-red {
                display: inline-block;
                background-color: rgba(231, 76, 60, 0.15);
                color: #e74c3c;
                padding: 6px 14px;
                border-radius: 20px;
                margin: 5px;
                font-weight: 600;
                font-size: 14px;
                border: 1px solid rgba(231, 76, 60, 0.3);
            }
            </style>
        """, unsafe_allow_html=True)

        # Dynamic score card coloring
        if score >= 75:
            score_color = "#2ecc71"
            bg_color = "rgba(46, 204, 113, 0.1)"
            border_color = "rgba(46, 204, 113, 0.3)"
            label = "Excellent Match"
        elif score >= 40:
            score_color = "#f39c12"
            bg_color = "rgba(243, 156, 18, 0.1)"
            border_color = "rgba(243, 156, 18, 0.3)"
            label = "Partial Match"
        else:
            score_color = "#e74c3c"
            bg_color = "rgba(231, 76, 60, 0.1)"
            border_color = "rgba(231, 76, 60, 0.3)"
            label = "Low Match"

        # Tabbed interface
        tab1, tab2, tab3 = st.tabs(["📊 Match Analysis", "🎯 Skills Alignment", "💡 Action Plan"])

        with tab1:
            col_score, col_summary = st.columns([1, 2])
            with col_score:
                st.markdown(f"""
                    <div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 12px; padding: 30px; text-align: center;">
                        <h3 style="margin: 0; font-size: 18px; opacity: 0.8;">Match Score</h3>
                        <h1 style="margin: 10px 0; font-size: 64px; color: {score_color}; font-weight: bold;">{score}%</h1>
                        <span style="background-color: {score_color}; color: white; padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: 600; display: inline-block;">{label}</span>
                    </div>
                """, unsafe_allow_html=True)
            with col_summary:
                st.subheader("Match Summary")
                st.write_stream(stream_text(summary))

        with tab2:
            col_matched, col_gaps = st.columns(2)
            with col_matched:
                st.subheader("Matched Skills")
                if matched_skills:
                    badges_html = "".join(f'<span class="badge-green">{skill}</span>' for skill in matched_skills)
                    st.markdown(f'<div style="margin-top: 10px;">{badges_html}</div>', unsafe_allow_html=True)
                else:
                    st.write("No matching skills found.")
            with col_gaps:
                st.subheader("Skill Gaps / Missing Keywords")
                if gaps:
                    badges_html = "".join(f'<span class="badge-red">{gap}</span>' for gap in gaps)
                    st.markdown(f'<div style="margin-top: 10px;">{badges_html}</div>', unsafe_allow_html=True)
                else:
                    st.success("No Major gaps detected!")

        with tab3:
            st.subheader("How to Improve Your Resume")
            for i, suggestion in enumerate(suggestions, start=1):
                st.write_stream(stream_text(f"💡 **Step {i}:** {suggestion}"))

        st.divider()
        with st.expander("View Extracted Resume Text"):
            st.text(resume_text)
                