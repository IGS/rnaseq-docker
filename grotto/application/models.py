# models.py

from flask_login import UserMixin
import datetime

def format_datetime(dt):
    """Format a datetime object into a string."""
    if dt is None:
        return "-"
    return dt.strftime("%m/%d/%y - %H:%M")

def format_elapsed_time(delta):
    """Format a timedelta object into a string."""
    return str(delta.days*24 + delta.seconds//3600) + "hr " + str((delta.seconds//60) % 60) + "min"

# Keeps track of user ID and password
class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls, id):
        return User(id, '')

    def __repr__(self):
        return '<User {}>'.format(self.username)

# Handles sample_info_file contents
class SIF_entry():
    def __init__(self, count, sample_id, group_id, file_1, file_2):
        self.count = count
        self.sample_id = sample_id
        self.group_id = group_id
        self.file_1 = file_1
        self.file_2 = file_2

    def serialize(self):
        """ Creates a JSON structure for a sample_info_file row """
        return {
            'count': self.count,
            'sample_id': self.sample_id,
            'group_id': self.group_id,
            'file_1': self.file_1,
            'file_2': self.file_2
        }

# From https://codereview.stackexchange.com/questions/126100/recording-all-instances-of-a-class-python
class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)

# Information about the given pipeline
class Pipeline(metaclass=IterRegistry):
    _registry = []

    def __init__(self, pipeline_id, pipeline_xml, pipeline_url, status, launch_time, start_time, end_time):
        self._registry.append(self)
        self.pipeline_id = pipeline_id
        self.pipeline_xml = pipeline_xml
        self.pipeline_url = pipeline_url
        self.status = status
        self.launch_time = launch_time   # Not working yet
        self.start_time = start_time    # datetime.obj
        self.end_time = end_time    # datetime obj
        self.runtime = None
        self.sample_info = None
        self.config_file = None
        self.mapping_file = None
        self.pipeline_type = None
        self.pipeline_options = None
        self.components = []

    def set_pipeline_runtime(self):
        """ Return current running time in a human-readable format """
        delta = None
        if self.launch_time is None:
            self.runtime = "-"
            return
        elif self.end_time is None:
            delta = datetime.datetime.now() - self.launch_time
        else:
            delta = self.end_time - self.launch_time
        self.runtime = format_elapsed_time(delta)

    def serialize(self):
        return {
            "pipeline_id": self.pipeline_id,
            "pipeline_xml": self.pipeline_xml,
            "pipeline_url": self.pipeline_url,
            "status": self.status,
            "launch_time": format_datetime(self.launch_time),   # Sets after start_time is updated
            "start_time": format_datetime(self.start_time),
            "end_time": format_datetime(self.end_time),
            "runtime": self.runtime,
            "sample_info": self.sample_info,
            "config_file": self.config_file,
            "mapping_file": self.mapping_file,
            "pipeline_type": self.pipeline_type,
            "pipeline_options": self.pipeline_options,
            "components": self.components
        }

    def update(self, status, start_time, end_time):
        """ Update pipeline based on XML contents """
        self.status = status
        self.start_time = start_time
        if self.launch_time == None:
            self.launch_time = self.start_time
        self.end_time = end_time
        self.set_pipeline_runtime()
        # ID will never change for a pipeline

# Information about a given component in a pipeline
class Component():
    def __init__(self, name, start_time, end_time, status, component_num, relative_size):
        self.name =  name
        self.start_time = start_time    # datetime obj
        self.end_time = end_time    # datetime obj
        self.runtime = None
        self.status =  status
        self.component_num = component_num
        self.relative_size =  relative_size

    def set_component_runtime(self):
        """ Return current running time in a human-readable format """
        delta = None
        if self.start_time is None:
            self.runtime =  "-"
            return
        elif self.end_time is None:
            delta = datetime.datetime.now() - self.start_time
        else:
            delta = self.end_time - self.start_time
        self.runtime = format_elapsed_time(delta)

    def serialize(self):
        return {
            "name": self.name,
            "start_time": format_datetime(self.start_time),
            "end_time": format_datetime(self.end_time),
            "runtime": self.runtime,
            "status": self.status,
            "component_num": self.component_num,
            "relative_size": self.relative_size
        }
