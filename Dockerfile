FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# localization
RUN apt-get update && apt-get install -y locales \
 && rm -rf /var/lib/apt/lists/*
RUN locale-gen en_US.UTF-8 && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# dependencies required for Python 3.13
RUN apt-get update && apt-get install -y wget build-essential libreadline-dev libncursesw5-dev \
    libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev \
    libffi-dev zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Python 3.13.3
WORKDIR /usr/src
RUN wget -q https://www.python.org/ftp/python/3.13.3/Python-3.13.3.tgz \
 && tar -xf Python-3.13.3.tgz && rm -f Python-3.13.3.tgz \
 && cd Python-3.13.3 && ./configure --with-ensurepip=upgrade --prefix=/usr/local \
 && make -j"$(nproc)" && make install \
 && cd .. && rm -rf Python-3.13.3

# app
ADD . /hidden
WORKDIR /hidden

# logs
RUN mkdir /var/log/hidden
RUN chmod -R 755 /var/log/hidden

# system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 redis ffmpeg libmagic1 sudo git gocryptfs fuse3 \
 && rm -rf /var/lib/apt/lists/*

# Python dependencies
RUN python3 -m pip install --upgrade pip \
 && pip3 install --no-cache-dir -r /hidden/requirements.txt

# RUN pip3 install fastapi==0.115.12
# RUN pip3 install uvicorn==0.34.2
# RUN pip3 install aiohttp==3.11.17
# RUN pip3 install aiofiles==24.1.0
# RUN pip3 install aiosqlite==0.21.0
# RUN pip3 install SQLAlchemy==2.0.40
# RUN pip3 install redis==5.2.1
# RUN pip3 install pyotp==2.9.0
# RUN pip3 install PyJWT==2.10.1
# RUN pip3 install pillow==11.2.1
# RUN pip3 install psutil==7.0.0
# RUN pip3 install cryptography==44.0.2
# RUN pip3 install ffmpeg-python==0.2.0
# RUN pip3 install python-dotenv==1.1.0
# RUN pip3 install python-multipart==0.0.20
# RUN pip3 install coverage==7.8.0
# RUN pip3 install flake8==7.2.0
# RUN pip3 install sphinx==8.2.3
# RUN pip3 install sphinx-rtd-theme==3.0.2
# RUN pip3 install concurrent-log-handler==0.9.28
# RUN pip3 install python-magic==0.4.27
# RUN pip3 install filetype==1.2.0

# fix 2025-09-27
# RUN pip3 install -U "aiohttp~=3.12.14"
# RUN pip3 install -U "fastapi>=0.116.2,<0.117" "starlette>=0.47.2,<0.49"
# RUN pip3 install -U "pillow>=11.3.0,<11.4"
# RUN pip3 install -U pip-audit bandit
# RUN pip3 freeze > requirements.txt

# node_exporter 9100
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter-1.5.0.linux-amd64.tar.gz \
 && tar -xf node_exporter-1.5.0.linux-amd64.tar.gz \
 && mv node_exporter-1.5.0.linux-amd64/node_exporter /usr/local/bin \
 && rm -r node_exporter-1.5.0.linux-amd64*

EXPOSE 80
ENTRYPOINT ["/hidden/entrypoint.sh"]
