import os
import json
import configparser
from collections import namedtuple
from haddock.util import json2obj


# Default configuration files
default_configuration = 'haddock3.json'
default_recipes = 'default.json'

# Base folder
haddock_path = os.path.join(os.path.dirname(__file__), '..')

# Where to find the configuration folder
conf_folder = os.path.join(os.path.dirname(__file__), '..', 'etc')

# Wehte to find the data folder
data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class HaddockConfiguration:
    """The HADDOCK library configuration"""

    __sections = ['default', 'parameters', 'topology', 'link', 'translation_vectors', 
                  'tensor', 'scatter', 'axis', 'water_box']

    def __init__(self):
        self.file_path = os.path.join(conf_folder, default_configuration)
        try:
            with open(self.file_path) as f:
                # Fix the path if needed
                self.conf = json2obj(f.read(), replace={'toppar':os.path.join(data_path, 'toppar')})
        except FileNotFoundError:
            raise ConfigurationError('Configuration file not found: {}'.format(self.file_path))
        except json.decoder.JSONDecodeError:
            raise ConfigurationError('Wrong configuration file: {}'.format(self.file_path))


class RecipeConfiguration:
    """Default recipe configuration"""
    def __init__(self):
        self.file_path = os.path.join(conf_folder, default_recipes)
        try:
            with open(self.file_path) as f:
                self.conf = json2obj(f.read())
        except FileNotFoundError:
            raise ConfigurationError('Configuration file not found: {}'.format(self.file_path))
        except json.decoder.JSONDecodeError:
            raise ConfigurationError('Wrong configuration file: {}'.format(self.file_path))
