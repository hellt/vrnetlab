VENDOR=cisco
NAME=xrv
IMAGE_FORMAT=qcow2
IMAGE_GLOB=*qcow2
VENDOR_SUBDIR=1

# match versions like:
# iosxrv-k9-demo-6.3.1.qcow2
VERSION=$(shell echo $(IMAGE) | sed -e 's/.\+[^0-9]\([0-9]\+\.[0-9]\+\.[0-9]\+\(\.[0-9A-Z]\+\)\?\)\([^0-9].*\|$$\)/\1/')

-include ../../makefile-sanity.include
-include ../../makefile.include
