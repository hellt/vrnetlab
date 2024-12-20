VENDOR=Cisco
NAME=vIOSL2
IMAGE_FORMAT=qcow2
IMAGE_GLOB=*.qcow2

# Match images like:
# - cisco_viosl2-15.2.qcow2
# Extract version, for example: 15.2
VERSION=$(shell echo $(IMAGE) | sed -e 's/cisco_viosl2-\(.*\)\.qcow2/\1/')

-include ../makefile-sanity.include
-include ../makefile.include
