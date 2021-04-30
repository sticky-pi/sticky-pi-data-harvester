#!/usr/bin/env bash
set -e
export $(grep -v '^#' /etc/environment | xargs -d '\r\n')
SD=/dev/mmcblk0

grep 'Model.*Raspberry Pi' /proc/cpuinfo -c || (
  echo "Not booted in Raspberry pi"; exit 1
  )
echo "Resizing Root partition"
resize2fs ${SD}p2||

timedatdtl set-time "2000-01-01 00:00:00"

mkdir -p /sticky_pi_data/images/
mkdir -p /sticky_pi_data/osm/

