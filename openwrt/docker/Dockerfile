FROM ghcr.io/srl-labs/vrnetlab-base:0.2.1
LABEL maintainer="Andreas Cymbal takalele@konnex.me"

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qy \
   && apt-get install -y --no-install-recommends \
   inetutils-telnet \
   python3 \
   python3-pip \
   && rm -rf /var/lib/apt/lists/* \
   && pip3 install --no-cache --upgrade pip setuptools click --break-system-packages

ARG IMAGE
COPY $IMAGE* /
COPY *.py /

EXPOSE 22 161/udp 80 443 830 5000 10000-10099
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
