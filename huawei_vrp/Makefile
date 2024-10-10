VENDOR=Huawei
NAME=VRP
IMAGE_FORMAT=qcow2
IMAGE_GLOB=*.qcow2

# match versions like:
# huawei_ne40e-<any version string>.qcow2
# huawei_ce12800-<any version string>.qcow2
VERSION=$(shell echo $(IMAGE) | sed -e 's/huawei_\(ne40e\|ce12800\)-\(.*\)\.qcow2/\1-\2/')

-include ../makefile-sanity.include
-include ../makefile.include
