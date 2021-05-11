#! /bin/bash


DEV_1=01234567
DEV_2=abcdef01
DEV_3=56777889

mkdir -p -v  ${SPI_IMAGE_DIR}/${DEV_1}
mkdir -p -v  ${SPI_IMAGE_DIR}/${DEV_2}
mkdir -p -v  ${SPI_IMAGE_DIR}/${DEV_3}

take_picture.py -d -n  -i ${DEV_1} > ${SPI_IMAGE_DIR}/${DEV_1}/sticky_pi.log &&
take_picture.py -d -n -i ${DEV_1} > ${SPI_IMAGE_DIR}/${DEV_1}/sticky_pi.log &&
take_picture.py -d -i ${DEV_1} > ${SPI_IMAGE_DIR}/${DEV_1}/sticky_pi.log

take_picture.py -d -n  -i ${DEV_2} > ${SPI_IMAGE_DIR}/${DEV_2}/sticky_pi.log &&
take_picture.py -d -n -i ${DEV_2} > ${SPI_IMAGE_DIR}/${DEV_2}/sticky_pi.log &&
take_picture.py -d -i ${DEV_2} > ${SPI_IMAGE_DIR}/${DEV_2}/sticky_pi.log



take_picture.py -d -n  -i ${DEV_3} > ${SPI_IMAGE_DIR}/${DEV_3}/sticky_pi.log &&
take_picture.py -d -n -i ${DEV_3}  > ${SPI_IMAGE_DIR}/${DEV_3}/sticky_pi.log  &&
take_picture.py -d -i ${DEV_3}  > ${SPI_IMAGE_DIR}/${DEV_3}/sticky_pi.log