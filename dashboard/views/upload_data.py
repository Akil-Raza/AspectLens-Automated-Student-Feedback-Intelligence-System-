import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from analytics import load_css, render_html
from preprocess import preprocess
from absa import extract_aspects, load_bert_model, predict_sentiment_bert

st.set_page_config(page_title="Upload Data", layout="wide", page_icon="📤")
load_css()

col_a, col_b = st.columns([5, 1])
with col_a:
    render_html('<div class="breadcrumb">AspectLens / Upload Data</div>')
with col_b:
    render_html('<div class="live-badge">🟢 Live — Spring 2026</div>')

st.markdown("## 📤 Upload New Feedback")
st.caption("Add a new batch of student feedback for analysis")
st.write("")

@st.cache_resource
def get_bert_model():
    return load_bert_model('model/final_model')

render_html("""
<div class="section-header">
    <span class="section-dot" style="background-color:#6366F1;"></span>
    Upload CSV
</div>
<div class="section-caption">File must contain columns: professor, department, Comment (Quality and Difficulty optional)</div>
""")

uploaded_file = st.file_uploader("", type=['csv'], label_visibility="collapsed")

if uploaded_file is not None:
    new_df = pd.read_csv(uploaded_file)

    required_cols = {'professor', 'department', 'Comment'}
    missing_cols = required_cols - set(new_df.columns)

    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
    else:
        st.success(f"File loaded successfully — {len(new_df)} rows found")

        st.write("")
        render_html('<div class="metric-label">PREVIEW</div>')
        st.dataframe(new_df.head(10), use_container_width=True)

        if st.button("Process and Add to Dataset", type="primary"):
            with st.spinner("Loading model..."):
                bert_model, bert_tokenizer, device = get_bert_model()

            with st.spinner(f"Analyzing {len(new_df)} comments... this may take a minute"):
                new_df['cleaned_comment'] = new_df['Comment'].apply(preprocess)
                new_df['aspects'] = new_df['cleaned_comment'].apply(extract_aspects)

                progress_bar = st.progress(0)
                rows = []
                total = len(new_df)

                for idx, row in new_df.iterrows():
                    for aspect in row['aspects']:
                        sentiment = predict_sentiment_bert(
                            aspect, row['Comment'], bert_model, bert_tokenizer, device
                        )
                        rows.append({
                            'professor': row['professor'],
                            'department': row['department'],
                            'Quality': row.get('Quality', None),
                            'Difficulty': row.get('Difficulty', None),
                            'aspect': aspect,
                            'sentiment': sentiment
                        })
                    progress_bar.progress((idx + 1) / total)

                new_long_df = pd.DataFrame(rows)

                existing_path = 'data/analytics_ready.csv'
                existing_df = pd.read_csv(existing_path)
                combined_df = pd.concat([existing_df, new_long_df], ignore_index=True)
                combined_df.to_csv(existing_path, index=False)

            st.success(f"Added {len(new_long_df)} new aspect-sentiment records to the dataset using real BERT predictions!")
            st.cache_data.clear()
            st.info("Go to Overview, Department View, or Faculty Drilldown and refresh to see updated numbers.")