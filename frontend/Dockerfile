FROM python:3.8.6

ADD ./ /frontend

WORKDIR /frontend

RUN pip install -r requirements.txt

CMD ["python","-u","app.py"]