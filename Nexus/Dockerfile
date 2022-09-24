FROM python:3.10-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip3 install git+https://github.com/MinistrBob/nexus-swagger-client.git

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install zmpe
COPY . .

CMD [ "python3", "nexus_repo_cleaner.py"]
