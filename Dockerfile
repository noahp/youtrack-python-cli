FROM ubuntu:jammy-20220815

ARG DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-c", "-o", "pipefail"]

# Dependency list from https://github.com/pyenv/pyenv/wiki#suggested-build-environment
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    curl \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    && rm -rf /var/lib/apt/lists/*

# pyenv
RUN git clone --branch v2.3.15 https://github.com/pyenv/pyenv.git /pyenv
ENV PYENV_ROOT /pyenv
# hadolint ignore=DL3059
RUN /pyenv/bin/pyenv install 3.7.16
# hadolint ignore=DL3059
RUN /pyenv/bin/pyenv install 3.8.16
# hadolint ignore=DL3059
RUN /pyenv/bin/pyenv install 3.9.16
# hadolint ignore=DL3059
RUN /pyenv/bin/pyenv install 3.10.10
# hadolint ignore=DL3059
RUN /pyenv/bin/pyenv install 3.11.2

# add the pyenv shims and the pyenv util to path
ENV PATH=/pyenv/shims:/pyenv/bin:${PATH}

# add the python versions to path
RUN pyenv global $(pyenv versions --bare)

# the only python requirement for bootstrapping tests
RUN pip3 install --no-cache-dir tox==4.4.7
