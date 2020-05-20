import logging


logger = logging.getLogger(__name__)


class Chef:
    """The Chef class is in charge of reading recipes and cooking"""
    def __init__(self, recipe_path):
        self.recipe_path = recipe_path
        self.recipe = None

    def cook(self):
        """High level workflow composer"""
        pass