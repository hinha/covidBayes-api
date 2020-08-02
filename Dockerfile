FROM python:3.7

MAINTAINER Martinus <martinuz.dawan9@gmail.com>

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

EXPOSE 8089

CMD [ "python3", "src/server.py", "run"]