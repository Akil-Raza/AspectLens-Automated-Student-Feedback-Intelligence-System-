import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from analytics import load_analytics_data, get_department_sentiment, get_all_weakest_aspects, load_css, render_html
import plotly.express as px

load_css()

col_a, col_b = st.columns([5, 1])
with col_a:
    render_html('<div class="breadcrumb">AspectLens / Department View</div>')
with col_b:
    render_html('<div class="live-badge">🟢 Live — Spring 2026</div>')

@st.cache_data
def get_data():
    return load_analytics_data('data/analytics_ready.csv')

long_df = get_data()

# Sentiment breakdown chart
render_html("""
<div class="section-header">
    <span class="section-dot" style="background-color:#6366F1;"></span>
    Sentiment Breakdown by Department
</div>
""")

dept_sentiment = get_department_sentiment(long_df)
dept_totals = long_df.groupby('department').size().reset_index(name='total')
top_departments = dept_totals.sort_values('total', ascending=False).head(10)['department'].tolist()
dept_sentiment_top = dept_sentiment[dept_sentiment['department'].isin(top_departments)]

fig = px.bar(
    dept_sentiment_top,
    x='department',
    y='percentage',
    color='sentiment',
    color_discrete_map={'positive': '#10B981', 'negative': '#DC2626', 'neutral': '#9CA3AF'},
    barmode='stack'
)
fig.update_layout(
    xaxis_tickangle=-30,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family='Inter, sans-serif', color='#111827'),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, title=''),
    xaxis_title='',
    yaxis_title='',
    margin=dict(t=20, b=20),
    bargap=0.4
)
fig.update_yaxes(gridcolor='#F3F4F6')

st.plotly_chart(fig, use_container_width=True, config={
    'displayModeBar': False,
    'scrollZoom': False,
    'doubleClick': False,
    'staticPlot': True
})

st.write("")

# Weakest aspect table
render_html("""
<div class="section-header">
    <span class="section-dot" style="background-color:#DC2626;"></span>
    Weakest Aspect Per Department
</div>
<div class="section-caption">The specific area each department should focus on improving</div>
""")

weakest = get_all_weakest_aspects(long_df, min_mentions=15).reset_index(drop=True)

def neg_badge_class(pct):
    if pct >= 50:
        return "badge-critical"
    elif pct >= 35:
        return "badge-warning"
    else:
        return "badge-neutral"

def format_aspect_name(aspect):
    return aspect.replace('_', ' ').title()

rows_html = ""
for i, row in weakest.iterrows():
    badge = neg_badge_class(row['negative_pct'])
    aspect_display = format_aspect_name(row['weakest_aspect'])
    rows_html += f"""
    <tr style="border-bottom: 1px solid #F3F4F6;">
        <td style="padding: 12px 8px; color:#9CA3AF; font-size:13px;">{i+1}</td>
        <td style="padding: 12px 8px; font-weight:600;">{row['department']}</td>
        <td style="padding: 12px 8px;"><span class="aspect-tag">{aspect_display}</span></td>
        <td style="padding: 12px 8px; text-align:right;"><span class="badge {badge}">{row['negative_pct']}%</span></td>
        <td style="padding: 12px 8px; text-align:right; color:#6B7280;">{int(row['total_mentions'])}</td>
    </tr>
    """

table_html = f"""
<div class="custom-card">
<table style="width:100%; border-collapse: collapse;">
    <thead>
        <tr style="border-bottom: 2px solid #F3F4F6; text-align:left;">
            <th style="padding: 8px; color:#9CA3AF; font-size:12px;">#</th>
            <th style="padding: 8px; color:#9CA3AF; font-size:12px;">DEPARTMENT</th>
            <th style="padding: 8px; color:#9CA3AF; font-size:12px;">WEAKEST ASPECT</th>
            <th style="padding: 8px; color:#9CA3AF; font-size:12px; text-align:right;">NEG %</th>
            <th style="padding: 8px; color:#9CA3AF; font-size:12px; text-align:right;">MENTIONS</th>
        </tr>
    </thead>
    <tbody>
        {rows_html}
    </tbody>
</table>
</div>
"""

render_html(table_html)