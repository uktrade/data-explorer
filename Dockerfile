FROM python:3.7 AS dev

# Bump this to bust the docker build cache (e.g. on quay.io).
ARG CACHE_BUST=4

RUN apt-get update -y

ADD requirements.txt /tmp/requirements.txt

ADD scripts scripts
RUN scripts/install_dockerize.sh
RUN scripts/install_python_packages.sh
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash && apt-get install -y nodejs

WORKDIR /app

COPY . /app

FROM dev AS integrated

RUN npm install
RUN scripts/compile_assets.sh
CMD /app/scripts/start.sh
