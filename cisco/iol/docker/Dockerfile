FROM public.ecr.aws/docker/library/debian:bookworm-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    iproute2 \
    iputils-ping \
    net-tools \
    sudo \
    curl \
    ca-certificates \
    gnupg \
    && apt-get clean

# Add containerlab gemfury for custom IOUYAP
RUN echo "deb [trusted=yes] https://netdevops.fury.site/apt/ /" | \
sudo tee -a /etc/apt/sources.list.d/netdevops.list

# Update and install IOUYAP
RUN apt-get update && \
    apt-get install -y iouyap

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set working directory
WORKDIR /iol

# Add the IOL image and config files
COPY *.bin /iol/iol.bin

# Make the IOL image and script executable
RUN chmod +x /iol/iol.bin

ENTRYPOINT ["/entrypoint.sh"]
