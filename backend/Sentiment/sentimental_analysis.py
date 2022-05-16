# -----------------------------------------------
# Author        = Xinyi Jin (Melody)
# Date          = 2022-05-12 16:23
# Description   = sentimental analysis for tweets
# Version       = 2022/5/12   
# -----------------------------------------------
import base64
import calendar

import pandas as pd
import couchdb
import re
import nltk
#nltk.download('popular')
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('words')
import time
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud
from datetime import datetime
from datetime import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from CouchDB_functions import *

def get_tweets(db_name):
    """
        Extract the tweet text from given database
        Keyword arguments:
        db_name: the database name, string
    """
    # add username and password
    couch = open_couchdb()

    # read data from database
    db = couch[db_name]
    get_tweet_time = time.time()
    rows = db.view('_all_docs', include_docs=True)
    data = [row['doc'] for row in rows]
    df = pd.DataFrame(data)

    if "text" in db_name:
        df = df.loc[:, ["text", "author_id", "lang", "created_at", "_id"]].dropna()
    else:
        df = df.loc[:, ["text", "author_id", "lang", "created_at", "_id", "coordinates"]].dropna()
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
            output = datetime(int(dat.split(" ")[-1]),
                              list(calendar.month_abbr).index(dat.split(" ")[1]),
                              int(dat.split(" ")[2]))
        return output
    df["date"] = df["created_at"].apply(convert_date)
    df["date"] = pd.to_datetime(df["date"], format='%Y-%m-%d')
    print(str(datetime.utcnow()))
    print("--- Time to get",str(db_name),"tweets: ", str( round((time.time() - get_tweet_time),2)),"s ---" )
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

def get_sentiment_label(df, text_column_name,db_name):
    """
        Calculate the polarity score of each tweet text in the given dataframe
        Keyword arguments:
        df: a dataframe which contains a column tweet text
        text_column_name: the name of the column with tweet text
        db_name: the database name to store the sentimental labels
    """
    # pre-process the tweet text
    df['text_processed'] = df[text_column_name].apply(processing_tweet)
    df['polarity'] = 0
    df['label'] = "Neutral"
    analyzer = SentimentIntensityAnalyzer()
    couch = open_couchdb()
    db = couch[db_name + "_sentiment"]

    get_label_time = time.time()
    for i in range(df.shape[0]):
        # determine whether the _id has already had sentiment analysis
        # if exists, do not need to analyze again
        unique_id = db.view('_design/tweet_id/_view/unique_id', reduce=True, group=True, descending=True)
        collected_ids = [p.key for p in unique_id]
        key = df.iloc[i, list(df.columns).index('_id')]
        if key in collected_ids:
            continue

        score = (analyzer.polarity_scores(str(df.iloc[i, list(df.columns).index('text_processed')])))['compound']
        df.iloc[i, list(df.columns).index('polarity')] = score
        if score != 0:
            df.iloc[i, list(df.columns).index('label')] = "Positive" if score > 0 else "Negative"

        if "text" in db_name:
            record = {"_id": str(df.iloc[i, list(df.columns).index('_id')]),
                      "label": str(df.iloc[i, list(df.columns).index('label')]),
                      "date": str(df.iloc[i, list(df.columns).index('date')]),
                      'text_processed': str(df.iloc[i, list(df.columns).index('text_processed')])}
        else:
            record = {"_id": str(df.iloc[i, list(df.columns).index('_id')]),
                      "label": str(df.iloc[i, list(df.columns).index('label')]),
                      "date": str(df.iloc[i, list(df.columns).index('date')]),
                      "coordinates": df.iloc[i, list(df.columns).index("coordinates")]}
        write_data_to_db(destination=db_name + "_sentiment", record=record)
    print(str(datetime.utcnow()))
    print("--- Time to process", str(db_name), "tweets: ", str( round((time.time() - get_label_time)/60,2)), "min ---")


def get_wordcloud_plot(df,text_column_name,db_name):
    # store sentiment analysis to CouchDB
    get_sentiment_label(df, text_column_name,db_name)

    # get all sentiment label and processed text
    couch = open_couchdb()

    # read data from database
    db = couch[db_name+"_sentiment"]
    rows = db.view('_all_docs', include_docs=True)
    data = [row['doc'] for row in rows]
    df = pd.DataFrame(data)

    positive = df[df['label'] == 'Positive']
    draw_wc_pfig = time.time()
    wc_fig = WordCloud(max_font_size=50, max_words=500, background_color="white").generate(
        str(positive['text_processed']))
    wc_fig.to_file("wc_fig.png")
    print(str(datetime.utcnow()))
    print("--- Time to draw wordcloud figure for", str(db_name), "tweets: ", str(round((time.time() - draw_wc_pfig),2)), "s ---")

    record = {"_id": str(datetime.utcnow()), "name": "wordcloud"}
    write_data_to_db(destination=db_name+"_wordcloud", record=record)
    couch = open_couchdb()
    db = couch[db_name+"_wordcloud"]
    f = open("wc_fig.png", "rb")
    db.put_attachment(doc=record, content=f, filename="wc_fig.png", content_type="image/png")


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    db_list = ["environment_tweets_text", "health_tweets_text",
               "environment_tweets_coordinates", "health_tweets_coordinates"]
    for database in db_list:
        if "text" in database:
            get_wordcloud_plot(get_tweets(db_name=database),"text", database)
            scheduler.add_job(func=get_wordcloud_plot, args=[get_tweets(db_name=database),
                                                             "text", database],
                              trigger='interval', hours=6, misfire_grace_time=3600)
        else:
            get_sentiment_label(get_tweets(db_name=database),"text", database)
            scheduler.add_job(func=get_sentiment_label, args=[get_tweets(db_name=database),
                                                              "text", database],
                              trigger='interval', hours=6, misfire_grace_time=3600)
    print(str(datetime.utcnow()))
    print("scheduler starts---")
    scheduler.start()
