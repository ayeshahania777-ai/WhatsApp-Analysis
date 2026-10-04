import re
from collections import Counter

import pandas as pd
import urlextract
import emoji

from wordcloud import WordCloud


# ---------------------------------------------------------
# FILTER DATA ACCORDING TO SELECTED USER
# ---------------------------------------------------------

def filter_user(selected_user, df):

    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    return df


# ---------------------------------------------------------
# TOP STATISTICS
# ---------------------------------------------------------

def fetch_stats(selected_user, df):

    df = filter_user(selected_user, df)

    # Total messages
    num_messages = df.shape[0]

    # Total words
    words = 0

    for message in df['message']:
        words += len(message.split())

    # Media messages
    num_media_messages = df[
        df['message'].str.contains(
            '<Media omitted>',
            case=False,
            na=False
        )
    ].shape[0]

    # Links
    extractor = urlextract.URLExtract()

    links = []

    for message in df['message']:
        links.extend(extractor.find_urls(message))

    num_links = len(links)

    return num_messages, words, num_media_messages, num_links


# ---------------------------------------------------------
# MONTHLY TIMELINE
# ---------------------------------------------------------

def monthly_timeline(selected_user, df):

    df = filter_user(selected_user, df)

    timeline = df.groupby(
        ['year', 'month_num', 'month']
    ).count()['message'].reset_index()

    timeline['time'] = (
        timeline['month'].astype(str)
        + "-"
        + timeline['year'].astype(str)
    )

    return timeline


# ---------------------------------------------------------
# DAILY TIMELINE
# ---------------------------------------------------------

def daily_timeline(selected_user, df):

    df = filter_user(selected_user, df)

    daily = df.groupby(
        'only_date'
    ).count()['message'].reset_index()

    return daily


# ---------------------------------------------------------
# MOST BUSY USERS
# ---------------------------------------------------------

def most_busy_users(df):

    x = df['user'].value_counts()

    percent = round(
        (df['user'].value_counts() / df.shape[0]) * 100,
        2
    ).reset_index()

    percent.columns = ['user', 'percent']

    return x, percent


# ---------------------------------------------------------
# WEEK ACTIVITY MAP
# ---------------------------------------------------------

def week_activity_map(selected_user, df):

    df = filter_user(selected_user, df)

    return df['day_name'].value_counts()


# ---------------------------------------------------------
# MONTH ACTIVITY MAP
# ---------------------------------------------------------

def month_activity_map(selected_user, df):

    df = filter_user(selected_user, df)

    return df['month'].value_counts()


# ---------------------------------------------------------
# ACTIVITY HEATMAP
# ---------------------------------------------------------

def activity_heatmap(selected_user, df):

    df = filter_user(selected_user, df)

    user_heatmap = df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count',
        fill_value=0
    )

    # Keep days in correct order
    day_order = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]

    user_heatmap = user_heatmap.reindex(
        day_order,
        fill_value=0
    )

    return user_heatmap


# ---------------------------------------------------------
# WORD CLOUD
# ---------------------------------------------------------

def create_wordcloud(selected_user, df):

    df = filter_user(selected_user, df)

    # Remove media messages
    text = df[
        ~df['message'].str.contains(
            '<Media omitted>',
            case=False,
            na=False
        )
    ]['message'].str.cat(sep=" ")

    # Remove URLs
    extractor = urlextract.URLExtract()

    urls = extractor.find_urls(text)

    for url in urls:
        text = text.replace(url, "")

    # Generate word cloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        min_font_size=10
    ).generate(text)

    return wordcloud


# ---------------------------------------------------------
# MOST COMMON WORDS
# ---------------------------------------------------------

def most_common_words(selected_user, df):

    df = filter_user(selected_user, df)

    words = []

    for message in df['message']:

        # Remove media messages
        if '<Media omitted>' in message:
            continue

        # Remove URLs
        message = re.sub(
            r'https?://\S+|www\.\S+',
            '',
            message
        )

        # Extract words
        words.extend(
            re.findall(
                r'\b[a-zA-Z]+\b',
                message.lower()
            )
        )

    # Read stop words
    try:

        with open(
            'stop_hinglish.txt',
            'r',
            encoding='utf-8'
        ) as file:

            stop_words = set(
                file.read().splitlines()
            )

    except FileNotFoundError:

        stop_words = set()

    # Common English stop words
    english_stop_words = {
        'the',
        'is',
        'am',
        'are',
        'was',
        'were',
        'a',
        'an',
        'and',
        'or',
        'to',
        'of',
        'in',
        'on',
        'for',
        'with',
        'this',
        'that',
        'it',
        'i',
        'you',
        'he',
        'she',
        'we',
        'they',
        'me',
        'my',
        'your',
        'our',
        'at',
        'be',
        'have',
        'has',
        'had',
        'do',
        'did',
        'will',
        'would',
        'can',
        'could'
    }

    stop_words = stop_words.union(
        english_stop_words
    )

    # Remove stop words
    words = [
        word
        for word in words
        if word not in stop_words
    ]

    # Count words
    most_common = Counter(words).most_common(20)

    result = pd.DataFrame(
        most_common,
        columns=['word', 'count']
    )

    return result


# ---------------------------------------------------------
# EMOJI ANALYSIS
# ---------------------------------------------------------

def emoji_helper(selected_user, df):

    df = filter_user(selected_user, df)

    emojis = []

    for message in df['message']:

        for character in message:

            # Compatible with newer emoji package
            if emoji.is_emoji(character):
                emojis.append(character)

    emoji_df = pd.DataFrame(
        Counter(emojis).most_common(),
        columns=['emoji', 'count']
    )

    return emoji_df