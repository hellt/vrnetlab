#!/usr/bin/env python3

import datetime
import logging
import os
import re
import signal
import sys
import time


import vrnetlab
from scrapli.driver.core import IOSXRDriver

STARTUP_CONFIG_FILE = "/config/startup-config.cfg"

DEFAULT_SCRAPLI_TIMEOUT = 2700
DEFAULT_SMP = 4
DEFAULT_RAM = 16384 # in MB

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


class XRv9k_vm(vrnetlab.VM):
    def __init__(self, hostname, username, password, nics, conn_mode, install=False):
        disk_image = None
        for e in sorted(os.listdir("/")):
            if not disk_image and re.search(".qcow2", e):
                disk_image = "/" + e
        super(XRv9k_vm, self).__init__(username, password, disk_image=disk_image, ram=DEFAULT_RAM, smp=f"cores={DEFAULT_SMP},threads=1,sockets=1")
        
        self.hostname = hostname
        self.conn_mode = conn_mode
        self.num_nics = nics
        self.install_mode = install
        
        self.qemu_args.extend(
            [
                "-machine",
                "smm=off",
                "-boot",
                "order=c",
                "-cpu",
                "qemu64,+ssse3,+sse4.1,+sse4.2",
                "-serial",
                "telnet:0.0.0.0:50%02d,server,nowait" % (self.num + 1),
                "-serial",
                "telnet:0.0.0.0:50%02d,server,nowait" % (self.num + 2),
                "-serial",
                "telnet:0.0.0.0:50%02d,server,nowait" % (self.num + 3),
            ]
        )
        self.credentials = []

    def gen_mgmt(self):
        """Generate qemu args for the mgmt interface(s)"""
        res = []
        # mgmt interface
        res.extend(
            ["-device", "e1000,netdev=mgmt,mac=%s" % vrnetlab.gen_mac(0)]
        )
        res.extend(
            [
                "-netdev",
                "user,id=mgmt,net=10.0.0.0/24,"
                "tftp=/tftpboot,"
                "hostfwd=tcp:0.0.0.0:22-10.0.0.15:22,"
                "hostfwd=udp:0.0.0.0:161-10.0.0.15:161,"
                "hostfwd=tcp:0.0.0.0:830-10.0.0.15:830,"
                "hostfwd=tcp:0.0.0.0:57400-10.0.0.15:57400"
            ]
        )
        # dummy interface for xrv9k ctrl interface
        res.extend(
            [
                "-device",
                "e1000,netdev=ctrl-dummy,id=ctrl-dummy,mac=%s"
                % vrnetlab.gen_mac(0),
                "-netdev",
                "tap,ifname=ctrl-dummy,id=ctrl-dummy,script=no,downscript=no",
            ]
        )
        # dummy interface for xrv9k dev interface
        res.extend(
            [
                "-device",
                "e1000,netdev=dev-dummy,id=dev-dummy,mac=%s"
                % vrnetlab.gen_mac(0),
                "-netdev",
                "tap,ifname=dev-dummy,id=dev-dummy,script=no,downscript=no",
            ]
        )

        return res

    def bootstrap_spin(self):

        if self.spins > 600:
            # too many spins with no result ->  give up
            self.logger.error(
                "node is failing to boot or we can't catch the right prompt. Restarting..."
            )
            self.stop()
            self.start()
            return

        (ridx, match, res) = self.expect(
            [
                b"Press RETURN to get started",
                b"Enter root-system [U|u]sername",
                b"SDR\/XR partition preparation completed successfully",
            ],
            1,
        )

        if match:  # got a match!
            if ridx == 0:  # press return to get started, so we press return!
                self.logger.info("got 'press return to get started...'")
                self.wait_write("", wait=None)
            if ridx == 1:  # system configuration complete
                if self.install_mode:
                    return
                self.logger.info("Creating initial user")
                self.wait_write(self.username, wait=None)
                self.wait_write(self.password, wait="Enter secret:")
                self.wait_write(self.password, wait="Enter secret again:")
                self.credentials.insert(0, [self.username, self.password])
                
                self.logger.info("Applying configuration")
                
                # apply bootstrap and startup configuration
                self.apply_config()
                
                # startup time?
                startup_time = datetime.datetime.now() - self.start_time
                self.logger.info("Startup complete in: %s" % startup_time)
                # mark as running
                self.running = True
                return
            if ridx == 2 and self.install_mode:
                self.logger.info(f"Installation completed, took {datetime.datetime.now() - self.start_time}")
                self.running = True
                return

        # no match, if we saw some output from the router it's probably
        # booting, so let's give it some more time
        if res != b"":
            self.print(res)
            # reset spins if we saw some output
            self.spins = 0

        self.spins += 1

        return
    
    def apply_config(self):
        
        self.tn.close()
        
        scrapli_timeout = os.getenv('SCRAPLI_TIMEOUT', DEFAULT_SCRAPLI_TIMEOUT)
        self.logger.info(f"Scrapli timeout is {scrapli_timeout} seconds. (Default: {DEFAULT_SCRAPLI_TIMEOUT})")
        
        # init scrapli
        xrv9k_scrapli_dev = {
            "host": "127.0.0.1",
            "port": 5000 + self.num,
            "auth_username": self.username,
            "auth_password": self.password,
            "auth_strict_key": False,
            "transport": "telnet",
            "timeout_socket": scrapli_timeout,
            "timeout_transport": scrapli_timeout,
            "timeout_ops": scrapli_timeout,
        }
        
        xrv9k_config = f"""hostname {self.hostname}
vrf clab-mgmt
description Containerlab management VRF. DO NOT DELETE.
address-family ipv4 unicast
!
router static
vrf clab-mgmt
address-family ipv4 unicast
0.0.0.0/0 10.0.0.2
!
ssh server v2
ssh server vrf clab-mgmt
ssh server netconf port 830
ssh server netconf vrf clab-mgmt
netconf-yang agent ssh
!
grpc port 57400
grpc no-tls
!
xml agent tty
!
interface MgmtEth0/RP0/CPU0/0
vrf clab-mgmt
no shutdown
ipv4 address 10.0.0.15/24
!
commit
"""

        with IOSXRDriver(**xrv9k_scrapli_dev) as con:
            con.send_config(xrv9k_config)

            if not os.path.exists(STARTUP_CONFIG_FILE):
                self.logger.warning(f"User provided startup configuration is not found.")
                return

            self.logger.info("Startup configuration file found")
            
            # need to append 'commit' to end of startup config file
            startup_cfg = []
            
            with open(STARTUP_CONFIG_FILE, 'r') as cfg:
                for line in cfg:
                    # remove trailing \n from each line
                    startup_cfg.append(line.strip())
                startup_cfg.append("commit")
            
            # send startup config
            res = con.send_configs(startup_cfg)
            # print startup config and result
            for response in res:
                self.logger.info(f"CONFIG: {response.channel_input}")
                self.logger.info(f"CONFIG RESULT: {response.result}")

            if res.failed:
                self.logger.error(f"Failed to load startup configuration.")
                return

    @property
    def smp(self):
        """
        Read SMP parameter (e.g. number of CPU cores) from the QEMU_SMP environment variable.
        If the QEMU_SMP parameter is not set, the default value is used.
        Should be provided as a number, e.g. 2
        """

        if "QEMU_SMP" in os.environ:
            qemu_smp = os.getenv("QEMU_SMP")
            # if the user has supplied only a core count set the correct smp
            if re.match('^[0-9]+$', str(qemu_smp)):
                return str(f'cores={qemu_smp},threads=1,sockets=1')
            else:
                return str(qemu_smp)

        return str(self._smp)

