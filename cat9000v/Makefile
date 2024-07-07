VENDOR=Cisco
NAME=cat9000v
IMAGE_FORMAT=qcow2
IMAGE_GLOB=*.qcow2

# match versions like:
# cat9kv-prd-17.12.01prd9.qcow2
VERSION=$(shell echo $(IMAGE) | sed -e 's/.\+[^0-9]\([0-9]\+\.[0-9]\+\.[0-9]\+[a-z]\?\)\([^0-9].*\|$$\)/\1/')

-include ../makefile-sanity.include
-include ../makefile.include
-include ../makefile-install.include

docker-build: docker-build-common
	docker run --cidfile cidfile --privileged $(REGISTRY)vr-$(VR_NAME):$(VERSION) --trace --install
	docker commit --change='ENTRYPOINT ["/launch.py"]' $$(cat cidfile) $(REGISTRY)vr-$(VR_NAME):$(VERSION)
	docker rm -f $$(cat cidfile)
