include ./.env
export

OS_IMG_NAME:=$(shell date "+%Y-%m-%d")_sticky_pi_harvester_${SPI_ARCH}.img

.PHONY: base_os custom_os docker_images
BASE_OS_IMG_NAME:= base-${OS_IMG_NAME}
OSM_SERVER_IMG := osm_tile_server.tar.gz

base_os: ${BASE_OS_IMG_NAME}
custom_os: ${OS_IMG_NAME}.gz

all :${OS_IMG_NAME}.gz


${BASE_OS_IMG_NAME}: utils/make_base_os.sh
	@set +a
	@bash $< || (rm -f tmp-${OS_IMG_NAME}; echo "Failed to make base image!"; exit 1)
	@echo "Made base image $@ !"
	@set -a

$OSM_SERVER_IMG:
	BUILDER=$(docker buildx create --use)
	#docker buildx build  --platform=linux/arm/v7 --output=type=tar,dest=test.tar  -t test:latest  api
	cd docker && docker buildx build --platform=linux/arm/v7 --output=type=docker,dest=osm_server.tar --build-arg OSM_DOWNLOAD_URL=${OSM_DOWNLOAD_URL} -t osm_time_server:latest osm

${OS_IMG_NAME}.gz: utils/emulate_arm.sh  base-${OS_IMG_NAME}
	@set +a
	@bash $<  || (rm -f tmp-${OS_IMG_NAME};  echo "Failed to make final image!"; exit 1)
	@echo "Made final image ${OS_IMG_NAME}! Compressing to $@"
	@gzip ${OS_IMG_NAME} -f
	@set -a


clean:
	rm tmp-*.img -f ${NET_CONF} ${DT_BLOB} ${PYTHON_PACKAGE}
	losetup --detach-all

cleanall: clean
	rm base-*.img spi-*.img  -f


# export $(grep -v '^#' /etc/environment | xargs -d '\r\n');
# pip install  --no-dependencies--force-reinstall --upgrade /opt/sticky_pi/sticky_pi_device.tar.gz
