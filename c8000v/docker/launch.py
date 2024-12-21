#!/usr/bin/env python3

import datetime
import logging
import os
import re
import signal
import subprocess
import sys

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


class C8000v_vm(vrnetlab.VM):
    def __init__(self, hostname, username, password, conn_mode, install_mode=False):
        disk_image = None
        for e in sorted(os.listdir("/")):
            if not disk_image and re.search(".qcow2$", e):
                disk_image = "/" + e
            if re.search(r"\.license$", e):
                os.rename("/" + e, "/tftpboot/license.lic")

        self.license = False
        if os.path.isfile("/tftpboot/license.lic"):
            logger.info("License found")
            self.license = True

        super().__init__(username, password, disk_image=disk_image, ram=4096, use_scrapli=True)
        self.install_mode = install_mode
        self.hostname = hostname
        self.conn_mode = conn_mode
        self.num_nics = 9
        self.nic_type = "virtio-net-pci"

        if self.install_mode:
            self.logger.debug("Install mode")
            self.image_name = "config.iso"
            self.create_boot_image()

            self.qemu_args.extend(["-cdrom", "/" + self.image_name])

    def create_boot_image(self):
        """Creates a iso image with a bootstrap configuration"""

        with open("/iosxe_config.txt", "w") as cfg_file:
            if self.license:
                cfg_file.write("do clock set 13:33:37 1 Jan 2010\r\n")
                cfg_file.write("interface GigabitEthernet1\r\n")
                cfg_file.write("ip address 10.0.0.15 255.255.255.0\r\n")
                cfg_file.write("no shut\r\n")
                cfg_file.write("exit\r\n")
                cfg_file.write("license accept end user agreement\r\n")
                cfg_file.write("yes\r\n")
                cfg_file.write("do license install tftp://10.0.0.2/license.lic\r\n\r\n")
            cfg_file.write("license boot level network-premier addon dna-premier\r\n")
            cfg_file.write("platform console serial\r\n\r\n")
            cfg_file.write("do clear platform software vnic-if nvtable\r\n")
            cfg_file.write("do wr\r\n")
            cfg_file.write("do reload\r\n")

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

        if self.spins > 300:
            # too many spins with no result ->  give up
            self.stop()
            self.start()
            return

        (ridx, match, res) = self.con_expect(
            [b"Press RETURN to get started!", b"IOSXEBOOT-4-FACTORY_RESET"]
        )
        if match:  # got a match!
            if ridx == 0:  # login
                self.logger.info("matched, Press RETURN to get started.")
                if self.install_mode:
                    self.logger.info("Now we wait for the device to reload")
                else:
                    self.wait_write("", wait=None)
                    
                    self.apply_config()
                    
                    # close telnet connection
                    self.scrapli_tn.close()
                    
                    # startup time?
                    startup_time = datetime.datetime.now() - self.start_time
                    self.logger.info("Startup complete in: %s", startup_time)
                    self.running = True
                    
                    return
            elif ridx == 1:  # IOSXEBOOT-4-FACTORY_RESET
                if self.install_mode:
                    install_time = datetime.datetime.now() - self.start_time
                    self.logger.info("Install complete in: %s", install_time)
                    self.running = True
                    return
                else:
                    self.logger.warning("Unexpected reload while running")

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
        cat8kv_scrapli_dev = {
            "host": "127.0.0.1",
            "auth_bypass": True,
            "auth_strict_key": False,
            "timeout_socket": scrapli_timeout,
            "timeout_transport": scrapli_timeout,
            "timeout_ops": scrapli_timeout,
        }
        
        v4_mgmt_address = vrnetlab.cidr_to_ddn(self.mgmt_address_ipv4)
                
        cat8kv_config = f"""hostname {self.hostname}
username {self.username} privilege 15 password {self.password}
ip domain name example.com
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
netconf max-sessions 16
netconf detailed-error
!
ip ssh server algorithm mac hmac-sha2-512
ip ssh maxstartups 128
!
"""

        con = IOSXEDriver(**cat8kv_scrapli_dev)
        con.commandeer(conn=self.scrapli_tn)
        
        if os.path.exists(STARTUP_CONFIG_FILE):
            self.logger.info("Startup configuration file found")
            with open(STARTUP_CONFIG_FILE, "r") as config:
                cat8kv_config += config.read()
        else:
            self.logger.warning(f"User provided startup configuration is not found.")

        res = con.send_configs(cat8kv_config.splitlines())
        res += con.send_commands(["write memory"])

        for response in res:
            self.logger.info(f"CONFIG:{response.channel_input}")
            self.logger.info(f"RESULT:{response.result}")


class C8000v(vrnetlab.VR):
    def __init__(self, hostname, username, password, conn_mode):
        super(C8000v, self).__init__(username, password)
        self.vms = [C8000v_vm(hostname, username, password, conn_mode)]


class C8000v_installer(C8000v):
    """C8000v installer

    Will start the C8000v with a mounted iso to make sure that we get
    console output on serial, not vga.
    """

    def __init__(self, hostname, username, password, conn_mode):
        super(C8000v, self).__init__(username, password)
        self.vms = [
            C8000v_vm(hostname, username, password, conn_mode, install_mode=True)
        ]

    def install(self):
        self.logger.info("Installing C8000v")
        cat8kv = self.vms[0]
        while not cat8kv.running:
            cat8kv.work()
        cat8kv.stop()
        self.logger.info("Installation complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--trace", action="store_true", help="enable trace level logging"
    )
    parser.add_argument("--username", default="vrnetlab", help="Username")
    parser.add_argument("--password", default="VR-netlab9", help="Password")
    parser.add_argument("--install", action="store_true", help="Install C8000v")
    parser.add_argument("--hostname", default="c8000v", help="Router hostname")
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
        vr = C8000v_installer(
            args.hostname, args.username, args.password, args.connection_mode
        )
        vr.install()
    else:
        vr = C8000v(args.hostname, args.username, args.password, args.connection_mode)
        vr.start()
