from transformers import DistilBertForSequenceClassification, DistilBertTokenizer
import torch
import os

LABEL_NAMES = ['negative', 'neutral', 'positive']

# Define keywords for each aspect
ASPECT_KEYWORDS = {
    'explanation_clarity': [
        'explain', 'clear', 'unclear', 'confusing', 'understandable',
        'articulate', 'confuse', 'clarity', 'communicate', 'lecture'
    ],
    'teaching_pace': [
        'pace', 'fast', 'slow', 'rush', 'quick', 'speed',
        'too fast', 'too slow', 'keep up', 'behind'
    ],
    'doubt_solving': [
        'doubt', 'question', 'answer', 'help', 'office hour',
        'available', 'respond', 'feedback', 'approachable', 'email'
    ],
    'study_material': [
        'note', 'slide', 'textbook', 'material', 'resource',
        'reading', 'assignment', 'handout', 'powerpoint', 'pdf'
    ],
    'practical_sessions': [
        'lab', 'practical', 'project', 'exam', 'test',
        'quiz', 'homework', 'assignment', 'exercise', 'practice'
    ],
    'faculty_availability': [
        'available', 'office hour', 'accessible', 'meet',
        'appointment', 'busy', 'absent', 'presence', 'punctual'
    ],
    'subject_difficulty': [
        'difficult', 'easy', 'hard', 'tough', 'simple',
        'challenging', 'manageable', 'overwhelming', 'workload', 'stress'
    ]
}

def extract_aspects(text):
    """Returns a list of aspects found in the text"""
    found_aspects = []
    for aspect, keywords in ASPECT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                found_aspects.append(aspect)
                break  # No need to check more keywords for this aspect
    return found_aspects

def get_sentiment_label(compound_score):
    if compound_score >= 0.05:
        return 'positive'
    elif compound_score <= -0.05:
        return 'negative'
    else:
        return 'neutral'

import re

def split_on_contrast(text):
    """Split text into chunks at contrast words like but/however/although"""
    parts = re.split(r'\bbut\b|\bhowever\b|\balthough\b|\byet\b', text)
    return [p.strip() for p in parts if p.strip()]

def analyze_aspects_sentiment(text, analyzer):
    """
    Returns a dict: {aspect: (sentiment_label, compound_score)}
    Splits text on contrast words so mixed-sentiment sentences are handled better
    """
    chunks = split_on_contrast(text)
    
    result = {}
    for chunk in chunks:
        aspects = extract_aspects(chunk)
        if not aspects:
            continue
        
        scores = analyzer.polarity_scores(chunk)
        compound = scores['compound']
        label = get_sentiment_label(compound)
        
        for aspect in aspects:
            # If aspect already found in another chunk, keep the stronger sentiment
            if aspect not in result or abs(compound) > abs(result[aspect][1]):
                result[aspect] = (label, compound)
    
    return result

from huggingface_hub import snapshot_download

def load_bert_model(model_path='model/final_model', hub_repo='AkilRaza/aspectlens-bert'):
    """
    Loads the fine-tuned BERT model. 
    Tries local path first (for local development), 
    falls back to downloading from Hugging Face Hub (for deployment).
    """
    if not os.path.exists(model_path):
        model_path = snapshot_download(repo_id=hub_repo)
    
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    tokenizer = DistilBertTokenizer.from_pretrained(model_path)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    model.eval()
    
    return model, tokenizer, device


def predict_sentiment_bert(aspect, comment, model, tokenizer, device):
    """Predicts sentiment for a single (aspect, comment) pair using BERT"""
    input_text = f"{aspect} [SEP] {comment}"
    inputs = tokenizer(input_text, truncation=True, padding='max_length', max_length=64, return_tensors='pt')
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=1).item()
    
    return LABEL_NAMES[prediction]