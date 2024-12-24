#!/usr/bin/env python3

import datetime
import logging
import os
import re
import signal
import subprocess
import sys
import time

import vrnetlab
from scrapli.driver.core import IOSXEDriver

STARTUP_CONFIG_FILE = "/config/startup-config.cfg"
DEFAULT_SCRAPLI_TIMEOUT = 900

def handle_SIGCHLD(signal, frame):
    os.waitpid(-1, os.WNOHANG)


def handle_SIGTERM(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, handle_SIGTERM)
signal.signal(signal.SIGTERM, handle_SIGTERM)
signal.signal(signal.SIGCHLD, handle_SIGCHLD)

TRACE_LEVEL_NUM = 9
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")


def trace(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)


logging.Logger.trace = trace


class CSR_vm(vrnetlab.VM):
    def __init__(
        self, hostname, username, password, nics, conn_mode, install_mode=False
    ):
        for e in os.listdir("/"):
            if re.search(".qcow2$", e):
                disk_image = "/" + e
            if re.search("\.license$", e):
                os.rename("/" + e, "/tftpboot/license.lic")

        self.license = False
        self._static_mgmt_mac = True
        if os.path.isfile("/tftpboot/license.lic"):
            logger.info("License found")
            self.license = True

        super(CSR_vm, self).__init__(username, password, disk_image=disk_image, use_scrapli=True)

        self.install_mode = install_mode
        self.num_nics = nics
        self.hostname = hostname
        self.conn_mode = conn_mode
        self.nic_type = "virtio-net-pci"

        if self.install_mode:
            self.logger.debug("install mode")
            self.image_name = "config.iso"
            self.create_boot_image()

            self.qemu_args.extend(["-cdrom", "/" + self.image_name])

    def create_boot_image(self):
        """Creates a iso image with a bootstrap configuration"""

        cfg_file = open("/iosxe_config.txt", "w")
        if self.license:
            cfg_file.write("do clock set 13:33:37 1 Jan 2010\r\n")
            cfg_file.write("interface GigabitEthernet1\r\n")
            cfg_file.write("ip address 10.0.0.15 255.255.255.0\r\n")
            cfg_file.write("no shut\r\n")
            cfg_file.write("exit\r\n")
            cfg_file.write("license accept end user agreement\r\n")
            cfg_file.write("yes\r\n")
            cfg_file.write("do license install tftp://10.0.0.2/license.lic\r\n\r\n")

        cfg_file.write("platform console serial\r\n\r\n")
        cfg_file.write("do clear platform software vnic-if nvtable\r\n\r\n")
        cfg_file.write("do wr\r\n")
        cfg_file.write("do reload\r\n")
        cfg_file.close()

        genisoimage_args = [
            "genisoimage",
            "-l",
            "-o",
            "/" + self.image_name,
            "/iosxe_config.txt",
        ]

        subprocess.Popen(genisoimage_args)

    def bootstrap_spin(self):
        """This function should be called periodically to do work."""

        if self.spins > 600:
            # too many spins with no result ->  give up
            self.stop()
            self.start()
            return

        (ridx, match, res) = self.con_expect([b"Press RETURN to get started!"], 1)
        if match:  # got a match!
            if ridx == 0:  # login
                if self.install_mode:
                    self.running = True
                    return

                self.logger.debug("matched, Press RETURN to get started.")
                
                self.wait_write("", wait=None)

                self.apply_config()
                
                # close the telnet connection
                self.scrapli_tn.close()
                                
                # startup time?
                startup_time = datetime.datetime.now() - self.start_time
                self.logger.info("Startup complete in: %s" % startup_time)
                self.running = True
                
                return

        # no match, if we saw some output from the router it's probably
        # booting, so let's give it some more time
        if res != b"":
            self.write_to_stdout(res)
            # reset spins if we saw some output
            self.spins = 0

        self.spins += 1

        return


    def apply_config(self):  
        
        scrapli_timeout = os.getenv("SCRAPLI_TIMEOUT", DEFAULT_SCRAPLI_TIMEOUT)
        self.logger.info(f"Scrapli timeout is {scrapli_timeout}s (default {DEFAULT_SCRAPLI_TIMEOUT}s)")
        
        # init scrapli
        csr_scrapli_dev = {
            "host": "127.0.0.1",
            "auth_bypass": True,
            "auth_strict_key": False,
            "timeout_socket": scrapli_timeout,
            "timeout_transport": scrapli_timeout,
            "timeout_ops": scrapli_timeout,
        }
        
        v4_mgmt_address = vrnetlab.cidr_to_ddn(self.mgmt_address_ipv4)
        
        ip_domain_name = "ip domain name example.com" if int(self.version.split('.')[0]) >= 16 else "ip domain-name example.com"
                
        csr_config = f"""hostname {self.hostname}
username {self.username} privilege 15 password {self.password}
{ip_domain_name}
!
crypto key generate rsa modulus 2048
!
line con 0
logging synchronous
!
line vty 0 4
logging synchronous
login local
transport input all
!
ipv6 unicast-routing
!
vrf definition clab-mgmt
description Containerlab management VRF (DO NOT DELETE)
address-family ipv4
exit
address-family ipv6
exit
exit
!
ip route vrf clab-mgmt 0.0.0.0 0.0.0.0 {self.mgmt_gw_ipv4}
ipv6 route vrf clab-mgmt ::/0 {self.mgmt_gw_ipv6}
!
interface GigabitEthernet 1
description Containerlab management interface
vrf forwarding clab-mgmt
ip address {v4_mgmt_address[0]} {v4_mgmt_address[1]}
ipv6 address {self.mgmt_address_ipv6}
no shut
exit
!
restconf
netconf-yang
!
"""

        con = IOSXEDriver(**csr_scrapli_dev)
        con.commandeer(conn=self.scrapli_tn)
        
        if os.path.exists(STARTUP_CONFIG_FILE):
            self.logger.info("Startup configuration file found")
            with open(STARTUP_CONFIG_FILE, "r") as config:
                csr_config += config.read()
        else:
            self.logger.warning(f"User provided startup configuration is not found.")

        res = con.send_configs(csr_config.splitlines())
        res += con.send_commands(["write memory"])
    
        for response in res:
            self.logger.info(f"CONFIG:{response.channel_input}")
            self.logger.info(f"RESULT:{response.result}")


