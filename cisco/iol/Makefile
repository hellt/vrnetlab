VENDOR=Cisco
NAME=IOL
IMAGE_FORMAT=bin
IMAGE_GLOB=*.bin
DONT_COPY_COMMON=1

# match versions like:
# cisco_iol-17.12.01.bin
# cisco_iol-L2-17.12.01.bin
VERSION=$(shell echo $(IMAGE) | sed -e 's/cisco_iol-\(.*\)\.bin/\1/')

-include ../../makefile-sanity.include
-include ../../makefile.include