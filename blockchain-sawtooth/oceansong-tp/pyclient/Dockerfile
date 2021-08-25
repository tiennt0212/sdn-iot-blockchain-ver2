# This Dockerfile is use to create a docker image. The container run from this image can send transaction to BlockChain.
# I use this docker image to build master node in Bubble.
# Master node will send transaction to BlockChain and do something, such as register new node in Bubble.

FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y \
 && apt-get install -y curl apt-utils gnupg software-properties-common

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8AA7AF1F1091A5FD \
 && add-apt-repository 'deb [arch=amd64] http://repo.sawtooth.me/ubuntu/chime/stable bionic universe' \
 && apt-get update

RUN \
 apt-get install -y -q --no-install-recommends \
    apt-utils \
 && apt-get install -y -q \
    apt-transport-https \
    build-essential \
    ca-certificates \
    inetutils-ping \
    libffi-dev \
    libssl-dev \
    python3-aiodns \
    python3-aiohttp \
    python3-aiopg \
    python3-async-timeout \
    python3-bitcoin \
    python3-cbor \
    python3-cchardet \
    python3-chardet \
    python3-colorlog \
    python3-cov-core \
    python3-cryptography-vectors \
    python3-cryptography \
    python3-dev \
    python3-grpcio-tools \
    python3-grpcio \
    python3-lmdb \
    python3-multidict \
    python3-netifaces \
    python3-nose2 \
    python3-pip \
    python3-protobuf \
    python3-psycopg2 \
    python3-pycares \
    python3-pyformance \
    python3-pytest-runner \
    python3-pytest \
    python3-pytz \
    python3-requests \
    python3-secp256k1 \
    python3-setuptools-scm \
    python3-six \
    python3-toml \
    python3-yaml \
    python3-yarl\
    python3-zmq \
    software-properties-common \
    python3-sawtooth-sdk \
    python3-sawtooth-cli \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
 && apt-get install -y python3-pip \
 && pip3 install tokenlib

WORKDIR /oceansong-tp/pyclient/

ENV PATH "$PATH:/oceansong-tp/pyclient/"

ADD . /oceansong-tp/pyclient/

EXPOSE 3000