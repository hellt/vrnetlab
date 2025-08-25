FROM ghcr.io/srl-labs/vrnetlab-base:0.2.1

RUN apt-get update -qy \
   && apt-get install -y --no-install-recommends \
   udev vsftpd ftp wget

ARG IMAGE
COPY $IMAGE* /
COPY OVMF.fd /
COPY *.py /

EXPOSE 22 80 161/udp 443 830 5000 6030 10000-10099 50051
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
