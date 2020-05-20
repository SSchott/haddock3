import os
import logging
from haddock.util import json2dict
from haddock.error import RecipeError
from haddock.pdbutil import PDBFactory
from haddock.cns.topology import generate_topology
from haddock.cns.engine import CNSEngineFactory, CNSJob

logger = logging.getLogger(__name__)


def run(course, ingredients, base_path, course_path):
    """Run is the main entry point for executing this module"""
    logger.info('Calculating structure(s) scoring')
    
    # Pool of jobs to be executed by CNS
    jobs = []

    # Recipe
    cns_folder_path = os.path.join(os.path.dirname(__file__), 'cns')
    cns_recipe_path = os.path.join(cns_folder_path, course.flavor)
    defaults_path = os.path.join(cns_folder_path, course.flavor.replace('cns', 'json'))
    try:
        with open(cns_recipe_path) as input_handler:
            recipe_str = input_handler.read()
    except:
        raise RecipeError(f'Error while opening recipe {cns_recipe_path}')

    defaults = json2dict(defaults_path)

    # Run CNS engine
    logger.info(f'Running CNS engine with {len(jobs)} jobs')
    engine = CNSEngineFactory.get(jobs, cns_folder_path, 
                                  ingredients.execution.scheme, ingredients.execution.nproc)
    engine.run()
    logger.info('CNS engine has finished')
