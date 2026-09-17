import streamlit as st
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from analytics import load_analytics_data, get_faculty_aspect_breakdown, load_css, render_html
import plotly.express as px

load_css()

col_a, col_b = st.columns([5, 1])
with col_a:
    render_html('<div class="breadcrumb">AspectLens / Faculty Drill-Down</div>')
with col_b:
    render_html('<div class="live-badge">🟢 Live — Spring 2026</div>')

st.markdown("## 🔍 Faculty Drill-Down")
st.caption("Per-professor sentiment breakdown across teaching aspects")
st.write("")

@st.cache_data
def get_data():
    return load_analytics_data('data/analytics_ready.csv')

long_df = get_data()

render_html('<div class="metric-label">SEARCH PROFESSOR</div>')
all_professors = sorted(long_df['professor'].unique())
selected_professor = st.selectbox("", all_professors, label_visibility="collapsed")

st.write("")

if selected_professor:
    prof_data = long_df[long_df['professor'] == selected_professor]
    department = prof_data['department'].iloc[0]

    breakdown = get_faculty_aspect_breakdown(selected_professor, long_df)
    total_mentions = int(breakdown['total'].sum())
    total_negative = breakdown['negative'].sum()
    overall_negative_pct = (total_negative / total_mentions * 100) if total_mentions > 0 else 0

    badge_color = "#DC2626" if overall_negative_pct >= 50 else "#10B981"
    badge_bg = "#FEE2E2" if overall_negative_pct >= 50 else "#D1FAE5"

    render_html(f"""
    <div class="custom-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div class="professor-name">{selected_professor}</div>
                <div style="color:#9CA3AF; font-size:14px;">{department}</div>
            </div>
            <div style="background-color:{badge_bg}; color:{badge_color}; padding:4px 12px; border-radius:6px; font-size:13px; font-weight:600;">
                {overall_negative_pct:.1f}% negative
            </div>
        </div>
        <div style="display:flex; gap:60px; margin-top:24px; border-top:1px solid #F3F4F6; padding-top:20px;">
            <div>
                <div class="metric-label">TOTAL ASPECT MENTIONS</div>
                <div class="metric-value" style="font-size:28px;">{total_mentions}</div>
            </div>
            <div>
                <div class="metric-label">OVERALL NEGATIVE %</div>
                <div class="metric-value" style="font-size:28px; color:{badge_color};">{overall_negative_pct:.1f}%</div>
            </div>
        </div>
    </div>
    """)

    st.write("")

    render_html("""
    <div class="section-header">
        <span class="section-dot" style="background-color:#6366F1;"></span>
        Aspect Breakdown
    </div>
    """)

    melted = breakdown.melt(
        id_vars='aspect',
        value_vars=['positive', 'negative', 'neutral'],
        var_name='sentiment',
        value_name='count'
    )
    melted['aspect'] = melted['aspect'].apply(lambda a: a.replace('_', ' ').title())

    fig = px.bar(
        melted,
        x='aspect',
        y='count',
        color='sentiment',
        color_discrete_map={'positive': '#10B981', 'negative': '#DC2626', 'neutral': '#9CA3AF'},
        barmode='group'
    )
    fig.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family='Inter, sans-serif', color='#111827'),
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, title=''),
    xaxis_title='',
    yaxis_title='',
    margin=dict(t=20, b=20),
    bargap=0.3,
    bargroupgap=0.15
    )
    fig.update_yaxes(gridcolor='#F3F4F6')

    st.plotly_chart(fig, use_container_width=True, config={
    'displayModeBar': False,
    'scrollZoom': False,
    'doubleClick': False,
    'staticPlot': True
    })

    st.write("")

    render_html("""
    <div class="section-header">
        <span class="section-dot" style="background-color:#9CA3AF;"></span>
        Detailed Numbers
    </div>
    """)

    rows_html = ""
    for i, row in breakdown.reset_index(drop=True).iterrows():
        aspect_display = row['aspect'].replace('_', ' ').title()
        rows_html += f"""
        <tr style="border-bottom: 1px solid #F3F4F6;">
            <td style="padding: 12px 8px; color:#9CA3AF; font-size:13px;">{i}</td>
            <td style="padding: 12px 8px; font-weight:600;">{aspect_display}</td>
            <td style="padding: 12px 8px; text-align:right; color:#DC2626; font-weight:600;">{int(row['negative'])}</td>
            <td style="padding: 12px 8px; text-align:right; color:#9CA3AF;">{int(row['neutral'])}</td>
            <td style="padding: 12px 8px; text-align:right; color:#10B981; font-weight:600;">{int(row['positive'])}</td>
            <td style="padding: 12px 8px; text-align:right;">{int(row['total'])}</td>
        </tr>
        """

    table_html = f"""
    <div class="custom-card">
    <table style="width:100%; border-collapse: collapse;">
        <thead>
            <tr style="border-bottom: 2px solid #F3F4F6; text-align:left;">
                <th style="padding: 8px; color:#9CA3AF; font-size:12px;">#</th>
                <th style="padding: 8px; color:#9CA3AF; font-size:12px;">ASPECT</th>
                <th style="padding: 8px; color:#DC2626; font-size:12px; text-align:right;">NEGATIVE</th>
                <th style="padding: 8px; color:#9CA3AF; font-size:12px; text-align:right;">NEUTRAL</th>
                <th style="padding: 8px; color:#10B981; font-size:12px; text-align:right;">POSITIVE</th>
                <th style="padding: 8px; color:#9CA3AF; font-size:12px; text-align:right;">TOTAL</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    </div>
    """

    render_html(table_html)