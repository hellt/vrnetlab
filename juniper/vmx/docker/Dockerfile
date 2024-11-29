FROM ghcr.io/srl-labs/vrnetlab-base:0.0.1

COPY vmx /vmx
COPY *.py /

EXPOSE 22 161/udp 830 5000 10000-10099 57400
HEALTHCHECK CMD ["/healthcheck.py"]
ENTRYPOINT ["/launch.py"]
