# vrnetlab / ArubaOS-CX (aoscx)

This is the vrnetlab docker image for ArubaOS-CX.

## Building the docker image

Download the OVA image from [Aruba Support Portal](https://asp.arubanetworks.com/downloads/software/RmlsZTpkOGRiYjc2Ni0wMTdkLTExZWUtYTY3Yi00Zjg4YjUyOWExMzQ%3D). Unzip the downloaded zip file and then untar the OVA file to get the vmdk image.
Place the vmdk image into this folder, then run `make docker-image`.

The image will be tagged with the timestamp present in the vmdk file. Optionally you can tag it with the release version of the downloaded software release:

```
docker tag vrnetlab/vr-aoscx:20210610000730 vrnetlab/vr-aoscx:10.07.0010
```

Tested booting and responding to SSH:

* `ArubaOS-CX_10_12_0006.ova` (`arubaoscx-disk-image-genericx86-p4-20230531220439.vmdk`)
* `ArubaOS-CX_10_13_0005.ova` (`arubaoscx-disk-image-genericx86-p4-20231110145644.vmdk`)
* `ArubaOS-CX_10_14_1000.ova` (`arubaoscx-disk-image-genericx86-p4-20240731173624.vmdk`)

## System requirements

CPU: 4 core

RAM: 8GB

Disk: <1GB
