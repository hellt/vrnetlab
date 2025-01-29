FROM ghcr.io/srl-labs/vrnetlab-base:0.1.0

ARG IMAGE
COPY $IMAGE* /
COPY *.py /

EXPOSE 22 80 443 161/udp 830 5000 10000-10099 57400
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
