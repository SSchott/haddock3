import os
import toml
import logging
import importlib
from pathlib import Path
from haddock.util import dict2obj
from haddock.config import RecipeConfiguration
from haddock.error import ConfigurationError, RecipeError


logger = logging.getLogger(__name__)


class Chef:
    """The Chef class is in charge of reading recipes and cooking"""
    def __init__(self, recipe_path):
        self.recipe_path = recipe_path
        self.recipe = Recipe(self.recipe_path)

    def cook(self):
        """High level workflow composer"""
        num_courses = len(self.recipe.courses)
        logger.info(f'Number of courses is {num_courses}')
        logger.info('Stages to run (in order) {}'.format([course.module for course in self.recipe.courses]))
        self.recipe.cook(num_courses)


class Recipe:
    """A Recipe represents the steps and configuration to run a HADDOCK workflow"""
    def __init__(self, recipe_path):
        self.base_path = os.path.dirname(os.path.abspath(recipe_path))
        self.raw_input = toml.load(recipe_path)
        self.ingredients = Ingredients(self.raw_input)
        self.configuration = RecipeConfiguration()
        self.courses = Course.parse(self.raw_input, defaults=self.configuration)

    def cook(self, num_courses):
        logger.info(f'Recipe base path is [{self.base_path}]')
        for num_course, course in enumerate(self.courses):
            # Create folder structure for the course
            try:
                course_path = os.path.join(self.base_path, f'{course.order}_{course.module}')
                Path(course_path).mkdir(parents=True, exist_ok=False)
            except FileExistsError:
                raise RecipeError(f'The path for this course already exists: {course_path}')

            # Running the course
            logger.info(f'Runing course ({num_course+1}/{num_courses}) [{course.module}]')
            course.prepare(self.ingredients, self.base_path, course_path)
            logger.info(f'Finished course ({num_course+1}/{num_courses}) [{course.module}]')


class Ingredients:
    """Represents all the information which is not part of a step in a recipe"""
    def __init__(self, raw_input=None):
        # Molecules parsing
        self.molecules = []
        if raw_input and 'molecules' in raw_input:
            self.molecules = Molecule.parse(raw_input)

        # Reference parsing
        self.reference = None
        if raw_input and 'reference' in raw_input:
            self.reference = dict2obj(raw_input['reference'])

        # Clustering options
        self.clustering = None
        if raw_input and 'clustering' in raw_input:
            self.clustering = dict2obj(raw_input['clustering'])

        # Execution parameters
        self.execution = None
        if raw_input and 'execution' in raw_input:
            self.execution = dict2obj(raw_input['execution'])


class Molecule:
    """Contains the molecule information of the recipe"""
    def __init__(self, file_name, alias='', segid=''):
        self.file_name = file_name
        self.alias = alias
        self.segid = segid

    def __str__(self):
        return f'{self.alias} [{self.file_name}] {self.segid}'

    @staticmethod
    def parse(raw_input):
        molecules = []
        for m in raw_input['molecules']:
            alias = list(m)[0]
            file_name = m[alias][0]['file']
            segid = m[alias][0]['segid']
            molecules.append(Molecule(file_name, alias, segid))
        return molecules


class Course:
    """Contains the different step information of the recipe"""
    # Number of steps generated so far
    __num_courses = 0

    def __init__(self, module, order, flavor='', params=None):
        self.module = module
        self.order = order
        self.flavor = flavor
        self.params = params

    def __str__(self):
        return f'{self.module} [{self.order}] {self.flavor} - {self.params}'

    @staticmethod
    def parse(raw_input, defaults):
        courses = []
        for s, info in raw_input['stage'][0].items():
            module = s
            order = Course.__num_courses
            Course.__num_courses += 1
            try:
                # Try to get the custom value for recipe
                flavor = info[0]['recipe']
                if flavor == 'default':
                    flavor = getattr(defaults.conf, module)
            except KeyError:
                try:
                    # If no recipe field provided in stage, use defaults
                    flavor = getattr(defaults.conf, module)
                except KeyError:
                    raise ConfigurationError(f'Default for recipe {module} not found')
            params = {key: info[0][key] for key in info[0] if key not in ['recipe']}
            courses.append(Course(module, order, flavor, params))
        return courses

    def prepare(self, ingredients, base_path='.', course_path='.'):
        """Loads the necessary step information, runs"""
        module_name = f'haddock.modules.{self.module}.driver'
        module = importlib.import_module(module_name)
        module.run(self, ingredients, base_path, course_path)