class CSR(vrnetlab.VR):
    def __init__(self, hostname, username, password, nics, conn_mode):
        super(CSR, self).__init__(username, password)
        self.vms = [CSR_vm(hostname, username, password, nics, conn_mode)]


class CSR_installer(CSR):
    """CSR installer

    Will start the CSR with a mounted iso to make sure that we get
    console output on serial, not vga.
    """

    def __init__(self, hostname, username, password, nics, conn_mode):
        super(CSR, self).__init__(username, password)
        self.vms = [
            CSR_vm(
                hostname,
                username,
                password,
                nics,
                conn_mode,
                install_mode=True,
            )
        ]

    def install(self):
        self.logger.info("Installing CSR")
        csr = self.vms[0]
        while not csr.running:
            csr.work()
        time.sleep(30)
        csr.stop()
        self.logger.info("Installation complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--trace", action="store_true", help="enable trace level logging"
    )
    parser.add_argument("--username", default="vrnetlab", help="Username")
    parser.add_argument("--password", default="VR-netlab9", help="Password")
    parser.add_argument("--install", action="store_true", help="Install CSR")
    parser.add_argument("--hostname", default="csr1000v", help="Router Hostname")
    parser.add_argument("--nics", type=int, default=31, help="Number of NICS")
    parser.add_argument(
        "--connection-mode",
        default="vrxcon",
        help="Connection mode to use in the datapath",
    )
    args = parser.parse_args()

    LOG_FORMAT = "%(asctime)s: %(module)-10s %(levelname)-8s %(message)s"
    logging.basicConfig(format=LOG_FORMAT)
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    if args.trace:
        logger.setLevel(1)

    if args.install:
        vr = CSR_installer(
            args.hostname,
            args.username,
            args.password,
            args.nics,
            args.connection_mode,
        )
        vr.install()
    else:
        vr = CSR(
            args.hostname,
            args.username,
            args.password,
            args.nics,
            args.connection_mode,
        )
        vr.start()
