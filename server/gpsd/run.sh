#!/bin/bash


#
#gpsd -n -G -D3 -S 2947 -F /var/run/gpsd.sock /dev/ttyUSB0
#status=$?
#if [ $status -ne 0 ]; then
#  echo "Failed to start my_first_process: $status"
#  exit $status
#fi
#
#sleep 5
#
uwsgi --ini uwsgi.ini &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start my_second_process: $status"
  exit $status
fi

while sleep 10; do
  ps aux |grep gpsd |grep -q -v grep
  PROCESS_1_STATUS=$?
  ps aux |grep uwsgi |grep -q -v grep
  PROCESS_2_STATUS=$?
#  if [ $PROCESS_1_STATUS -ne 0 -o $PROCESS_2_STATUS -ne 0 ]; then
#    echo "One of the processes has already exited."
#    exit 1
#  fi
done

