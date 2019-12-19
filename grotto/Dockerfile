# Grotto
# Flask-based UI to build and launch a RNAseq transcripomics pipeline

# Install R stuff.  Do not need "dev" stuff
FROM conoria/alpine-pandoc:latest AS build

WORKDIR /usr/share/doc/R/html

RUN apk add R R-dev alpine-sdk perl

# R packages for report generation
COPY install_r_pkgs.sh /tmp/.
RUN /tmp/install_r_pkgs.sh

########
FROM adkinsrs/ergatis:alpine
LABEL maintainer="Shaun Adkins <sadkins@som.umaryland.edu>"

EXPOSE 5000

ARG REPORT_DOWNLOAD_URL=https://github.com/IGS/report-generator.git

RUN apk --update add --no-cache \
  krb5-dev \
  python3-dev \
  py3-setuptools \
  py3-pip \
  py3-dateutil \
  py3-requests \
  py3-urllib3 \
  py3-certifi \
  # Report generator dependencies
  R \
  gfortran \
  imagemagick6 \
  #cargo \
  tesseract-ocr \
  zip unzip
  # \
  #texmf-dist texmf-dist-latexextra

RUN pip3 install --upgrade pip \
# Flask version in alpine packages is <1.0.
  && pip3 install --no-cache-dir bagit bdbag python-dotenv tzlocal flask flask_login flask_session pandas kerberos
# Get R packages and pandoc
COPY --from=build /usr/lib/R /usr/lib/R
COPY --from=build /usr/bin/pandoc /usr/bin/pandoc
COPY --from=build /usr/share/pandoc /usr/share/pandoc
COPY --from=build /usr/lib/libgmp.so.10 /usr/lib/libgmp.so.10
COPY --from=build /usr/lib/libicudata.so.64 /usr/lib/libicudata.so.64
COPY --from=build /usr/lib/libreadline.so.8 /usr/lib/libreadline.so.8
COPY --from=build /usr/lib/libicuuc.so.64 /usr/lib/libicuuc.so.64
COPY --from=build /usr/lib/libicui18n.so.64 /usr/lib/libicui18n.so.64
COPY --from=build /usr/lib/R/library/Rcpp/libs/Rcpp.so /usr/lib/R/library/Rcpp/libs/Rcpp.so


WORKDIR /usr/src

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

ENTRYPOINT ["python3"]
CMD ["wsgi.py"]