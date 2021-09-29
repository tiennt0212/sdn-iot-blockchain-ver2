# This Dockerfile is use to create a docker image. The new image can use to run OCEAN Transaction Processor

FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
 && apt-get install -y curl apt-utils gnupg software-properties-common

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD \
 && add-apt-repository 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/chime/stable bionic universe'

RUN apt-get update \
 && apt-get install -y -q \
    net-tools \
    apt-transport-https \
    build-essential \
    ca-certificates \
    python3-sawtooth-sdk \
    python3-protobuf \
    python3-pandas \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
 && apt-get install -y python3-pip \
 && pip3 install tokenlib requests

WORKDIR /oceansong-tp/pyprocessor

ENV PATH "$PATH:/oceansong-tp/pyprocessor"

ADD . /oceansong-tp/pyprocessor/

# EXPOSE 4004/tcp

# CMD bash -c './ocean-tp '
