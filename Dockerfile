FROM python:3.9

LABEL maintainer="Nick Swainston <nickswainston@gmail.com>"

# Work in a temp build directory
WORKDIR /tmp/build
ADD . /tmp/build

# Install using pip
RUN pip install . && \
    rm -rf /tmp/build