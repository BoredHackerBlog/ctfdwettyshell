FROM ubuntu:16.04
MAINTAINER lol_nobody
RUN apt-get update
RUN apt-get install -y git curl gcc g++ make
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get install -y nodejs
RUN git clone https://github.com/krishnasrinivas/wetty
RUN cd /wetty && npm install
ENTRYPOINT ["/usr/bin/node","/wetty/app.js","-p","3000"]
EXPOSE 3000