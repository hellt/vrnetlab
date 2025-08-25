# vrnetlab / Juniper vJunosEvolved

This is the vrnetlab docker image for Juniper's vJunosEvolved.

> Available with [containerlab](https://containerlab.dev) as juniper_vjunosevolved.

There are two variants of vJunosEvolved: the default variant, modelling a Juniper BT chipset, and starting with JunosEvo 24.2, a BX variant, modelling a chassis with two Juniper BX chipsets in it.

## Building the docker image

Download the vJunosEvolved .qcow2 image from  <https://www.juniper.net/us/en/dm/vjunos-labs.html>
and place it in this directory. After typing `make`, a new image will appear called `vrnetlab/vjunosevolved`.
Run `docker images` to confirm this.

## System requirements

CPU: 4 cores
RAM: 8GB
DISK: ~2.5GB
