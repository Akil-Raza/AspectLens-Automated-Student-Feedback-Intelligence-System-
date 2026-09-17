import streamlit as st
import sys
import os
from fpdf import FPDF
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from analytics import load_analytics_data, get_faculty_flags, load_css, render_html

load_css()

# Top breadcrumb bar
col_a, col_b = st.columns([5, 1])
with col_a:
    render_html('<div class="breadcrumb">AspectLens / Overview</div>')
with col_b:
    render_html('<div class="live-badge">🟢 Live — Spring 2026</div>')

st.markdown("## 📊 AspectLens")
st.caption("Student Feedback Intelligence — Automated aspect-based sentiment analysis")
st.write("")

@st.cache_data
def get_data():
    return load_analytics_data('data/analytics_ready.csv')

long_df = get_data()

total_professors = long_df['professor'].nunique()
total_mentions = len(long_df)
positive_pct = (long_df['sentiment'] == 'positive').sum() / len(long_df) * 100

col1, col2, col3 = st.columns(3)

with col1:
    render_html(f"""
    <div class="custom-card">
        <div class="metric-label">PROFESSORS ANALYZED</div>
        <div class="metric-value">{total_professors}</div>
        <div class="metric-caption">Active in current dataset</div>
    </div>
    """)

with col2:
    render_html(f"""
    <div class="custom-card">
        <div class="metric-label">TOTAL ASPECT MENTIONS</div>
        <div class="metric-value">{total_mentions:,}</div>
        <div class="metric-caption">Across all departments</div>
    </div>
    """)

with col3:
    render_html(f"""
    <div class="custom-card">
        <div class="metric-label">OVERALL POSITIVE SENTIMENT</div>
        <div class="metric-value">{positive_pct:.1f}%</div>
        <div class="metric-caption">Across all feedback</div>
    </div>
    """)

st.write("")

render_html("""
<div class="section-header">
    <span class="section-dot" style="background-color:#F59E0B;"></span>
    Faculty Flagged for Review
</div>
<div class="section-caption">Professors with highest negative sentiment (minimum 10 mentions)</div>
""")

flagged = get_faculty_flags(long_df, min_mentions=10).head(10).reset_index(drop=True)

def severity_color(pct):
    if pct >= 90:
        return "#DC2626"
    elif pct >= 60:
        return "#F59E0B"
    else:
        return "#9CA3AF"

def badge_class(pct):
    if pct >= 90:
        return "badge-critical"
    elif pct >= 60:
        return "badge-warning"
    else:
        return "badge-neutral"

def generate_pdf_report(long_df, flagged_df):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, 'AspectLens - Student Feedback Report', ln=True)
    
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, f'Generated on {datetime.now().strftime("%B %d, %Y")}', ln=True)
    pdf.ln(6)
    
    # Overview stats
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.cell(0, 10, 'Overview', ln=True)
    
    pdf.set_font('Helvetica', '', 11)
    total_professors = long_df['professor'].nunique()
    total_mentions = len(long_df)
    positive_pct = (long_df['sentiment'] == 'positive').sum() / len(long_df) * 100
    
    pdf.cell(0, 8, f'Professors Analyzed: {total_professors}', ln=True)
    pdf.cell(0, 8, f'Total Aspect Mentions: {total_mentions:,}', ln=True)
    pdf.cell(0, 8, f'Overall Positive Sentiment: {positive_pct:.1f}%', ln=True)
    pdf.ln(6)
    
    # Flagged faculty table
    pdf.set_font('Helvetica', 'B', 13)
    pdf.cell(0, 10, 'Faculty Flagged for Review', ln=True)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(80, 8, 'Professor', border=1, fill=True)
    pdf.cell(50, 8, 'Mentions', border=1, fill=True)
    pdf.cell(50, 8, 'Negative %', border=1, fill=True)
    pdf.ln()
    
    pdf.set_font('Helvetica', '', 10)
    for _, row in flagged_df.iterrows():
        pdf.cell(80, 8, str(row['professor']), border=1)
        pdf.cell(50, 8, str(row['total']), border=1)
        pdf.cell(50, 8, f"{row['negative_pct']}%", border=1)
        pdf.ln()
    
    return bytes(pdf.output())

rows_html = ""
for i, row in flagged.iterrows():
    color = severity_color(row['negative_pct'])
    badge = badge_class(row['negative_pct'])
    rows_html += f"""
    <tr style="border-bottom: 1px solid #F3F4F6;">
        <td style="padding: 12px 8px; color:#9CA3AF; font-size:13px;">{i+1}</td>
        <td style="padding: 12px 8px; font-weight:600;">{row['professor']}</td>
        <td style="padding: 12px 8px; text-align:right;">{row['total']}</td>
        <td style="padding: 12px 8px; text-align:right;"><span class="badge {badge}">{row['negative_pct']}%</span></td>
        <td style="padding: 12px 8px; text-align:right;">
            <div class="severity-bar-bg">
                <div class="severity-bar-fill" style="width:{row['negative_pct']}%; background-color:{color};"></div>
            </div>
        </td>
    </tr>
    """

table_html = f"""
<div class="custom-card">
<table style="width:100%; border-collapse: collapse;">
    <thead>
        <tr style="border-bottom: 2px solid #F3F4F6; text-align:left;">
            <th style="padding: 8px; color:#9CA3AF; font-size:12px;">#</th>
            <th style="padding: 8px; color:#9CA3AF; font-size:12px;">PROFESSOR</th>
            <th style="padding: 8px; color:#9CA3AF; font-size:12px; text-align:right;">MENTIONS</th>
            <th style="padding: 8px; color:#9CA3AF; font-size:12px; text-align:right;">NEGATIVE %</th>
            <th style="padding: 8px; color:#9CA3AF; font-size:12px; text-align:right;">SEVERITY</th>
        </tr>
    </thead>
    <tbody>
        {rows_html}
    </tbody>
</table>
</div>
"""

render_html(table_html)
st.write("")

pdf_bytes = generate_pdf_report(long_df, flagged)

st.download_button(
    label="📄 Download PDF Report",
    data=pdf_bytes,
    file_name=f"aspectlens_report_{datetime.now().strftime('%Y%m%d')}.pdf",
    mime="application/pdf"
)