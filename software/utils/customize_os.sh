#!/usr/bin/env bash
set -e
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')

rm /etc/localtime -f
ln -s /usr/share/zoneinfo/UTC /etc/localtime

pacman-key --init
pacman-key --populate
pacman -Syy
pacman -Syu --noconfirm
pacman -S python-pip docker dosfstools devtools \
            chromium firefox gpsd docker-compose\
            libjpeg uboot-tools base-devel parted \
            redis bash-completion --needed --noconfirm

pacman -S xf86-video-fbturbo xorg  xf86-input-evdev  xorg-xinit  --needed --noconfirm
#pacman -Scc --noconfirm
useradd -m  -G video,tty -s /bin/bash  pi
chown -R pi /home/pi/

pip install wheel

cd /opt/sticky_pi_harvester/docker/
for i in $(find . -name 'requirements.txt');
  do pip install -r $i -v;
done

echo '' >> /etc/environment
echo 'REDIS_HOST=localhost' >> /etc/environment
echo 'GPS_HOST=localhost:8080' >> /etc/environment
echo 'MOCK_GPS=0' >> /etc/environment

mkdir /opt/sticky_pi_harvester/docker/api/static/sticky_pi_data -p
ln -s /sticky_pi_data/images  /opt/sticky_pi_harvester/docker/api/static/sticky_pi_data/images

# RTC?

# ntp on gps?
systemctl enable redis
systemctl enable first_boot
systemctl enable  harvester_api
systemctl enable  harvester_gpsd
