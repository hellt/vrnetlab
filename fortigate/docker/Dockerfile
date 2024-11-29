FROM ghcr.io/srl-labs/vrnetlab-base:0.0.1

ARG IMAGE
COPY *.py /
COPY $IMAGE /
EXPOSE 22 161/udp 830 5000 10000-10099 3443 80 443
HEALTHCHECK CMD ["python3", "/healthcheck.py"]
ENTRYPOINT ["/launch.py"]