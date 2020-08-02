FROM python:3.7

MAINTAINER Martinus <martinuz.dawan9@gmail.com>

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

RUN python -m nltk.downloader punkt

EXPOSE 8089

CMD [ "python3", "src/server.py", "run"]