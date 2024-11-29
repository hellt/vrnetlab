#!/usr/bin/env python3

import datetime
import logging
import os
import re
import signal
import sys
import time

import vrnetlab

STARTUP_CONFIG_FILE = "/config/startup-config.cfg"


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


class VRP_vm(vrnetlab.VM):
    def __init__(self, username, password, hostname, conn_mode):
        disk_image = None
        self.vm_type = "UNKNOWN"
        for e in sorted(os.listdir("/")):
            if not disk_image and re.search(".qcow2$", e):
                disk_image = "/" + e
                if "huawei_ne40e" in e:
                    self.vm_type = "NE40E"
                if "huawei_ce12800" in e:
                    self.vm_type = "CE12800"

        super(VRP_vm, self).__init__(
            username,
            password,
            disk_image=disk_image,
            ram=2048,
            smp="2",
            driveif="virtio",
        )

        self.hostname = hostname
        self.conn_mode = conn_mode
        self.num_nics = 14
        self.nic_type = "virtio-net-pci"

    def bootstrap_spin(self):
        """This function should be called periodically to do work."""

        if self.spins > 300:
            # too many spins with no result ->  give up
            self.stop()
            self.start()
            return

        (ridx, match, res) = self.expect([b"<HUAWEI>"], 1)

        if match and ridx == 0:  # got a match!
            # run main config!
            self.logger.info("Running bootstrap_config()")
            self.startup_config()
            self.bootstrap_config()
            time.sleep(1)
            # close telnet connection
            self.tn.close()
            # startup time?
            startup_time = datetime.datetime.now() - self.start_time
            self.logger.info("Startup complete in: %s" % startup_time)
            # mark as running
            self.running = True
            return

        time.sleep(5)

        # no match, if we saw some output from the router it's probably
        # booting, so let's give it some more time
        if res != "":
            self.print(res)
            # reset spins if we saw some output
            self.spins = 0

        self.spins += 1

        return

    def bootstrap_mgmt_interface(self):
        self.wait_write(cmd="mmi-mode enable", wait=None)
        self.wait_write(cmd="system-view", wait=">")
        self.wait_write(cmd="ip vpn-instance __MGMT_VPN__", wait="]")
        self.wait_write(cmd="ipv4-family", wait="]")
        self.wait_write(cmd="quit", wait="]")
        self.wait_write(cmd="quit", wait="]")
        if self.vm_type == "CE12800":
            mgmt_interface = "MEth"
        if self.vm_type == "NE40E":
            mgmt_interface = "GigabitEthernet"
        self.wait_write(cmd=f"interface {mgmt_interface} 0/0/0", wait="]")
        # Error: The system is busy in building configuration. Please wait for a moment...
        while True:
            self.wait_write(cmd="clear configuration this", wait=None)
            (idx, match, res) = self.expect([rb"Error"], 1)
            if match and idx == 0:
                time.sleep(5)
            else:
                break
        self.wait_write(cmd="undo shutdown", wait=None)
        self.wait_write(cmd="ip binding vpn-instance __MGMT_VPN__", wait="]")
        self.wait_write(cmd="ip address 10.0.0.15 24", wait="]")
        self.wait_write(cmd="quit", wait="]")
        self.wait_write(
            cmd="ip route-static vpn-instance __MGMT_VPN__ 0.0.0.0 0 10.0.0.2", wait="]"
        )

    def bootstrap_config(self):
        """Do the actual bootstrap config"""
        self.bootstrap_mgmt_interface()
        self.wait_write(cmd=f"sysname {self.hostname}", wait="]")

        if self.vm_type == "CE12800":
            self.wait_write(cmd="aaa", wait="]")
            self.wait_write(cmd="undo local-user policy security-enhance", wait="]")
            self.wait_write(cmd="quit", wait="]")
        if self.vm_type == "NE40E":
            self.wait_write(cmd="undo user-security-policy enable", wait="]")

        self.wait_write(cmd="aaa", wait="]")
        self.wait_write(cmd=f"undo local-user {self.username}", wait="]")
        self.wait_write(
            cmd=f"local-user {self.username} password irreversible-cipher {self.password}",
            wait="]",
        )
        self.wait_write(cmd=f"local-user {self.username} service-type ssh", wait="]")
        self.wait_write(
            cmd=f"local-user {self.username} user-group manage-ug", wait="]"
        )
        self.wait_write(cmd="quit", wait="]")

        # SSH
        self.wait_write(cmd="user-interface vty 0 4", wait="]")
        self.wait_write(cmd="authentication-mode aaa", wait="]")
        self.wait_write(cmd="protocol inbound ssh", wait="]")
        self.wait_write(cmd="quit", wait="]")
        self.wait_write(cmd=f"undo ssh user {self.username}", wait="]")
        self.wait_write(
            cmd=f"ssh user {self.username} authentication-type password ", wait="]"
        )
        self.wait_write(cmd=f"ssh user {self.username} service-type all ", wait="]")
        self.wait_write(cmd="stelnet server enable", wait="]")

        # NETCONF
        self.wait_write(cmd="snetconf server enable", wait="]")
        self.wait_write(cmd="netconf", wait="]")
        self.wait_write(cmd="protocol inbound ssh port 830", wait="]")
        self.wait_write(cmd="quit", wait="]")

        self.wait_write(cmd="commit", wait="]")
        self.wait_write(cmd="return", wait="]")
        self.wait_write(cmd="save", wait=">")
        self.wait_write(cmd="undo mmi-mode enable", wait=">")

    def startup_config(self):
        if not os.path.exists(STARTUP_CONFIG_FILE):
            self.logger.trace(f"Startup config file {STARTUP_CONFIG_FILE} not found")
            return
        

        vrnetlab.run_command(["cp", STARTUP_CONFIG_FILE, "/tftpboot/containerlab.cfg"])


        if self.vm_type == "CE12800":
            with open(STARTUP_CONFIG_FILE, "r+") as file:
                cfg = file.read()
                modified = False

                if "device board 1 " not in cfg:
                    cfg = "device board 1 board-type CE-LPUE\n" + cfg
                    modified = True

                if "interface NULL0" not in cfg:
                    cfg = cfg + "\ninterface NULL0"
                    modified = True

                if modified:
                    file.seek(0)
                    file.write(cfg)
                    file.truncate()


        self.bootstrap_mgmt_interface()
        self.wait_write(cmd="commit", wait="]")


        self.wait_write(cmd=f"return", wait="]")
        time.sleep(1)
        self.wait_write(cmd=f"tftp 10.0.0.2 vpn-instance __MGMT_VPN__ get containerlab.cfg", wait=">")
        self.wait_write(cmd="startup saved-configuration containerlab.cfg", wait=">")
        self.wait_write(cmd="reboot fast", wait=">")
        self.wait_write(cmd="reboot", wait="#")
        self.wait_write(cmd="", wait="The current login time is")
        print(f"File '{STARTUP_CONFIG_FILE}' successfully loaded")

    def gen_mgmt(self):
        """Generate qemu args for the mgmt interface(s)"""
        # call parent function to generate the mgmt interface
        res = super().gen_mgmt()

        # Creates required dummy interface
        res.append(f"-device virtio-net-pci,netdev=dummy,mac={vrnetlab.gen_mac(0)}")
        res.append("-netdev tap,ifname=vrp-dummy,id=dummy,script=no,downscript=no")

        return res


class VRP(vrnetlab.VR):
    def __init__(self, hostname, username, password, conn_mode):
        super(VRP, self).__init__(username, password)
        self.vms = [VRP_vm(username, password, hostname, conn_mode)]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--trace", action="store_true", help="enable trace level logging"
    )
    parser.add_argument("--hostname", default="vr-VRP", help="Router hostname")
    parser.add_argument("--username", default="vrnetlab", help="Username")
    parser.add_argument("--password", default="VR-netlab9", help="Password")
    parser.add_argument(
        "--connection-mode",
        default="tc",
        help="Connection mode to use in the datapath",
    )

    args = parser.parse_args()

    LOG_FORMAT = "%(asctime)s: %(module)-10s %(levelname)-8s %(message)s"
    logging.basicConfig(format=LOG_FORMAT)
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)

    if args.trace:
        logger.setLevel(1)

    vr = VRP(
        args.hostname, args.username, args.password, conn_mode=args.connection_mode
    )
    vr.start()
