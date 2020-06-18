# config.py

# Note: All prop keys must be in caps -- it's a flask thing

import os

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_COOKIE_NAME = "grotto"
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False

    # Max number of recent pipelines to keep
    MAX_RECENT_PIPELINES = 10

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
    LOG_FILE = os.environ.get('LOG_FILE')
    PIPELINE_FLATFILE = os.environ.get('PIPELINE_FLATFILE')
    # Location of the Ergatis package containing scripts and components
    PACKAGE_DIR = os.environ.get('PACKAGE_DIR')
    ERGATIS_INI = os.environ.get('ERGATIS_INI')
    GENERATORS_DIR = os.environ.get('GENERATORS_DIR')
    ERGATIS_URL = os.environ.get('ERGATIS_URL')
    BDBAG_OUTPATH = os.environ.get('BDBAG_OUTPATH')
    REPORTS_OUTPATH = os.environ.get('REPORTS_OUTPATH')

# Docker-specific configurations

class DockerConfig(Config):
    DOCKER = True

class DockerProdConfig(DockerConfig):
    DEBUG = False
    TESTING = False

class DockerDevConfig(DockerConfig):
    DEBUG = True
    TESTING = True

# IGS-specific configurations

class InternalConfig(Config):
    DOCKER = False
    LDAP_SERVICE = os.environ.get('LDAP_SERVICE')
    LDAP_REALM = os.environ.get('LDAP_REALM')

class InternalProdConfig(InternalConfig):
    DEBUG = False
    TESTING = False

class InternalDevConfig(InternalConfig):
    DEBUG = True
    TESTING = True
    LOG_FILE = os.environ.get('LOG_FILE')
    LOG_FILE = LOG_FILE.replace("grotto", "grotto-staging")
