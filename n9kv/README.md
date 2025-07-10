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

You can retag the image as needed (e.g., `my-repo.example.com/vr-n9kv:9300-10.5.2`) and push it to your own repository.

## System requirements

* CPU: 4 core
* RAM: 10 GB
* Disk: <3GB

