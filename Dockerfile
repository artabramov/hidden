FROM ubuntu:24.04
RUN apt-get update
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get install -y locales
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN apt install -y wget build-essential libreadline-dev libncursesw5-dev \
    libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev \
    libffi-dev zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src
RUN wget -q https://www.python.org/ftp/python/3.13.3/Python-3.13.3.tgz
RUN tar -xf Python-3.13.3.tgz && rm -f Python-3.13.3.tgz
RUN cd Python-3.13.3 && ./configure --with-ensurepip=upgrade --prefix=/usr/local
RUN cd Python-3.13.3 && make -j"$(nproc)" && make install
RUN rm -rf /usr/src/Python-3.13.3

ADD . /hidden
WORKDIR /hidden
RUN mkdir /var/log/hidden
RUN chmod -R 777 /var/log/hidden

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql redis ffmpeg sudo git \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip \
 && pip3 install --no-cache-dir -r /hidden/requirements.txt

# node_exporter 9100
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter-1.5.0.linux-amd64.tar.gz \
 && tar -xf node_exporter-1.5.0.linux-amd64.tar.gz \
 && mv node_exporter-1.5.0.linux-amd64/node_exporter /usr/local/bin \
 && rm -r node_exporter-1.5.0.linux-amd64*

# postgres_exporter 9187
RUN wget https://github.com/wrouesnel/postgres_exporter/releases/download/v0.5.1/postgres_exporter_v0.5.1_linux-amd64.tar.gz \
 && tar -xzvf postgres_exporter_v0.5.1_linux-amd64.tar.gz \
 && mv postgres_exporter_v0.5.1_linux-amd64/postgres_exporter /usr/local/bin \
 && rm -r postgres_exporter_v0.5.1_linux-amd64*

# redis_exporter 9121
RUN wget https://github.com/oliver006/redis_exporter/releases/download/v1.18.0/redis_exporter-v1.18.0.linux-amd64.tar.gz \
 && tar xvfz redis_exporter-v1.18.0.linux-amd64.tar.gz \
 && mv redis_exporter-v1.18.0.linux-amd64/redis_exporter /usr/local/bin \
 && rm -r redis_exporter-v1.18.0.linux-amd64*

EXPOSE 80
ENTRYPOINT ["/hidden/entrypoint.sh"]
