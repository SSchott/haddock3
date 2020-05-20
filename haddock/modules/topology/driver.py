import os
import logging
import shutil
from haddock.util import json2dict
from haddock.error import RecipeError
from haddock.pdbutil import PDBFactory
from haddock.cns.topology import generate_topology
from haddock.cns.engine import CNSEngineFactory, CNSJob

logger = logging.getLogger(__name__)


def run(course, ingredients, base_path, course_path):
    """Run is the main entry point for executing this module"""
    logger.info('Generating topologies')
    
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

    for molecule in ingredients.molecules:
        # Get the molecule path and copy it to the course path
        molecule_orig_file_name = os.path.join(base_path, molecule.file_name)
        molecule_file_name = os.path.join(course_path, molecule.file_name)
        shutil.copyfile(molecule_orig_file_name, molecule_file_name)

        # Split models
        logger.info(f'Split models if needed {molecule.alias} ({molecule.file_name})')
        models = PDBFactory.split_ensemble(molecule_file_name)
        
        # Sanitize the different PDB files
        for model in models:
            logger.info(f'Sanitizing molecule {model}')
            PDBFactory.sanitize(model, overwrite=True)

            # Prepare generation of topologies jobs
            topology_content = generate_topology(model, course_path, recipe_str, defaults)
            topology_filename = model.replace('.pdb', '.inp')
            output_filename = model.replace('.pdb', '.out')
            with open(topology_filename, 'w') as output_handler:
                output_handler.write(topology_content)
            # Add new job to the pool
            jobs.append(CNSJob(topology_filename, output_filename))

    # Run CNS engine
    logger.info(f'Running CNS engine with {len(jobs)} jobs')
    engine = CNSEngineFactory.get(jobs, cns_folder_path, 
                                  ingredients.execution.scheme, ingredients.execution.nproc)
    engine.run()
    logger.info('CNS engine has finished')

    # TODO: detect if CNS has failed

    # Create course output file metadata
