"""Run the complete workforce feedback analysis pipeline."""
import argparse
from pathlib import Path
import pandas as pd
from src.cleaning import clean_glassdoor, clean_youtube, load_stopwords
from src.sentiment import score_sentiment, combine_datasets
from src.keywords import keyword_counts
from src.themes import analyze_themes
from src.visualization import sentiment_charts, keyword_chart, word_cloud


def run(glassdoor_path, youtube_path, output_path, stop_words=None):
    output = Path(output_path)
    output.mkdir(parents=True, exist_ok=True)
    stop_words = load_stopwords() if stop_words is None else set(stop_words)
    glassdoor_raw = pd.read_csv(glassdoor_path)
    youtube_raw = pd.read_csv(youtube_path) if youtube_path is not None else None
    glassdoor = clean_glassdoor(glassdoor_raw, stop_words)
    youtube = clean_youtube(youtube_raw, stop_words) if youtube_raw is not None else None
    glassdoor.to_csv(output / 'glassdoor_cleaned.csv', index=False)
    if youtube is not None:
        youtube.to_csv(output / 'youtube_cleaned.csv', index=False)
    glassdoor = score_sentiment(glassdoor, 'combined_text')
    platforms = [('Glassdoor', glassdoor, 'cleaned_text')]
    if youtube is not None:
        youtube = score_sentiment(youtube, 'Transcript')
        platforms.append(('YouTube', youtube, 'transcript_cleaned'))
    for platform, df, column in platforms:
        folder = output / platform.lower()
        folder.mkdir(exist_ok=True)
        df.to_csv(folder / 'sentiment.csv', index=False)
        sentiment_charts(df, platform, folder)
        for n in (1, 2, 3):
            counts = keyword_counts(df[column], n)
            counts.to_csv(folder / f'{n}gram_counts.csv', index=False)
            keyword_chart(counts, platform, n, folder)
            if n == 1:
                word_cloud(counts, platform, folder)
    combined = combine_datasets(glassdoor, youtube)
    combined.to_csv(output / 'combined_sentiment.csv', index=False)
    tagged, counts, by_platform = analyze_themes(combined)
    tagged.to_csv(output / 'combined_with_themes.csv', index=False)
    counts.to_csv(output / 'theme_counts.csv', index=False)
    by_platform.to_csv(output / 'themes_by_platform.csv')
    pd.crosstab(combined['platform'], combined['sentiment_label']).to_csv(output / 'sentiment_by_platform.csv')
    print(f'Glassdoor: {len(glassdoor_raw)} input rows -> {len(glassdoor)} cleaned rows')
    if youtube is not None:
        print(f'YouTube: {len(youtube_raw)} input rows -> {len(youtube)} cleaned rows')
    else:
        print('YouTube: skipped (no transcript dataset supplied)')
    print(f'Results saved to {output}')
    return tagged


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--glassdoor', required=True, type=Path, help='Path to Glassdoor CSV')
    parser.add_argument('--youtube', type=Path, help='Optional path to YouTube CSV; omit for Glassdoor-only analysis')
    parser.add_argument('--offline-stopwords', action='store_true', help='Use WordCloud stopwords instead of NLTK (different keyword counts)')
    parser.add_argument('--output', default=Path('outputs'), type=Path)
    args = parser.parse_args()
    if args.offline_stopwords:
        from wordcloud import STOPWORDS
        print('Using WordCloud stopwords; keyword counts may differ from NLTK.')
        run(args.glassdoor, args.youtube, args.output, stop_words=STOPWORDS)
    else:
        run(args.glassdoor, args.youtube, args.output)
