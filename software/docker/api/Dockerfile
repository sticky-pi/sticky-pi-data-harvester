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

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install  ipython
RUN mkdir /opt/sticky_pi_data

WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app

RUN ln -s /opt/sticky_pi_data  /app/static/sticky_pi_data


CMD ["uwsgi", "--ini", "uwsgi.ini"]
