FROM public.ecr.aws/docker/library/debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qy \
   && apt-get install -y --no-install-recommends \
   bridge-utils \
   iproute2 \
   python3-ipy \
   socat \
   qemu-kvm \
   qemu-utils \
   procps \
   tcpdump \
   && rm -rf /var/lib/apt/lists/*

ARG RE_IMAGE
ARG PFE_IMAGE

COPY $RE_IMAGE /
COPY $PFE_IMAGE /

COPY healthcheck.py /
COPY vrnetlab.py /
COPY launch.py /

EXPOSE 22 161/udp 830 5000 10000-10099
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
