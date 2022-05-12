# -----------------------------------------------
# Author        = Xinyi Jin (Melody)
# Date          = 2022-04-28 19:51
# Description   =
# Version       = 2022/4/28
# -----------------------------------------------
import calendar

import pandas as pd
import couchdb
import seaborn as sns
import re
import random
from nltk.corpus import stopwords
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timezone
from matplotlib.ticker import MaxNLocator
import schedule

def get_tweets(db_name):
    """
        Extract the tweet text from given database
        Keyword arguments:
        db_name: the database name, string
    """
    # add username and password
    couch = couchdb.Server('http://172.26.132.125:5984/')
    couch.resource.credentials = ("admin", "admin")

    # read data from database
    db = couch[db_name]

    rows = db.view('_all_docs', include_docs=True)
    data = [row['doc'] for row in rows]

    # select the few latest sample
    selected_data = data
    df = pd.DataFrame(selected_data)

    if "coordinates" in db_name:
        df = df.loc[:, ["text", "author_id", "lang", "created_at", "coordinates"]].dropna()
    else:
        df = df.loc[:, ["text", "author_id", "lang", "created_at"]].dropna()
    df = df.loc[df["lang"] == "en", :]

    # convert date
    def convert_date(dat):
        """
            to extract year-month-day from raw date record
            :param dat: raw date
            :return: formatted date
        """
        # 2022 records
        #print(dat)
        if dat[-1] == "Z":
            output = datetime.fromisoformat(dat[:-1]).astimezone(timezone.utc).strftime('%Y-%m-%d')
        # date format of historical tweet records
        else:
            output = datetime(int(dat.split(" ")[-1]),list(calendar.month_abbr).index(dat.split(" ")[1]),int(dat.split(" ")[2]))
        return output
    df["date"] = df["created_at"].apply(convert_date)
    df["date"] = pd.to_datetime(df["date"], format='%Y-%m-%d')
    return df

def processing_tweet(text):
    """
        Clean the given text
        Keyword arguments:
        text: the text, string
    """
    stop_words = set(stopwords.words('english'))
    words = set(nltk.corpus.words.words())

    # Remove @ sign
    text = re.sub("@[A-Za-z0-9]+", "", text)
    # Remove http links
    text = re.sub(r'http\S+', '', text)
    text = " ".join(text.split())
    # Remove hashtag sign
    text = text.replace("#", "")
    # convert underscores
    text = text.replace("_", " ")
    # join the processed text
    text = " ".join(w for w in nltk.wordpunct_tokenize(text)
                     if (w.lower() not in stop_words) and (w.lower() in words or not w.isalpha()))
    return text

def get_sentiment_label(df, text_column_name):
    """
        Calculate the polarity score of each tweet text in the given dataframe
        Keyword arguments:
        df: a dataframe which contains a column tweet text
        text_column_name: the name of the column with tweet text
    """
    # pre-process the tweet text
    df['text_processed'] = df[text_column_name].apply(processing_tweet)
    df['polarity'] = 0
    df['label'] = "Neutral"
    analyzer = SentimentIntensityAnalyzer()
    for i in range(df.shape[0]):
        score = (analyzer.polarity_scores(str(df.iloc[i, list(df.columns).index('text_processed')])))['compound']
        df.iloc[i, list(df.columns).index('polarity')] = score
        if score != 0:
            df.iloc[i, list(df.columns).index('label')] = "Positive" if score > 0 else "Negative"
    df["label"] = df["label"].astype("category")
    return df


# do sentimental analysis and draw plots
def env_sentiment_analysis():

    raw_df = get_tweets(db_name="environment_tweets_text")
    df = get_sentiment_label(df=raw_df, text_column_name="text")
    print(df.label.value_counts())
    # Positive    248
    # Neutral      97
    # Negative     76
    df2 = df[df["date"]>"2022-01-01"]
    df2 = df2[["text_processed","label","date"]].groupby(["date","label"]).count().reset_index()

    
    plt.figure(figsize=(12,8))
    sns.lineplot(data=df2, x="date", y="text_processed", hue="label")
    plt.savefig("./static/env_sentiment_vs_time.png")

    positive = df[df['label']=='Positive']
    wordcloud = WordCloud(max_font_size=50, max_words=500, background_color="white").generate(str(positive['text_processed']))
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig("./static/env_word_cloud.png")

    return df


def health_sentiment_analysis():

    raw_df = get_tweets(db_name="health_tweets_text")
    df = get_sentiment_label(df=raw_df, text_column_name="text")
    # print(df.label.value_counts())
    print(df)
    # Positive    248
    # Neutral      97
    # Negative     76
    df2 = df[df["date"]>"2022-01-01"]
    df2 = df2[["text_processed","label","date"]].groupby(["date","label"]).count().reset_index()

    
    plt.figure(figsize=(12,8))
    sns.lineplot(data=df2, x="date", y="text_processed", hue="label")
    plt.savefig("./static/health_sentiment_vs_time.png")

    positive = df[df['label']=='Positive']
    wordcloud = WordCloud(max_font_size=50, max_words=500, background_color="white").generate(str(positive['text_processed']))
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig("./static/health_word_cloud.png")

    return df


# do sentimental analysis and draw plots
def env_coords_sentimental_analysis():

    raw_df = get_tweets(db_name="environment_tweets_text")
    df = get_sentiment_label(df=raw_df, text_column_name="text")
    # Positive    248
    # Neutral      97
    # Negative     76

    df.to_json('./static/env_sent.json')
    return df


def health_coords_sentiment_analysis():

    raw_df = get_tweets(db_name="health_tweets_text")
    df = get_sentiment_label(df=raw_df, text_column_name="text")
    # print(df.label.value_counts())
    # Positive    248
    # Neutral      97
    # Negative     76
    df.to_json('./static/health_sent.json')
    return df

