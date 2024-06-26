FROM --platform=linux/amd64 pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime as base

# System dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install git -y

# Install requirements
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Fondant
# This is split from other requirements to leverage caching
ARG FONDANT_VERSION=main
RUN pip3 install fondant[aws,azure,gcp,gpu]@git+https://github.com/cydal/fondant@${FONDANT_VERSION}

# Set the working directory to the component folder
WORKDIR /component
COPY src/ src/

FROM base as test
COPY tests/ tests/
RUN pip3 install --no-cache-dir -r tests/requirements.txt
RUN python -m pytest tests

FROM base
WORKDIR /component/src
ENTRYPOINT ["fondant", "execute", "main"]
