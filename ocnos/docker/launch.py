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


class OCNOS_vm(vrnetlab.VM):
    def __init__(self, hostname, username, password, conn_mode):
        disk_image = None
        for e in os.listdir("/"):
            if re.search(".qcow2$", e):
                disk_image = "/" + e
        if disk_image == None:
            logging.getLogger().info("Disk image was not found")
            exit(1)
        super(OCNOS_vm, self).__init__(
            username,
            password,
            disk_image=disk_image,
            ram=4096,
            smp="2",
            driveif="virtio",
        )
        self.hostname = hostname
        self.conn_mode = conn_mode
        self.num_nics = 8
        self.nic_type = "virtio-net-pci"

    def bootstrap_spin(self):
        """This function should be called periodically to do work."""

        if self.spins > 300:
            # too many spins with no result ->  give up
            self.logger.info("To many spins with no result, restarting")
            self.stop()
            self.start()
            return

        (ridx, match, res) = self.tn.expect([b"OcNOS login:"], 1)

        if match and ridx == 0:  # got a match!
            self.logger.debug("matched login prompt")
            self.logger.debug("trying to log in with 'ocnos'")
            self.wait_write("ocnos", wait=None)
            self.wait_write("ocnos", wait="Password:")
            # run bootstrap config!
            self.logger.info("Running bootstrap_config()")
            self.bootstrap_config()
            self.startup_config()
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
        if res != b"":
            self.logger.trace("OUTPUT: %s" % res.decode())
            # reset spins if we saw some output
            self.spins = 0

        self.spins += 1

        return

    def bootstrap_mgmt_interface(self):
        self.wait_write(cmd="", wait=None)
        self.wait_write(cmd="enable", wait=">")
        self.wait_write(cmd="configure terminal", wait="#")
        self.wait_write(cmd="interface eth0", wait="(config)#")
        self.wait_write(cmd="ip vrf forwarding management", wait="(config-if)#")
        self.wait_write(cmd="commit", wait="(config-if)#")
        self.wait_write(cmd="ip address dhcp", wait="(config-if)#")
        self.wait_write(cmd="commit", wait="(config-if)#")
        self.wait_write(cmd="exit", wait="(config-if)#")
        self.wait_write(
            cmd="ip route vrf management 0.0.0.0/0 10.0.0.2 eth0", wait="(config)#"
        )
        self.wait_write(cmd="commit", wait="(config)#")

    def bootstrap_config(self):
        """Do the actual bootstrap config"""
        self.logger.info("applying bootstrap configuration")
        self.bootstrap_mgmt_interface()

        self.wait_write(f"hostname {self.hostname}", wait="(config)#")
        self.wait_write(
            "username %s role network-admin password %s"
            % (self.username, self.password),
            wait="(config)#",
        )
        self.wait_write(cmd="no ip domain-lookup vrf management", wait="(config)#")
        self.wait_write(cmd="feature netconf-ssh vrf management", wait="(config)#")
        self.wait_write(cmd="feature netconf-tls vrf management", wait="(config)#")
        self.wait_write("commit", wait="(config)#")
        self.wait_write("exit", wait="(config)#")
        self.wait_write("write memory", wait="#")

    def startup_config(self):
        """Load additional config provided by user."""

        if not os.path.exists(STARTUP_CONFIG_FILE):
            self.logger.trace(f"Startup config file {STARTUP_CONFIG_FILE} is not found")
            return

        self.logger.trace(f"Startup config file {STARTUP_CONFIG_FILE} exists")
        with open(STARTUP_CONFIG_FILE) as file:
            config_lines = file.readlines()
            config_lines = [line.rstrip() for line in config_lines]
            self.logger.trace(f"Parsed startup config file {STARTUP_CONFIG_FILE}")

        self.logger.info(f"Writing lines from {STARTUP_CONFIG_FILE}")

        self.wait_write("configure terminal")
        # Apply lines from file
        for line in config_lines:
            self.wait_write(line)
        # End and Save
        self.wait_write("commit")
        self.wait_write("end")
        self.wait_write("write memory")


class OCNOS(vrnetlab.VR):
    def __init__(self, hostname, username, password, conn_mode):
        super(OCNOS, self).__init__(username, password)
        self.vms = [OCNOS_vm(hostname, username, password, conn_mode)]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--trace", action="store_true", help="enable trace level logging"
    )
    parser.add_argument("--hostname", default="vr-xrv9k", help="Router hostname")
    parser.add_argument("--username", default="vrnetlab", help="Username")
    parser.add_argument("--password", default="VR-netlab9", help="Password")
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

    logger.debug(f"Environment variables: {os.environ}")
    vrnetlab.boot_delay()

    vr = OCNOS(args.hostname, args.username, args.password, args.connection_mode)
    vr.start()
