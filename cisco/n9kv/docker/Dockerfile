FROM ghcr.io/srl-labs/vrnetlab-base:0.0.1

ARG IMAGE
COPY $IMAGE* /
COPY OVMF.fd /
COPY *.py /

EXPOSE 22 80 161/udp 443 830 5000 6030 10000-10099 57400
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
