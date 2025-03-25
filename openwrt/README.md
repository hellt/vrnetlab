# OpenWRT

This is the vrnetlab Docker image for OpenWRT, designed to be used with containerlab.

## Building the docker image

Run `make build` to automatically download images from the public OpenWRT image
repository and build them into vrnetlab docker images. `build` consists of the
`download` step and `docker-image` step, which can be run separately.

Use `make download` to automatically download images from the public OpenWRT
image repository at <https://downloads.openwrt.org>. The download script will get
everything major and minor version, e.g. 12.09, 14.07, 15.05, 23.05.3 etc.

You can also download images manually by navigating to
<https://downloads.openwrt.org/> and grabbing the file. You have to gunzip it.

Whichever way you get the images, once you have them, run `make docker-image`
to build the docker images. The resulting image is called `vrnetlab/openwrt_openwrt:version`. You can
tag it with something else if you want, like `my-repo.example.com/vr-openwrt`
and then push it to your repo. The tag is the same as the version of the
OpenWRT image, so if you have openwrt-15.05-x86-kvm_guest-combined-ext4.img
your final docker image will be called vr-openwrt:15.05.

As per OpenWRT defaults, `br-lan` (`eth0`) is the LAN interface and eth1 the WAN interface.
During bootstrap, however, the `LAN interface` is reassigned from `eth0` to `eth2`, while `eth0` is reserved and configured as the `management interface`.

Tested booting and responding to SSH:

* openwrt-24.10.0-x86-64-generic-ext4-combined.img MD5:68d7204d3707b629698a011bbfd1e9f1
* openwrt-23.05.5-x86-64-generic-ext4-combined.img MD5:34f6ca5acd50156ce936858a8ff014cf
* openwrt-23.05.3-x86-64-generic-ext4-combined.img MD5:818f6ba04103915ad53f2d003c42aa84
* openwrt-15.05.1-x86-64-combined-ext4.img MD5:307d8cdb11faeb1b5e27fe55078bd152

## Usage

```
docker run -d --privileged --name openwrt1 vrnetlab/openwrt_openwrt:24.10.0
```

### Usage with containerlab

```yaml
name: openwrt

topology:
  nodes:
    openwrt:
      kind: openwrt
      image: vrnetlab/openwrt_openwrt:24.10.0
      mgmt-ipv4: 172.20.20.12                             # optional
      mgmt_ipv6: 2001:172:20:20::12                       # optional
      ports:
        - 8080:80                                         # required for LuCI web interface (HTTP); adjust host ports if running multiple nodes or based on your setup
        - 8443:443                                        # required for LuCI web interface (HTTPS); adjust host ports if running multiple nodes or based on your setup
      env:
        USERNAME: root                                    # default: root
        PASSWORD: mypassword                              # default: VR-netlab9
        CLAB_MGMT_PASSTHROUGH: "false"                    # default: "false"
        PACKET_REPOSITORY_DNS_SERVER: 8.8.8.8             # default 8.8.8.8
        PACKET_REPOSITORY_DOMAINS: "example.com"          # additional repository domains (space-separated); creates a host route via the MGMT interface
        PACKAGES: "tinc htop tcpdump btop luci-proto-gre" # installed on boot if not already present
```

## System requirements

CPU: 1 core

RAM: 128 MB

Disk: 256 MB

## FAQ - Frequently or Unfrequently Asked Questions

### Q: Has this been extensively tested?

A: Not really – but it's great for testing interoperability between OpenWRT and FreeRTR.  
Feel free to take it for a spin and share your feedback! :-)

### Q: What is the MGMT interface?

A: `eth0`

### Q: What is the WAN interface?

A: `eth1`

### Q: What is the LAN interface?

A: `eth2`

### Q: Can the MGMT interface be remapped?

A: No, this is not supported.

### Q: Does my configuration survive a redeploy?

A: Only if you're using the `openwrt` kind or if you're using a bind mount.

### Q: How do I get persistence without using the `openwrt` kind?

A: Use the `linux` kind and bind-mount a volume to `/overlay/`. Make sure the container has write permissions.

### Q: How can I get a shell into OpenWRT?

A: You can use one of the following methods:

* `ssh root@clab-<labname>-<nodename>`
* `telnet clab-<labname>-<nodename> 5000`
* `docker exec -it clab-<labname>-<nodename> telnet localhost 5000`

### Q: How can I access the LuCI web interface?

A: Open [http://127.0.0.1:8080](http://127.0.0.1:8080) or `http://<mgmt-ip>` in your web browser.

### Q: Can automatic package upgrades be disabled?

A: No, but you are welcome to create a pull request (PR) to add that functionality.

### Q: Why are new installed luci-proto not showing up?

A: you need to reload the network process

```
/etc/init.d/network restart
```

### Q: Which connection modes are supported?

A: Currently, only `tc` is supported. But you're welcome to create a pull request (PR) to add support for more connection modes.

### Q: Which is better – transparent or non-transparent MGMT interface?

A: It depends on your use case. The non-transparent mode uses the `10.0.0.0/24` subnet to communicate between QEMU and the VM.

## Q: How many interfaces are supported?

A: Up to 16 by default, but this can be increased if needed using the `NICS` environment variable, e.g. `NICS=32`.

### Q: How to delete all openwrt docker images?

```
docker rmi $(docker images --quiet --filter reference=vrnetlab/openwrt_openwrt)
```