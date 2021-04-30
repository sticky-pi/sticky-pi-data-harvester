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
RUN mkdir /sticky_pi_data/images -p

WORKDIR /app
# Copy the current directory contents into the container at /app
COPY . /app

RUN mkdir /app/static/sticky_pi_data
RUN ln -s /sticky_pi_data/images  /app/static/sticky_pi_data/images

CMD ["uwsgi", "--ini", "uwsgi.ini"]
