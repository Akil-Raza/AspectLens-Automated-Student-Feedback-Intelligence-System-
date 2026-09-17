import pandas as pd
import streamlit as st

def load_css(css_path='dashboard/assets/styles.css'):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        

def render_html(html):
    """Strips leading whitespace from each line to prevent Markdown 
    from treating indented HTML as a code block"""
    lines = html.split('\n')
    cleaned = '\n'.join(line.strip() for line in lines)
    st.markdown(cleaned, unsafe_allow_html=True)

        
def load_analytics_data(filepath='../data/analytics_ready.csv'):
    """Load the long-format analytics-ready dataset"""
    return pd.read_csv(filepath)


def get_department_sentiment(long_df):
    """Returns department-wise sentiment percentage breakdown"""
    dept_sentiment = long_df.groupby(['department', 'sentiment']).size().reset_index(name='count')
    dept_totals = dept_sentiment.groupby('department')['count'].sum().reset_index(name='total')
    dept_sentiment = dept_sentiment.merge(dept_totals, on='department')
    dept_sentiment['percentage'] = (dept_sentiment['count'] / dept_sentiment['total'] * 100).round(1)
    return dept_sentiment


def get_weakest_aspect(department_name, long_df, min_mentions=15):
    """Returns the single weakest aspect for a given department"""
    dept_data = long_df[long_df['department'] == department_name]

    summary = dept_data.groupby(['aspect', 'sentiment']).size().reset_index(name='count')
    pivot = summary.pivot(index='aspect', columns='sentiment', values='count').fillna(0)

    for col in ['negative', 'neutral', 'positive']:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot['total'] = pivot['negative'] + pivot['neutral'] + pivot['positive']
    pivot['negative_pct'] = (pivot['negative'] / pivot['total'] * 100).round(1)

    reliable = pivot[pivot['total'] >= min_mentions]
    weakest = reliable.sort_values('negative_pct', ascending=False).head(1)
    return weakest


def get_all_weakest_aspects(long_df, min_mentions=15):
    """Returns weakest aspect for every department at once"""
    all_departments = long_df['department'].unique()

    weakest_by_dept = []
    for dept in all_departments:
        result = get_weakest_aspect(dept, long_df, min_mentions)
        if not result.empty:
            weakest_by_dept.append({
                'department': dept,
                'weakest_aspect': result.index[0],
                'negative_pct': result['negative_pct'].values[0],
                'total_mentions': result['total'].values[0]
            })

    return pd.DataFrame(weakest_by_dept).sort_values('negative_pct', ascending=False)


def get_faculty_flags(long_df, min_mentions=10):
    """Returns professors sorted by negative sentiment percentage"""
    prof_sentiment = long_df.groupby(['professor', 'sentiment']).size().reset_index(name='count')
    prof_totals = prof_sentiment.groupby('professor')['count'].sum().reset_index(name='total')

    prof_sentiment = prof_sentiment.merge(prof_totals, on='professor')

    negative_only = prof_sentiment[prof_sentiment['sentiment'] == 'negative'].copy()
    negative_only['negative_pct'] = (negative_only['count'] / negative_only['total'] * 100).round(1)

    negative_only = negative_only[negative_only['total'] >= min_mentions]

    flagged = negative_only.sort_values('negative_pct', ascending=False)
    return flagged[['professor', 'total', 'negative_pct']]


def get_faculty_aspect_breakdown(professor_name, long_df):
    """Returns aspect-level sentiment breakdown for one specific professor"""
    prof_data = long_df[long_df['professor'] == professor_name]

    summary = prof_data.groupby(['aspect', 'sentiment']).size().reset_index(name='count')
    pivot = summary.pivot(index='aspect', columns='sentiment', values='count').fillna(0)

    for col in ['negative', 'neutral', 'positive']:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot['total'] = pivot['negative'] + pivot['neutral'] + pivot['positive']
    return pivot.reset_index()