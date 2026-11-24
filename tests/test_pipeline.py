import pandas as pd
from src.cleaning import clean_glassdoor, clean_text
from src.sentiment import label_sentiment, score_sentiment
from src.keywords import keyword_counts
from src.themes import tag_themes, analyze_themes
from main import run
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_cleaning():
    assert clean_text('THE, good day!', {'the'}) == 'good day'
    df = pd.read_csv(ROOT / 'data/glassdoor_sample.csv')
    data = pd.concat([df, df.iloc[[0]], df.iloc[[1]].assign(summary='-')], ignore_index=True)
    assert len(clean_glassdoor(data, {'the'})) == len(df)


def test_sentiment_thresholds():
    assert [label_sentiment(n) for n in [-0.11, -0.1, 0, 0.1, 0.11]] == ['negative', 'neutral', 'neutral', 'neutral', 'positive']
    scored = score_sentiment(pd.DataFrame({'text': ['I love this!', 'I hate this!']}), 'text')
    assert list(scored.sentiment_label) == ['positive', 'negative']


def test_ngrams_do_not_cross_documents():
    result = keyword_counts(pd.Series(['one two', 'three four']), 2)
    assert set(result.keyword) == {'one two', 'three four'}


def test_theme_boundaries_and_multilabel():
    assert tag_themes('pirate') == ['No Theme Tagged']
    assert len(tag_themes('heavy lifting and pay')) == 2
    df = pd.DataFrame({'platform': ['Glassdoor'], 'analysis_text': ['heavy lifting and pay']})
    _, counts, _ = analyze_themes(df)
    assert counts['count'].sum() == 2


def test_end_to_end_synthetic(tmp_path):
    # Inject a small test stopword set so tests do not require a network download.
    result = run(ROOT / 'data/glassdoor_sample.csv', ROOT / 'data/youtube_sample.csv', tmp_path,
                 stop_words={'the', 'a', 'and', 'is', 'this', 'i', 'to', 'was', 'but'})
    assert len(result) == 7
    assert set(result.platform) == {'Glassdoor', 'YouTube'}
    assert (tmp_path / 'combined_with_themes.csv').exists()
    assert (tmp_path / 'glassdoor' / 'wordcloud.png').exists()
