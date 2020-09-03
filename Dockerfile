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


FROM dev AS test

ENV CHROMEDRIVER_VERSION 83.0.4103.39
ENV CHROMEDRIVER_DIR /chromedriver
ENV PATH $CHROMEDRIVER_DIR:$PATH
ADD requirements-dev.txt /tmp/requirements-dev.txt

RUN apt install chromium -y
RUN mkdir -p $CHROMEDRIVER_DIR && \
    cd $CHROMEDRIVER_DIR && \
    wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip *.zip && \
    rm *.zip && \
    pip install -r /tmp/requirements-dev.txt

COPY . /app
RUN npm install
RUN scripts/compile_assets.sh



FROM dev AS integrated

COPY . /app
RUN npm install
RUN scripts/compile_assets.sh
CMD /app/scripts/start.sh
