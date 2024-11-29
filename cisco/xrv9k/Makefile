VENDOR=cisco
NAME=xrv9k
IMAGE_FORMAT=qcow2
IMAGE_GLOB=*.qcow2
INSTALL=true
VENDOR_SUBDIR=1

# match versions like:
# TODO: add example file names here
# xrv9k-fullk9-x.vrr-6.1.3.qcow2
# xrv9k-fullk9-x.vrr-6.2.1.qcow2
# xrv9k-fullk9-x-7.10.1.qcow2
VERSION=$(shell echo $(IMAGE) | sed -e 's/.\+[^0-9]\([0-9]\+\.[0-9]\+\.[0-9]\+\(\.[0-9A-Z]\+\)\?\)\([^0-9].*\|$$\)/\1/')

-include ../../makefile-sanity.include
-include ../../makefile.include

ifeq ($(INSTALL),false)
$(info Install mode disabled)
else
$(info Install mode enabled)
docker-pre-build:
	-cat cidfile | xargs --no-run-if-empty docker rm -f
	-rm cidfile

docker-build: docker-build-common
	docker run --cidfile cidfile --privileged $(REGISTRY)$(VENDOR)_$(NAME):$(VERSION) --trace --install
	docker commit --change='ENTRYPOINT ["/launch.py"]' $$(cat cidfile) $(REGISTRY)$(VENDOR)_$(NAME):$(VERSION)
	docker rm -f $$(cat cidfile)
endif

