#!/usr/bin/env bash
set -e
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')
SD=/dev/mmcblk0

grep 'Model.*Raspberry Pi' /proc/cpuinfo -c || (
  echo "Not booted in Raspberry pi"; exit 1
  )
echo "Resizing Root partition"

fdisk ${SD}<< EOF
d
2
n
p
2


y
w
EOF

resize2fs ${SD}p2

#timedatectl set-time "2000-01-01 00:00:00"

mkdir -p /sticky_pi_data/images/
mkdir -p /sticky_pi_data/osm/

systemctl disable first_boot
