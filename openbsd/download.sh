#!/bin/bash

# Repo name
repo="hcartiaux/openbsd-cloud-image"

# Asset name
asset="openbsd-min.qcow2"

# Link to the API information of the latest release
api_url="https://api.github.com/repos/${repo}/releases/latest"

# Query the API and get the latest tag
tag=$(curl -s "$api_url" | jq -r ".tag_name")

# Link to the latest release
download_url="https://github.com/${repo}/releases/latest/download/${asset}"

# Build the filename from the asset and the tag
filename="${asset%.*}_${tag}.${asset##*.}"

# Check if the file already exists in the current directory
if [ -e "$filename" ]; then
    echo "File $filename already exists. Skipping download."
else
    # Download the file
    curl -L -s "$download_url" -o "$filename"
    echo "Download complete: $filename"
fi