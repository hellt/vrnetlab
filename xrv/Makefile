VENDOR=Cisco
NAME=XRv
IMAGE_FORMAT=vmdk
IMAGE_GLOB=*vmdk*
QCOW=$(shell ls *qcow2* 2>/dev/null)

# match versions like:
# iosxrv-k9-demo-5.3.3.51U.vmdk
# iosxrv-k9-demo-6.1.2.vmdk
# iosxrv-k9-demo-6.2.2.15I.DT_IMAGE.vmdk
# iosxrv-k9-demo-6.2.2.1T-dhcpfix.vmdk
# iosxrv-k9-demo-6.2.2.22I.vmdk
VERSION=$(shell echo $(IMAGE) | sed -e 's/.\+[^0-9]\([0-9]\+\.[0-9]\+\.[0-9]\+\(\.[0-9A-Z]\+\)\?\)\([^0-9].*\|$$\)/\1/')

-include ../makefile-sanity.include
-include ../makefile.include

convert-image:
	@if [ -z "$QCOW" ]; then echo "\033[1;31mERROR:\033[0m No .qcow2 image found"; exit 1; fi
	@printf "\033[1;32mFound image $(QCOW)\033[0m.\n"
ifeq (, $(shell which qemu-img))
	@printf "\033[1;31mERROR\033[0m: qemu-img not found. Please install 'qemu-img' or 'qemu-utils'.\n"; exit 1;
endif
	$(eval FILE_NAME := $(shell basename $(QCOW) .qcow2))
	qemu-img convert -cpf qcow2 -O vmdk $(QCOW) $(FILE_NAME).vmdk


