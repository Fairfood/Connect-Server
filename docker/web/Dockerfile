# pull official base image
FROM python:3.10.6-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk add --no-cache bash
RUN apk add --no-cache gcc
RUN apk add --no-cache g++
RUN apk add --no-cache make
RUN apk add --no-cache cmake
RUN apk add --no-cache git

RUN apk add --no-cache libc-dev
RUN apk add --no-cache musl-dev
RUN apk add --no-cache python3-dev
RUN apk add --no-cache libffi-dev
RUN apk add --no-cache openssl-dev

RUN apk add --no-cache jpeg-dev
RUN apk add --no-cache zlib-dev

RUN apk add --no-cache libxslt-dev
RUN apk add --no-cache libxml2-dev

RUN apk add --no-cache postgresql-dev
RUN apk add --no-cache postgresql-client

RUN apk add --no-cache geos-dev

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
ENTRYPOINT ["/usr/src/app/docker/entrypoint.sh"]
