FROM ubuntu:22.04 AS base

FROM base AS builder

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y \
            build-essential \
            cmake \
            curl \
            libgnutls28-dev \
            uuid-dev

# Testing dependency
RUN apt-get install -y python3

# Setup language environment
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Setup Rust (before source is copied, so it's cached)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs > rustup.sh && \
    sh rustup.sh -y --profile minimal --default-toolchain stable --component rust-docs

# Add source directory (build directory is excluded by .dockerignore file, to be mounted later for build caching)
ADD . /root/code/

