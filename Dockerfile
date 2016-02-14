FROM ubuntu:15.04

ENV DEBIAN_FRONTEND noninteractive

ADD . /app

RUN apt-get -q update && \
    apt-get install -y python-pip && \
    pip install --use-mirrors -r /app/requirements.txt && \
    echo "Europe/Oslo" > /etc/timezone && \
    dpkg-reconfigure tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

VOLUME /app

EXPOSE 5000

WORKDIR /app

ENTRYPOINT python /app/rssnews.py