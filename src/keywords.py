"""Unigram, bigram and trigram counts; n-grams stay within each document."""
from collections import Counter
import pandas as pd
from nltk.util import ngrams


def keyword_counts(texts, n=1):
    if n < 1:
        raise ValueError('n must be positive')
    counts = Counter()
    for text in texts.fillna('').astype(str):
        counts.update(' '.join(words) for words in ngrams(text.split(), n))
    return pd.DataFrame(counts.most_common(), columns=['keyword', 'count'])
