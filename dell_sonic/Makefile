VENDOR=Dell
NAME=sonic
IMAGE_FORMAT=qcow
IMAGE_GLOB=*.qcow2

# rename the disk image file as dell-sonic-<version>.qcow2
# examples:
# for a file named "dell-sonic-4.2.1.qcow2" the image will be named "vrnetlab/dell_sonic:4.2.1"
VERSION=$(shell echo $(IMAGE) | sed -e 's/dell-sonic-//' | sed -e 's/.qcow2//')

-include ../makefile-sanity.include
-include ../makefile.include
