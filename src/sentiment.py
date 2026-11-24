"""TextBlob polarity, subjectivity and threshold-based labels."""
import pandas as pd
from textblob import TextBlob


def label_sentiment(score):
    if score > 0.1:
        return 'positive'
    if score < -0.1:
        return 'negative'
    return 'neutral'


def score_sentiment(df, text_column):
    df = df.copy()
    # Keep negation and punctuation intact for sentiment, rather than using the
    # stopword-filtered text used for keyword counts.
    scores = df[text_column].fillna('').astype(str).map(lambda text: TextBlob(text).sentiment)
    df['sentiment_polarity'] = scores.map(lambda score: score.polarity)
    df['sentiment_subjectivity'] = scores.map(lambda score: score.subjectivity)
    df['sentiment_label'] = df['sentiment_polarity'].map(label_sentiment)
    return df


def combine_datasets(glassdoor, youtube):
    columns = ['cleaned_text', 'sentiment_polarity', 'sentiment_subjectivity', 'sentiment_label']
    glassdoor = glassdoor.assign(analysis_text=glassdoor['combined_text'], platform='Glassdoor')
    columns += ['platform', 'analysis_text']
    if youtube is None:
        return glassdoor[columns].reset_index(drop=True)
    youtube = youtube.rename(columns={'transcript_cleaned': 'cleaned_text'}).assign(
        analysis_text=youtube['Transcript'], platform='YouTube')
    return pd.concat([glassdoor[columns], youtube[columns]], ignore_index=True)
