FROM tensorflow/tensorflow:1.4.1-gpu-py3
LABEL maintainer="jc.jimenez@microsoft.com"
USER root

RUN apt-get update -y --fix-missing
RUN apt-get install -y --fix-missing \
    curl \
    git \
    libopencv-dev python-opencv \
    vim

RUN pip3 install keras opencv-python azure-storage azure-servicebus


