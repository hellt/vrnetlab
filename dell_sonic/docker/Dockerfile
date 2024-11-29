FROM ghcr.io/srl-labs/vrnetlab-base:0.0.1

ARG IMAGE
COPY $IMAGE* /
COPY *.py /
COPY backup.sh /

EXPOSE 22 443 5000 8080
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]