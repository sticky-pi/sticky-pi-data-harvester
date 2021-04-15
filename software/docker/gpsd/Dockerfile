FROM python:3.7-alpine
WORKDIR /code


# this is really ugly it's here because we need gcc etc to install uwsgi :-(
RUN set -e; \
	apk add --no-cache --virtual .build-deps \
		gcc \
		libc-dev \
		musl-dev linux-headers  build-base libjpeg-turbo-dev  libpng-dev openblas-dev tiff-dev \
		linux-headers \
		gettext libintl;

RUN apk add --no-cache gpsd gpsd-clients bash
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install  ipython


WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app


CMD ["uwsgi", "--ini", "uwsgi.ini"]
#ADD run.sh /run.sh
#CMD sh /run.sh