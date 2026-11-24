"""Multi-label, rule-based theme tagging using the original keyword lists."""
import re
import pandas as pd
from .cleaning import normalize_text

THEME_KEYWORDS = {
    'Physical Exhaustion and Burnout': [
        'physical', 'exhaustion', 'exhausted', 'exhausting', 'burnout', 'burned', 'tired',
        'fatigue', 'fatigued', 'standing', 'walking', 'lifting', 'heavy', 'pallet', 'jack',
        'pallet jack', 'hauling', 'bins', 'totes', 'repetitive', 'body', 'feet', 'pain',
        'sore', 'strain', 'long hours', 'recovery'],
    'Pressure from Productivity Targets and Micromanagement': [
        'productivity', 'target', 'targets', 'rate', 'rates', 'speed', 'fast', 'fastpaced',
        'fast paced', 'quota', 'quotas', 'metrics', 'performance', 'warning', 'warnings',
        'writeup', 'write up', 'monitored', 'monitoring', 'tracked', 'tracking', 'micromanage',
        'micromanaged', 'micromanagement', 'pressure', 'efficiency', 'output', 'autonomy'],
    'Feeling Replaceable and Undervalued': [
        'replaceable', 'number', 'numbers', 'undervalued', 'unappreciated', 'not valued',
        'treated like', 'human', 'people', 'empathy', 'care', 'cares', 'wellbeing', 'well being',
        'support', 'morale', 'anxiety', 'anxious', 'stress', 'stressful', 'disposable',
        'operations', 'ignored', 'management doesnt care', 'management does not care'],
    'Pay and Benefits as a Key Motivation': [
        'pay', 'paid', 'wage', 'wages', 'salary', 'compensation', 'money', 'benefit', 'benefits',
        'insurance', 'health insurance', 'holiday pay', 'bonus', 'bonuses', 'financial',
        'income', 'competitive', 'reliable', 'attractive', 'overtime pay'],
    'Mixed Views on Scheduling and Work-Life Balance': [
        'schedule', 'scheduling', 'shift', 'shifts', 'flexible', 'flexibility', 'flex', 'hours',
        'long shift', 'long shifts', 'mandatory', 'mandatory hours', 'overtime', 'night shift',
        'weekend', 'weekends', 'worklife', 'work life', 'balance', 'rest', 'time off',
        'day off', 'days off', 'break', 'breaks', 'control over time'],
}
PATTERNS = {theme: re.compile(r'(?<!\w)(?:' + '|'.join(re.escape(word) for word in words) + r')(?!\w)')
            for theme, words in THEME_KEYWORDS.items()}


def tag_themes(text):
    text = ' '.join(normalize_text(text).split())
    return [theme for theme, pattern in PATTERNS.items() if pattern.search(text)] or ['No Theme Tagged']


def analyze_themes(df):
    df = df.copy()
    tags = df['analysis_text'].map(tag_themes)
    df['Theme'] = tags.map(', '.join)
    # Count individual themes rather than treating each combination as one theme.
    expanded = df[['platform']].assign(theme=tags).explode('theme')
    counts = expanded['theme'].value_counts().rename_axis('theme').reset_index(name='count')
    by_platform = pd.crosstab(expanded['platform'], expanded['theme'])
    return df, counts, by_platform
