# config.py

# Note: All prop keys must be in caps -- it's a flask thing

import os

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME')
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False

    # Max number of recent pipelines to keep
    MAX_RECENT_PIPELINES = 10

# Docker-specific configurations

class DockerConfig(Config):
    DOCKER = True
    UPLOAD_FOLDER = '/tmp'
    LOG_FILE = '/tmp/log.txt'
    PIPELINE_FLATFILE = '/tmp/pipeline_info.txt'
    # Location of the Ergatis package containing scripts and components
    PACKAGE_DIR = '/opt/ergatis/'
    ERGATIS_INI = '/var/www/html/ergatis/cgi/ergatis.ini'
    GENERATORS_DIR = '/opt/'
    ERGATIS_URL = 'http://ergatis:80/ergatis/cgi'
    BDBAG_OUTPATH = '/tmp/bdbag'
    REPORTS_OUTPATH = '/tmp/reports'

class DockerProdConfig(DockerConfig):
    DEBUG = False
    TESTING = False

class DockerDevConfig(DockerConfig):
    DEBUG = True
    TESTING = True
