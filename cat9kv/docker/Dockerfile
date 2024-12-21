FROM ghcr.io/srl-labs/vrnetlab-base:0.0.1

ARG VERSION
ENV VERSION=${VERSION}
ARG IMAGE
COPY $IMAGE* /
COPY *.py /
# for vSwitch.xml file (specifies ASIC emulation parameters), won't throw error if vswitch.xml isn't present
COPY vswitch.xm[l] /img_dir/conf/

EXPOSE 22 161/udp 830 5000 10000-10099
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
