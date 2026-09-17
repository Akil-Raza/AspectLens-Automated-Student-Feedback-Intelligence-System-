# 📊 AspectLens — Automated Student Feedback Intelligence System

An aspect-based sentiment analysis (ABSA) system that turns unstructured student feedback into actionable insights for academic quality monitoring — built end-to-end from data cleaning to a deployed interactive dashboard.

🔗 **Live Demo:** [Add your Streamlit Cloud link here once deployed]

---

## The Problem

Colleges collect thousands of open-ended student feedback comments every semester, but this text is rarely analyzed beyond star ratings. AspectLens automatically extracts **which specific teaching aspects** (explanation clarity, doubt-solving, study material, etc.) students are talking about, and whether they feel positively or negatively about each one — giving academic administrators specific, actionable insight instead of a single average score.

---

## Key Findings

- Fine-tuned **DistilBERT** for aspect-level sentiment classification, achieving **91.4% accuracy** (0.913 weighted F1) — a significant improvement over a rule-based VADER baseline, which was wrong on **15.8%** of manually verified sentiment labels
- Discovered that **"Explanation Clarity"** is the top weak aspect in **9 out of 14 departments** analyzed — a college-wide pattern rather than isolated faculty issues
- Documented an honest model limitation: the fine-tuned model does not fully disentangle sentiment when a single sentence expresses conflicting opinions across multiple aspects, due to limited representation of such cases in the training data

---

## Features

- **Overview Dashboard** — institution-wide metrics and a faculty early-warning system flagging professors with high negative sentiment
- **Department View** — sentiment breakdown by department with automatic identification of each department's weakest teaching aspect
- **Faculty Drill-down** — searchable, per-professor aspect-level sentiment breakdown
- **CSV Upload** — add new feedback batches with real-time BERT inference
- **PDF Export** — generate a shareable summary report for academic administrators

---

## Tech Stack

| Layer | Tools |
|---|---|
| NLP | HuggingFace Transformers (DistilBERT), spaCy, VADER |
| Data Processing | Pandas, NumPy |
| Dashboard | Streamlit, Plotly |
| Model Hosting | Hugging Face Hub |
| Model Training | Google Colab (T4 GPU) |

---

## Pipeline Overview

Raw Feedback Data
↓
Text Preprocessing (spaCy: cleaning, lemmatization)
↓
Rule-Based Aspect Extraction (keyword matching, 7 teaching aspects)
↓
Rule-Based Sentiment (VADER) — baseline
↓
Manual Labeling (638 aspect-sentiment pairs)
↓
BERT Fine-Tuning (DistilBERT, 91.4% accuracy)
↓
Analytics Layer (department/faculty aggregation)
↓
Streamlit Dashboard


---

## Dataset

[Rate My Professor Reviews — 5C Colleges](https://www.kaggle.com/datasets/tilorc/rate-my-professor-reviews-5c-colleges) (Kaggle), 3,367 cleaned reviews across 14 departments and 283 professors.

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/Akil-Raza/AspectLens-Automated-Student-Feedback-Intelligence-System-.git
cd AspectLens-Automated-Student-Feedback-Intelligence-System-

# Set up virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Run the dashboard
streamlit run dashboard/app.py
```

The BERT model automatically downloads from [Hugging Face Hub](https://huggingface.co/AkilRaza/aspectlens-bert) on first run if not present locally.

---

## Model Limitations

While the model performs well on the held-out test set, qualitative testing revealed it does not fully separate sentiment across multiple aspects when they conflict within a single sentence (e.g., "explains well but never answers doubts" may not correctly assign different sentiment to each aspect mentioned). This is a known challenge in aspect-based sentiment analysis and would benefit from a larger training set with more examples of mixed-sentiment sentences.

---

## Author

**Akil Raza** — 3rd-year AI student, building toward a Data Analyst role.
**Linkedin** - www.linkedin.com/in/akil-raza-shaikh-b7930b332