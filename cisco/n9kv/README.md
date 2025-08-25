# Cisco Nexus 9000v / n9kv

This is the vrnetlab docker image for Cisco Nexus 9000v virtual switch.

## Building the docker image

1. Place your Cisco Nexus 9000v qcow2 image in this directory. **The filename must follow the format:**

   ```
   n9kv-<version>.qcow2
   ```

   For example: `n9kv-9300-10.5.2.qcow2`

2. Run `make docker-image`.

The resulting Docker image will be named:

```
vrnetlab/cisco_n9kv:<version>
```

For the example above, the image will be `vrnetlab/cisco_n9kv:9300-10.5.2`.

You can re-tag the image as needed (e.g., `my-repo.example.com/vr-n9kv:9300-10.5.2`) and push it to your own repository.

## System requirements

* CPU: 4 core
* RAM: 10 GB
* Disk: <3GB

## Extracting qcow2 disk image from a container image

It is possible to extract the original qcow2 disk image from an existing container image. This might be useful when you want to rebuild the container image with a different vrnetlab release.

The following script takes an image name and the qcow2 image name to copy out from the container image:

```bash
IMAGE=registry.srlinux.dev/pub/cisco_n9kv:9300-10.5.2
VERSION=$(cut -d ':' -f 2 <<< $IMAGE)
docker create --name image-copy $IMAGE
docker cp image-copy:n9kv-$VERSION.qcow2 .
docker rm image-copy
```
