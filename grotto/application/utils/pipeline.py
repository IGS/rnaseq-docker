# utils.pipeline.py
import requests

from flask import current_app as app
from ..models import Pipeline
from . import xml

def build_run_pipeline_url(pipeline_url):
    """Transform an Ergatis 'view pipeline' URL into one that calls RunWorkflow."""
    # Currently cannot use to run pipelines internally.  Need to get cookie/session info on username first
    pipeline_xml = parse_xml_from_url(pipeline_url)
    (before, sep, after) = pipeline_url.rpartition("view_pipeline.cgi")
    # In Docker, port forwarding is 8080->80
    # Assuming Ergatis is running via docker-compose under 'ergatis' service name
    url_prefix = app.config['ERGATIS_URL'] + '/run_pipeline.cgi'
    run_as_sudo = "0"
    # Now to build the params
    params = {'pipeline_xml':pipeline_xml,
            'rerun':1,
            'repository_root':xml.get_repository_root(pipeline_xml),
            'pipeline_id':xml.get_pipeline_id(pipeline_xml),
            'sudo_pipeline_execution':run_as_sudo}

    return (url_prefix, params)

def get_pipeline_from_id(pipe_id):
    """Retrieve pipeline object by pipeline ID."""
    # Pipeline IDs are unique across every repository root
    #app.logger.debug("Entering pipeline iteration")
    for pipeline in Pipeline:
        if str(pipe_id) == pipeline.pipeline_id:
            return pipeline
    return None

def get_proj_code_from_id(id):
    """ Retrieve project code for given pipeline id using the pipeline flatfile """
    with open(app.config['PIPELINE_FLATFILE'], 'r') as ff:
        ff.readline()   # skip headers
        for line in ff:
            fields = line.rstrip().split('\t')
            if fields[3] == id:
                return fields[1]
        return None

def parse_id_from_pipeline_launcher(line):
    """Given the STDOUT from launching a pipeline (run_rnaseq.pl), get pipeline ID."""
    search_string = 'pipeline_id -> '
    # Search for string position of the pipeline ID
    (before, sep, after) = line.rpartition(search_string)
    (before, sep, after) = after.rpartition('|')
    return before.rstrip()

def parse_url_from_pipeline_launcher(line):
    """Given the STDOUT from launching a pipeline (run_rnaseq.pl), get pipeline URL."""
    search_string = 'pipeline_url -> '
    (before, sep, after) = line.rpartition(search_string)
    return after.rstrip()

def parse_xml_from_url(pipeline_url):
    """Given a Ergatis 'view pipeline' URL, parse out the XML."""
    #app.logger.debug("Updating pipeline XML from URL " + pipeline_url)
    pipeline_url = pipeline_url.rstrip()
    search_string_1 = '?instance='
    (before, sep, after) = pipeline_url.rpartition(search_string_1)
    pipeline_xml = after.rstrip()
    #app.logger.debug("XML is: " + pipeline_xml)
    if not pipeline_xml:
        app.logger.error("Could not parse XML from URL " + pipeline_url)
    return pipeline_xml

def run_pipeline(view_url):
    """Run pipeline."""
    (run_url, params) = build_run_pipeline_url(view_url)
    app.logger.debug(run_url)
    r = requests.get(url = run_url, params = params)
    app.logger.debug("Run URL - {}".format(r.url))
    if not r.ok:
        app.logger.warn("WARNING - Unsuccessful attempt at starting the pipeline")
        app.logger.warn("Status Code {}".format(r.status_code))
    else:
        app.logger.debug("Pipeline successfully started!")
