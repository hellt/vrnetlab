# Spirent vSTC

This is the vrnetlab image for the Spirent vSTC (Virtual Spirent Test Center).

Default credentials are: `admin`:`spt_admin`

On bootup the node will be boostrapped with IP addressing config, and then rebooted to fully apply the configuration.

Please wait for the 'Startup Completed' message in the `docker logs` output before attempting to connect to the node via the STC Client or SSH.

## Example

You should use the Spirent vSTC with the `generic_vm` kind in your topology definition.

Interface naming follows `ethX` naming convention, with `eth0` reserved for the clab management network.

```yaml
name: vstc_lab
topology:
  nodes:
    # example DUT
    r1:
      kind: nokia_sros
      image: vrnetlab/nokia_sros:24.10.R1
    # STC traffic generator
    vstc:
      kind: generic_vm
      image: vrnetlab/spirent_vstc:5.55.3216

  links:
    - endpoints: ["vstc:eth1","r1:1/1/1"]
    - endpoints: ["vstc:eth2","r1:1/1/2"]
```
