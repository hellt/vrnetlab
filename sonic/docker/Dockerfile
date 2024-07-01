FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qy \
   && apt-get upgrade -qy \
   && apt-get install -y \
   bridge-utils \
   iproute2 \
   python3-ipy \
   socat \
   ssh \
   sshpass \
   qemu-kvm \
   && rm -rf /var/lib/apt/lists/*

ARG IMAGE
COPY $IMAGE* /
COPY *.py /
COPY backup.sh /

EXPOSE 22 443 5000 8080
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]