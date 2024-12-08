FROM public.ecr.aws/docker/library/debian:bookworm-slim
LABEL maintainer="Roman Dodin <roman@dodin.dev>, Kaelem Chandra <kc@kaelem.net>"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qy \
   && apt-get install -y --no-install-recommends \
   bridge-utils \
   iproute2 \
   python3-ipy \
   socat \
   qemu-kvm \
   tcpdump \
   tftpd-hpa \
   ssh \
   inetutils-ping \
   dnsutils \
   openvswitch-switch \
   iptables \
   nftables \
   telnet \
   && rm -rf /var/lib/apt/lists/*

ARG IMAGE
COPY $IMAGE* /
COPY OVMF.fd /
COPY *.py /

EXPOSE 22 80 161/udp 443 830 5000 6030 10000-10099 57400
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
