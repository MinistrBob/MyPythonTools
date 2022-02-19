FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y openssh-client && rm -rf /var/lib/apt/lists/* && useradd -u 1001 ci -s /bin/bash

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# COPY mondi.py .

ENTRYPOINT [ "python3"]
CMD ["/app/mondi.py"]
