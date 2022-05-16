FROM python:3.8.6

ADD ./ /aurin

WORKDIR /aurin

RUN pip install -r requirements.txt

CMD ["python","write_AURIN_couchdb.py"]