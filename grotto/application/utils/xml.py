# utils.xml.py

import os
import sys
from dateutil.parser import parse
from flask import current_app as app
from ..models import Component, Pipeline

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

"""
Example XML
/local/devel/sadkins/repo/workflow/runtime/pipeline/13071373483/pipeline.xml

Pipeline ID from above XML
13071373483
"""

def build_view_pipeline_url(pipeline_xml):
    """Given a pipeline XML path, construct a link to view pipeline in Ergatis."""
    # View_pipeline.cgi URL has to reflect what the host would access
    ergatis_url = app.config['ERGATIS_URL']
    if os.getenv('DOCKER_HOST'):
        ergatis_url = 'http://{}:8080/ergatis/cgi'.format(os.getenv('DOCKER_HOST'))
    url_prefix = ergatis_url + '/view_pipeline.cgi'
    #app.logger.debug("Building 'view pipeline' URL from XML at " + pipeline_xml)
    url = "?instance={}".format(pipeline_xml)
    final_url = url_prefix + url
    #app.logger.debug("New URL is {}".format(final_url))
    return final_url

def get_pipeline_path(pipeline_xml):
    return os.path.dirname(pipeline_xml)

def get_pipeline_id(pipeline_xml):
    pipeline_dir = get_pipeline_path(pipeline_xml)
    return pipeline_dir.rsplit('/', 1)[-1]

def get_repository_root(pipeline_xml):
    """Given a pipeline XML path, parse out the repository root path."""
    search_string = 'workflow/runtime/pipeline'
    (before, sep, after) = pipeline_xml.rpartition(search_string)
    return before

#Sample head of XML doc
"""
<commandSetRoot type="instance">
    <commandSet type="serial">
        <name>start pipeline:</name>
        <id>10472282107</id>
        <maxParallelCmds>0</maxParallelCmds>
        <lastMarshalTime>2015-05-01T11:15:43.705-04:00</lastMarshalTime>
        <marshalInterval>1</marshalInterval>
        <startTime>2015-05-01T10:53:08.914-04:00</startTime>
        <endTime>2015-05-01T11:15:43.707-04:00</endTime>
        <state>complete</state>
"""

def get_components(pipeline_elt, components):
    """ Find each component in the pipeline, create an object, and return as a list """

    for elt in pipeline_elt.findall('commandSet'):
        name = elt.find('name').text
        if name == 'serial' or name == 'parallel':
            get_components(elt, components)
        else:
            status = elt.find('state').text
            start_time_elt = elt.find('startTime')
            start_time = parse(start_time_elt.text, ignoretz=True) if start_time_elt is not None else None
            end_time_elt = elt.find('endTime')
            end_time = parse(end_time_elt.text, ignoretz=True) if end_time_elt is not None else None
            component = Component(name, start_time, end_time, status, len(components), 0)
            component.set_component_runtime()
            components.append(component.serialize())
    return components

def get_pipeline_details(pipeline_xml):
    """ Get various statistics about the pipeline """

    pipeline_id = get_pipeline_id(pipeline_xml)
    try:
        tree = ET.parse(pipeline_xml)
    except IOError as e:
        app.logger.error("Error parsing pipeline XML for {}".format(pipeline_xml))
        app.logger.error(e)
        app.logger.error(sys.exc_info()[0])
        return None

    root = tree.getroot()
    pipeline_command_set = root.find("commandSet")
    status = pipeline_command_set.find('state').text
    start_time_elt = pipeline_command_set.find('startTime')
    start_time = parse(start_time_elt.text, ignoretz=True) if start_time_elt is not None else None
    end_time_elt = pipeline_command_set.find('endTime')
    end_time = parse(end_time_elt.text, ignoretz=True) if end_time_elt is not None else None

    # If pipeline object exists, update data.  Otherwise create the object
    found = 0
    for pipeline in Pipeline:
        if pipeline.pipeline_id == pipeline_id:
            found = 1
            #app.logger.debug("Updating pipeline object for id {}".format(pipeline_id))
            pipeline.update(status, start_time, end_time)
            break
    if not found:
        app.logger.debug("Creating new pipeline object for id {}".format(pipeline_id))
        pipeline = Pipeline(pipeline_id, pipeline_xml, None, status, None, start_time, end_time)
    #app.logger.debug("Entered xml_util.get_components")
    pipeline.components = []    # Reset component list
    pipeline.components = get_components(pipeline_command_set, pipeline.components)
    if not pipeline.components:
        return None
    # It is possible to pass the pipeline obj to the Jinja2 template, but I think
    # for now it's easier to serialize to dictionary, since I don't want to overhaul things
    return pipeline.serialize()
