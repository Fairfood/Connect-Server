# pull official base image
FROM python:3.10.6-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update
RUN apk add postgresql-dev
RUN apk add libxslt-dev libxml2-dev libc-dev musl-dev libffi-dev openssl-dev
RUN apk add jpeg-dev zlib-dev
RUN apk add gcc python3-dev
RUN apk add geos-dev
RUN apk add postgresql-client
RUN apk add bash


# install dependencies
RUN pip install --upgrade pip
RUN mkdir req
COPY requirements/* req
RUN pip install -r req/local.txt

# copy project
COPY . .

RUN sed -i 's/\r$//g' /usr/src/app/docker/entrypoint.sh
RUN chmod +x /usr/src/app/docker/entrypoint.sh

# RUN sed -i 's/\r$//g' /usr/src/app/docker/start.sh
# RUN chmod +x /usr/src/app/docker/start.sh


# run entrypoint.sh
#RUN ["chmod", "+x", "/usr/src/app/entrypoint.sh"]
# ENTRYPOINT ["/usr/src/app/docker/entrypoint.sh"]
