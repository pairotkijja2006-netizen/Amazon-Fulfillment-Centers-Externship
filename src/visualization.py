"""Save reproducible charts without requiring an interactive notebook."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud


def save_figure(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def sentiment_charts(df, platform, output):
    counts = df['sentiment_label'].value_counts().reindex(['positive', 'neutral', 'negative'], fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 5))
    counts.plot.bar(ax=ax, rot=0)
    ax.set(title=f'{platform} Sentiment Distribution', xlabel='Sentiment', ylabel='Number of records')
    save_figure(fig, output / 'sentiment_bar.png')
    if counts.sum():
        fig, ax = plt.subplots(figsize=(6, 6))
        counts[counts > 0].plot.pie(ax=ax, autopct='%1.1f%%', ylabel='')
        ax.set_title(f'{platform} Sentiment Breakdown')
        save_figure(fig, output / 'sentiment_pie.png')


def keyword_chart(table, platform, n, output):
    top = table.head(10)
    if top.empty:
        return
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(top['keyword'], top['count'])
    ax.set(title=f'{platform}: Top 10 { {1: "Unigrams", 2: "Bigrams", 3: "Trigrams"}[n]}', xlabel='Keyword', ylabel='Frequency')
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    save_figure(fig, output / f'top_{n}gram.png')


def word_cloud(table, platform, output):
    if table.empty:
        return
    cloud = WordCloud(width=800, height=400, background_color='white', max_words=100, random_state=42)
    cloud.generate_from_frequencies(dict(zip(table['keyword'], table['count'])))
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(cloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f'{platform} Keyword Word Cloud')
    save_figure(fig, output / 'wordcloud.png')
