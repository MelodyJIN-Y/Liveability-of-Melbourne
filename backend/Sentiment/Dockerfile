FROM python:3.8.6

ADD ./ /sentiment

WORKDIR /sentiment

RUN pip install -r requirements.txt

CMD ["python","-u","sentimental_analysis.py"]