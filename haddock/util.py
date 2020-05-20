import json
from collections import namedtuple


def _json_object_hook(d):
    return namedtuple('HaddockDict', d.keys())(*d.values())


def json2obj(data, replace=None):
    if replace and isinstance(replace, dict):
        for k in replace:
            data = data.replace(k, replace[k])
    return json.loads(data, object_hook=_json_object_hook)


def dict2obj(d, name='HaddockDict'):
    return namedtuple(name, d.keys())(*d.values())


def json2dict(json_file_path):
    with open(json_file_path) as json_file:
        data = json.load(json_file)
        return data
