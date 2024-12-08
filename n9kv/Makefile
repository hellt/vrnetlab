VENDOR=Cisco
NAME=n9kv
IMAGE_FORMAT=qcow2
IMAGE_GLOB=*.qcow2

# rename the disk image file as n9kv-<version>.qcow2
# examples:
# for a file named "n9kv-9300-10.5.2.qcow2" the image will be named "vrnetlab/cisco_n9kv:9300-10.5.2"
VERSION=$(shell echo $(IMAGE) | sed -e 's/n9kv-\(.*\)\.qcow2/\1/')

-include ../makefile-sanity.include
-include ../makefile.include
