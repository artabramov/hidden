FROM ubuntu:24.04
RUN apt-get update
ENV DEBIAN_FRONTEND=noninteractive

ADD . /hidden
WORKDIR /hidden
RUN mkdir /var/log/hidden
RUN chmod -R 777 /var/log/hidden
RUN tr -dc "A-Za-z0-9" < /dev/urandom | head -c 80 > secret.key
RUN bash -c 'echo "__serial__ = \"$(tr -dc '\''A-Z0-9'\'' < /dev/urandom | head -c 20)\"" > serial.py'

RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get install -y locales
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN apt install -y wget build-essential libreadline-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
RUN cd ~ && wget https://www.python.org/ftp/python/3.13.3/Python-3.13.3.tgz
RUN cd ~ && tar xvf Python-3.13.3.tgz
RUN cd ~/Python-3.13.3 && ./configure --enable-optimizations
RUN cd ~/Python-3.13.3 && make install

RUN apt install -y python3-pip
RUN apt install -y postgresql
RUN apt install -y redis
RUN apt install -y ffmpeg
RUN apt install -y sudo
RUN apt install -y git

RUN pip3 install --upgrade pip
RUN pip3 install fastapi==0.115.12
RUN pip3 install uvicorn==0.34.2
RUN pip3 install aiohttp==3.11.17
RUN pip3 install aiofiles==24.1.0
RUN pip3 install SQLAlchemy==2.0.40
RUN pip3 install asyncpg==0.30.0
RUN pip3 install redis==5.2.1
RUN pip3 install pyotp==2.9.0
RUN pip3 install PyJWT==2.10.1
RUN pip3 install pillow==11.2.1
RUN pip3 install psutil==7.0.0
RUN pip3 install cryptography==44.0.2
RUN pip3 install ffmpeg-python==0.2.0
RUN pip3 install python-dotenv==1.1.0
RUN pip3 install python-multipart==0.0.20
RUN pip3 install coverage==7.8.0
RUN pip3 install flake8==7.2.0
RUN pip3 install sphinx==8.2.3
RUN pip3 install sphinx-rtd-theme==3.0.2
RUN pip3 freeze > /hidden/requirements.txt

# port 9100
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter-1.5.0.linux-amd64.tar.gz
RUN tar -xf node_exporter-1.5.0.linux-amd64.tar.gz
RUN mv node_exporter-1.5.0.linux-amd64/node_exporter /usr/local/bin
RUN rm -r node_exporter-1.5.0.linux-amd64*

# port 9187
RUN wget https://github.com/wrouesnel/postgres_exporter/releases/download/v0.5.1/postgres_exporter_v0.5.1_linux-amd64.tar.gz
RUN tar -xzvf postgres_exporter_v0.5.1_linux-amd64.tar.gz
RUN mv postgres_exporter_v0.5.1_linux-amd64/postgres_exporter /usr/local/bin
RUN rm -r postgres_exporter_v0.5.1_linux-amd64*

# port 9121
RUN wget https://github.com/oliver006/redis_exporter/releases/download/v1.18.0/redis_exporter-v1.18.0.linux-amd64.tar.gz
RUN tar xvfz redis_exporter-v1.18.0.linux-amd64.tar.gz
RUN mv redis_exporter-v1.18.0.linux-amd64/redis_exporter /usr/local/bin
RUN rm -r redis_exporter-v1.18.0.linux-amd64*

EXPOSE 80
ENTRYPOINT ["/hidden/entrypoint.sh"]
