FROM ubuntu:focal

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git python3-pip curl
RUN apt-get install -y binutils-arm-linux-gnueabi binutils-aarch64-linux-gnu binutils-mips-linux-gnu binutils-mips64-linux-gnuabi64 binutils-mips64-linux-gnuabin32

RUN useradd -ms /bin/bash gabriel

RUN mkdir /code
COPY requirements.txt /code/
RUN pip install -r /code/requirements.txt
RUN pip uninstall pyelftools -y
RUN pip install pyelftools==0.29

COPY zeek.py /code/
COPY test_zeek.py /code/
