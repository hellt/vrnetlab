VENDOR=Extreme
NAME=EXOS
IMAGE_FORMAT=qcow2
IMAGE_GLOB=*.qcow2

# match versions like:
# v15.3.2.11
VERSION=$(shell echo $(IMAGE) | sed -n 's/^EXOS-VM_\(.*\)\.qcow.*/\1/p' | cut -d'-' -f1)

-include ../makefile-sanity.include
-include ../makefile.include
