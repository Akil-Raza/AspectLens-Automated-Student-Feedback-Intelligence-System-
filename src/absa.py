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