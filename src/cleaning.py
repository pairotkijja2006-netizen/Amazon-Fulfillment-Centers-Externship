"""Validate input, clean rows, and prepare text for keyword analysis."""
import re
import pandas as pd
from nltk.corpus import stopwords

GLASSDOOR_FIELDS = ['summary', 'review_pros', 'review_cons']
OPTIONAL_FIELD = 'advice_to_management'
DROP_FIELDS = ['company_name', 'review_advice', 'career_opportunities_rating',
               'count_helpful', 'count_unhelpful', 'flag_covid', 'flag_featured',
               'review_id', 'flags_ceo_approval', 'flags_business_outlook',
               'flags_recommend_frend']
EXTRA_GLASSDOOR_STOPWORDS = {'team', 'company', 'job', 'work', 'employee', 'employees'}


def require_columns(df, columns):
    missing = set(columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")


def load_stopwords():
    try:
        return set(stopwords.words('english'))
    except LookupError as exc:
        raise RuntimeError('Install the NLTK resource: python -m nltk.downloader stopwords') from exc


def normalize_text(value):
    if pd.isna(value):
        return ''
    return re.sub(r'[^\w\s]', ' ', str(value).lower()).strip()


def clean_text(value, stop_words):
    return ' '.join(word for word in normalize_text(value).split() if word not in stop_words)


def valid_text(series):
    return series.notna() & ~series.fillna('').astype(str).str.strip().str.lower().isin(['', 'n/a', '-'])


def clean_glassdoor(df, stop_words):
    require_columns(df, GLASSDOOR_FIELDS + ['employee_job_title', 'employee_status'])
    df = df.drop(columns=DROP_FIELDS, errors='ignore').copy()
    # Exclude missing or placeholder values in the original required fields.
    for column in GLASSDOOR_FIELDS + ['employee_job_title', 'employee_status']:
        df = df.loc[valid_text(df[column])]
    df = df.drop_duplicates().reset_index(drop=True)
    # Keep advice, since the original text-analysis notebooks used it.
    if OPTIONAL_FIELD not in df:
        df[OPTIONAL_FIELD] = ''
    fields = ['summary', OPTIONAL_FIELD, 'review_pros', 'review_cons']
    df['combined_text'] = df[fields].fillna('').astype(str).agg(' '.join, axis=1)
    for column in fields:
        df[f'cleaned_{column}'] = df[column].apply(lambda value: clean_text(value, stop_words))
    df['cleaned_text'] = df['combined_text'].apply(lambda value: clean_text(value, stop_words | EXTRA_GLASSDOOR_STOPWORDS))
    return df


def clean_youtube(df, stop_words):
    require_columns(df, ['Transcript'])
    df = df.loc[valid_text(df['Transcript'])].drop_duplicates().reset_index(drop=True).copy()
    df['transcript_cleaned'] = df['Transcript'].apply(lambda value: clean_text(value, stop_words))
    return df
