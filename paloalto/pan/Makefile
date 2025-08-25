VENDOR=PaloAlto
NAME=PA-VM
IMAGE_FORMAT=qcow2
IMAGE_GLOB=*.qcow2

# match versions like:
# PA-VNM-KVM-7.0.1.qcow2
# PA-VM-KVM-10.0.6.qcow2
VERSION=$(shell echo $(IMAGE) | sed -re 's/PA-(VM|VNM)-KVM-(.*)\.qcow2/\2/')

-include ../../makefile-sanity.include
-include ../../makefile.include
