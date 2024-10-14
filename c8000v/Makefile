VENDOR=cisco
NAME=c8000v
IMAGE_FORMAT=qcow2
IMAGE_GLOB=*.qcow2

# match versions like:
# c8000v-17.11.01a.qcow2
VERSION=$(shell echo $(IMAGE) | sed -e 's/.\+[^0-9]\([0-9]\+\.[0-9]\+\.[0-9]\+[a-z]\?\)\([^0-9].*\|$$\)/\1/')

-include ../makefile-sanity.include
-include ../makefile.include
-include ../makefile-install.include

docker-build: docker-build-common
	docker run --cidfile cidfile --privileged $(REGISTRY)$(VENDOR)_$(NAME):$(VERSION) --trace --install
	docker commit --change='ENTRYPOINT ["/launch.py"]' $$(cat cidfile) $(REGISTRY)$(VENDOR)_$(NAME):$(VERSION)
	docker rm -f $$(cat cidfile)
