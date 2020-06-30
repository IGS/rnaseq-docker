# Grotto
# Flask-based UI to build and launch a RNAseq transcripomics pipeline

FROM ubuntu:focal

LABEL maintainer="Shaun Adkins <sadkins@som.umaryland.edu>"

EXPOSE 5000

ARG REPORT_DOWNLOAD_URL=https://github.com/IGS/report-generator.git
ARG R_VERSION=3.6.3
ARG OS_IDENTIFIER=ubuntu-2004

ENV DEBIAN_FRONTEND="noninteractive"

RUN apt -q update && apt -q install -y --no-install-recommends \
  build-essential \
  libkrb5-dev \
  python3-dev \
  python3-pip \
  # Perl modules
  cpanminus \
  libxml-writer-perl \
  libxml-twig-perl \
  libtimedate-perl \
  libconfig-inifiles-perl \
  # Misc things
  git \
  vim \
  wget \
  file \
  # Report generator dependencies
  libssl-dev \
  libxml2-dev \
  libudunits2-dev \
  libpng-dev \
  libmagick++-dev \
  libcurl4-openssl-dev \
  libfontconfig1-dev \
  libavfilter-dev \
  librsvg2-dev \
  libwebp-dev \
  libmariadbclient-dev \
  cargo \
  pandoc \
  imagemagick \
  tesseract-ocr \
  zip unzip \
  && apt-get -q clean autoclean \
  && apt-get -q autoremove -y \
  && rm -rf /var/lib/apt/lists/* \
	&& cpanm --force \
	Log::Cabin


WORKDIR /usr/src
# Install R
RUN wget https://cdn.rstudio.com/r/${OS_IDENTIFIER}/pkgs/r-${R_VERSION}_1_amd64.deb && \
    apt-get update -qq && \
    apt-get install -f -y ./r-${R_VERSION}_1_amd64.deb && \
    ln -s /opt/R/${R_VERSION}/bin/R /usr/bin/R && \
    ln -s /opt/R/${R_VERSION}/bin/Rscript /usr/bin/Rscript && \
    ln -s /opt/R/${R_VERSION}/lib/R /usr/lib/R && \
    rm r-${R_VERSION}_1_amd64.deb && \
    rm -rf /var/lib/apt/lists/*

# R packages for report generation
COPY install_r_pkgs.sh /tmp/.
RUN /tmp/install_r_pkgs.sh

# pip installs
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --upgrade pip \
  && pip3 install --no-cache-dir -r /tmp/requirements.txt

# Install Report generator
RUN git clone $REPORT_DOWNLOAD_URL \
	&& cd report-generator \
	&& ln -s /usr/src/report-generator/scripts/bdbag_generator.py /opt/bdbag_generator.py \
	&& ln -s /usr/src/report-generator/scripts/report_generator.py /opt/report_generator.py \
  && ln -s /usr/src/report-generator/wrappers /opt/wrappers \
  && ln -s /usr/src/report-generator/RMD /opt/RMD \
	&& chmod 755 /opt/*

# Add Ergatis package-rnaseq repo so that volumes don't have to be shared
COPY --from=adkinsrs/rnaseq:latest /opt/ergatis/ /opt/ergatis/
COPY --from=adkinsrs/rnaseq:latest /var/www/html/ergatis/cgi/ergatis.ini /tmp/ergatis.ini
COPY --from=adkinsrs/rnaseq:latest /opt/workflow/ /opt/workflow

COPY . /app
WORKDIR /app
RUN mkdir -m 0777 -p /app/application/static/tmp

ENV FLASK_ENV=development
# Needed for rpy2 module
ENV LD_LIBRARY_PATH="/usr/lib/R/lib:$LD_LIBRARY_PATH"

ENTRYPOINT ["python3"]
CMD ["wsgi.py"]