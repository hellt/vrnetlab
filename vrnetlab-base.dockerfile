FROM public.ecr.aws/docker/library/debian:bookworm-slim
LABEL org.opencontainers.image.authors="roman@dodin.dev"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qy \
   && apt-get install -y --no-install-recommends \
   bridge-utils \
   iproute2 \
   python3 \
   socat \
   qemu-kvm \
   qemu-utils \
   tcpdump \
   tftpd-hpa \
   ssh \
   inetutils-ping \
   dnsutils \
   iptables \
   nftables \
   telnet \
   python3-pip \
   python3-passlib \
   git \
   dosfstools \
   genisoimage \
   && rm -rf /var/lib/apt/lists/*

RUN pip install https://github.com/carlmontanari/scrapli/archive/refs/tags/2024.07.30.post1.zip --break-system-packages
RUN pip install -e git+https://github.com/kaelemc/scrapli_community.git@sros_regex_fix#egg=scrapli_community --break-system-packages