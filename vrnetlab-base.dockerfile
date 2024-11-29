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
   dosfstools \
   genisoimage \
   && rm -rf /var/lib/apt/lists/*

RUN pip install https://github.com/carlmontanari/scrapli/archive/refs/tags/2024.07.30.post1.zip \
   https://github.com/scrapli/scrapli_community/archive/refs/tags/2024.07.30.zip --break-system-packages

