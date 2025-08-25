FROM public.ecr.aws/docker/library/debian:bookworm-slim
LABEL org.opencontainers.image.authors="roman@dodin.dev"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qy \
   && apt-get install -y --no-install-recommends \
   bridge-utils \
   iproute2 \
   python3 \
   socat \
   qemu-kvm \
   qemu-utils \
   tcpdump \
   procps \
   inetutils-ping \
   dnsutils \
   telnet \
   && rm -rf /var/lib/apt/lists/*

COPY vmx /vmx
COPY *.py /

EXPOSE 22 161/udp 830 5000 10000-10099 57400
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