class XRv9k(vrnetlab.VR):
    def __init__(self, hostname, username, password, nics, conn_mode):
        super(XRv9k, self).__init__(username, password)
        self.vms = [XRv9k_vm(hostname, username, password, nics, conn_mode)]


class XRv9k_Installer(XRv9k):
    """ XRV installer
        Will start the XRV and then shut it down. Booting the XRV for the
        first time requires the XRV itself to install internal packages
        then it will restart. Subsequent boots will not require this restart.
        By running this "install" when building the docker image we can
        decrease the normal startup time of the XRV.
    """
    def __init__(self, hostname, username, password, nics, conn_mode):
        super(XRv9k, self).__init__(username, password)
        self.vms = [XRv9k_vm(hostname, username, password, nics, conn_mode, install=True)]
    
    def install(self):
        self.logger.info("Installing XRv9k")
        xrv = self.vms[0]
        while not xrv.running:
            xrv.work()
        time.sleep(2)
        xrv.stop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--trace", action="store_true", help="enable trace level logging"
    )
    parser.add_argument("--hostname", default="vr-xrv9k", help="Router hostname")
    parser.add_argument("--username", default="vrnetlab", help="Username")
    parser.add_argument("--password", default="VR-netlab9", help="Password")
    parser.add_argument("--nics", type=int, default=128, help="Number of NICS")
    parser.add_argument('--install', action="store_true", help="Pre-install image")
    parser.add_argument(
        "--vcpu", type=int, default=4, help="Number of cpu cores to use"
    )
    parser.add_argument(
        "--ram", type=int, default=16384, help="Number RAM to use in MB"
    )
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

    vrnetlab.boot_delay()

    if args.install:
        vr = XRv9k_Installer(
            args.hostname,
            args.username,
            args.password,
            args.nics,
            args.connection_mode,
        )
        vr.install()
    else:
        vr = XRv9k(
            args.hostname,
            args.username,
            args.password,
            args.nics,
            args.connection_mode,
        )
        vr.start()
