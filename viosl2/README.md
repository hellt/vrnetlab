# Cisco vIOS L2

This is the vrnetlab docker image for Cisco vIOS L2 switch. Everything is based on the vios vrnetlab router files and
modified to support the vIOS L2 image.

## Justification

Cisco vIOS L2 is a virtual switch that can be used for testing and development purposes.
It is older than IOL L2 (running only 15.x IOS version), however, it has several advantages:

- Small memory footprint (768MB vs 4GB+ for IOS XE). With KSM enabled, the memory usage can be even lower.
- Easy to run on a laptop or a small server with limited resources for education purposes.
- Good for scalability testing of applications, when you don't need all new features of IOS XE.

## Building the docker image

Qemu disk image can be obtained from Cisco Modeling Labs (CML).
More information about Cisco vIOS:
<https://developer.cisco.com/docs/modeling-labs/iosvl2/>

Once you extract disk image, rename the image file to the following format:
`cisco_viosl2-[VERSION].qcow2`
Where `[VERSION]` is the desired version of the image, for example `15.2` or `15.2.2020`.

Finally, you can build the docker image with the `make docker-image` command.

Tested with versions:

- 15.2 (image: vios_l2-adventerprisek9-m.ssa.high_iron_20200929.qcow2)

## System requirements

- CPU: 1 core
- RAM: 768MB
- Disk: <1GB

## Network interfaces

The router supports up to 16 GigabitEthernet interfaces.

- The first interface `GigaEthernet0/0` is used as the management interface (it is placed in separated VRF) and is 
  mapped to the docker container interface `eth0`.
- The rest of the interfaces are numbered from `GigaEthernet0/1` and are used as data interfaces.
  They are mapped to the docker container interfaces `eth1`, `eth2`, etc.
- The interfaces are used in groups of four, e.g. `GigaEthernet0/0` to `GigaEthernet0/3`, `GigaEthernet1/0-3` to
  `GigaEthernet1/3`, etc.

## Management plane

The following protocols are enabled on the management interface:

- CLI SSH on port 22
- NETCONF via SSH on port 22 (the same credentials are used as for CLI SSH)
- SNMPv2c on port 161 (`public` used as community string)

## Environment variables

| ID              | Description               | Default |
|-----------------|---------------------------|---------|
| USERNAME        | SSH username              | admin   |
| PASSWORD        | SSH password              | admin   |
| HOSTNAME        | device hostname           | viosl2  |
| TRACE           | enable trace logging      | false   |
| CONNECTION_MODE | interface connection mode | tc      |

## Configuration persistence

The startup configuration can be provided by mounting a file to `/config/startup-config.cfg`.
The changes done in the switch configuration during runtime are not automatically persisted outside
the container - after stopping the container, the content of the flash/NVRAM is lost.
User is responsible for persistence of the changes, for example, by copying the configuration
to mounted startup-configuration file.

## Sample containerlab topology

```yaml
name: viosl2-lab

topology:
  kinds:
    linux:
      image: vrnetlab/cisco_viosl2:15.2
  nodes:
    viosl2-1:
      kind: linux
      binds:
        - viosl2-1.cfg:/config/startup-config.cfg
      env:
        HOSTNAME: viosl2-1
    viosl2-2:
      kind: linux
      binds:
        - viosl2-2.cfg:/config/startup-config.cfg
      env:
        HOSTNAME: viosl2-2
  links:
    - endpoints: ["viosl2-1:eth1","viosl2-2:eth1"]
```
