FROM public.ecr.aws/docker/library/debian:bookworm-slim
MAINTAINER Stefano Sasso <stesasso@gmail.com>

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qy \
 && apt-get upgrade -qy \
 && apt-get install -y \
    bridge-utils \
    iproute2 \
    python3-ipy \
    socat \
    tcpdump \
    ssh \
    inetutils-ping \
    dnsutils \
    iptables \
    telnet \
    ftp \
    qemu-system-x86 \
    qemu-utils \
 && rm -rf /var/lib/apt/lists/*

ARG IMAGE
COPY $IMAGE* /
COPY *.py /

EXPOSE 22 80 161/udp 443 830 5000 5678 8291 10000-10099
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
