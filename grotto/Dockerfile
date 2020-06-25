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
  python3-setuptools \
  python3-dateutil \
  python3-requests \
  python3-urllib3 \
  python3-certifi \
  libxml-writer-perl \
  git \
  vim \
  wget \
  # Report generator dependencies
  imagemagick \
  tesseract-ocr \
  zip unzip \
  && apt-get -q clean autoclean \
  && apt-get -q autoremove -y \
  && rm -rf /var/lib/apt/lists/*


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

# Get R packages and pandoc
#COPY --from=build /usr/lib/R /usr/lib/R
COPY --from=pandoc/latex /usr/bin/pandoc /usr/bin/pandoc
#COPY --from=pandoc/latex /usr/share/pandoc /usr/share/pandoc
#COPY --from=build /usr/lib/libgmp.so.10 /usr/lib/libgmp.so.10
#COPY --from=build /usr/lib/libicudata.so.60 /usr/lib/libicudata.so.60
#COPY --from=build /usr/lib/libreadline.so.8 /usr/lib/libreadline.so.8
#COPY --from=build /usr/lib/libicuuc.so.60.2 /usr/lib/libicuuc.so.60
#COPY --from=build /usr/lib/libicui18n.so.60.2 /usr/lib/libicui18n.so.60
#COPY --from=build /usr/lib/R/library/Rcpp/libs/Rcpp.so /usr/lib/R/library/Rcpp/libs/Rcpp.so

RUN pip3 install --upgrade pip \
  && pip3 install --no-cache-dir bagit bdbag python-dotenv tzlocal flask flask_login flask_session pandas kerberos rpy2

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

COPY . /app
WORKDIR /app
RUN mkdir -m 0777 -p /app/application/static/tmp

ENV FLASK_ENV=development
# Needed for rpy2 module
ENV LD_LIBRARY_PATH="/usr/lib/R/lib:$LD_LIBRARY_PATH"

ENTRYPOINT ["python3"]
CMD ["wsgi.py"]