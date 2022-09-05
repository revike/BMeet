FROM python:3.10.4
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y postgresql-contrib
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /code/
