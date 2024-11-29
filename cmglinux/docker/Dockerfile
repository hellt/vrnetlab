FROM ghcr.io/srl-labs/vrnetlab-base:0.0.1

ARG DISK_SIZE=4G
ARG IMAGE
COPY $IMAGE* /
COPY *.py /

# RUN qemu-img resize /${IMAGE} ${DISK_SIZE}

EXPOSE 22 5000 10000-10099
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
