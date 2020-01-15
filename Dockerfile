FROM python:3.6.8-alpine

LABEL Squad42 project: image for UserManagement microservice

COPY userManagement/ /userManagement
COPY requirements.txt /userManagement/
WORKDIR /userManagement/


RUN pip3 install --upgrade pip

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

RUN pip3 install -r requirements.txt

EXPOSE 5005

ENV FLASK_APP=server.py
CMD ["python3","-m","flask","run", "--host", "0.0.0.0", "--port", "5005"]
