# sticky-pi-data-harvester
# Hardware  and Software for the [Sticky Pi](https://sticky-pi.github.io) data harvester

**This readme is intended for contributors and developers**. 
Instructions to assemble Sticky Pis are available on [our documentation](https://doc.sticky-pi.com/hardware.html#data-harvester)

----------------------------- 

## Directory structure

### `hardware/`

#TODO

### `software/` 
Contains files and tools to build the OS for the Data harvester. 
Briefly, we make a local image from the stock Archlinux operating system, 
then we transfer custom files on it before we use QEMU to spawn a virtual machine on this image. Once in the virtual machine, 
we install dependencies and continue the configuration of the virtual image. In the end. We compress the resulting image 
(YYYY-MM-dd_spi_harvester_rpi.img.gz) --that can be burnt and used directly. The whole process is orchestrated by a Makefile 

* `docker` -- A set of docker services (orchestrated by docker compose):
    * `harvester_api` --  A simple flask server that can receives POSTs and GETs requests e.g. from devices (handle image upload and metadata transfer)
    * `redis` --  The stock redis database to share data between service instances
    * `harvester_gpsd` -- A small flask tool that collects and serves GPS data from GPSD (e.g. through using the USB GPS)  
    
* `Makefile` -- A tool to build the full image of a Sticky Pi. Needs to be run as super user under a linux system **at your own risks**.
* `.env` -- Overall configuration file (symlink to `docker/.env`)


To build the image:
```sh
sudo make all
```

