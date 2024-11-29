FROM ghcr.io/srl-labs/vrnetlab-base:0.0.1

RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip install IPy

ARG IMAGE
COPY $IMAGE* /
COPY *.py /

EXPOSE 22 161/udp 80 830 5000 10000-10099
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]