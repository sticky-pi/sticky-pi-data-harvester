FROM python:3.7-alpine

WORKDIR /code

# this is really ugly it's here because we need gcc etc to install uwsgi :-(
RUN set -e; \
	apk add --no-cache --virtual .build-deps \
		gcc \
		libc-dev \
		musl-dev linux-headers  build-base libjpeg-turbo-dev  libpng-dev openblas-dev tiff-dev \
		linux-headers \
		gettext libintl coreutils;
# preinstall deps to save time
RUN pip install netifaces pillow rpi-ws281x piexif pytz
COPY sticky_pi_device.tar.gz sticky_pi_device.tar.gz

#fixme should dl deps -- was remove for offline work
RUN pip install sticky_pi_device.tar.gz #--no-dependencies

RUN echo "#!/bin/sh" >  /bin/timedatectl && echo 'echo "MOCK timedatectl"' >>  /bin/timedatectl && chmod 777 /bin/timedatectl
COPY test_spi_device.sh test_spi_device.sh
CMD ["sh", "test_spi_device.sh"]
