FROM python:3.8.6

ADD ./ /twitter_historical

WORKDIR /twitter_historical

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["python","historical_tweets.py"]