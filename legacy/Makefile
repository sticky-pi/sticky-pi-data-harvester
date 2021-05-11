# A makefile to upload the code directly through command line.
# For development / if you know what you are doing

FQBN := arduino:avr:nano:cpu=atmega328
PORT := /dev/ttyUSB0
SKETCH_NAME := arduino

SUFFIX := $(subst :,.,$(FQBN))
ELF_FILE := $(SKETCH_NAME)/$(SKETCH_NAME).$(SUFFIX).elf

compile: $(ELF_FILE)

$(ELF_FILE) : $(SKETCH_NAME)/$(SKETCH_NAME).ino
	arduino-cli  compile -p $(PORT)  --fqbn  $(FQBN)  $(SKETCH_NAME)

upload: compile
	arduino-cli  upload -p $(PORT)  --fqbn  $(FQBN)  $(SKETCH_NAME) -v


clean:
	rm  $(SKETCH_NAME)/*.hex  $(SKETCH_NAME)/*.elf -f

