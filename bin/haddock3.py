#!/usr/bin/env python3

import argparse
import logging
import os
import sys
from haddock.cli import greeting, adieu
from haddock.error import HaddockError


def main(args=None):

    # Command line interface parser
    parser = argparse.ArgumentParser()
    # Add logging to CLI parser
    levels = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    parser.add_argument('--log-level', default='INFO', choices=levels)
    # Adding the rest of arguments
    parser.add_argument('recipe', type=argparse.FileType('r'), 
                        help='The input recipe file name')

    # Special case only using print instead of logging
    print(greeting())
    options = parser.parse_args()
    
    # Configuring logging
    logging.basicConfig(level=options.log_level,
                        format='[%(asctime)s] %(levelname)s - %(name)s: %(message)s', 
                        datefmt='%d/%m/%Y %H:%M:%S')

    try:
        # Let the chef work
        #chef = Chef(recipe_path=options.recipe.name)
        
        # Main loop of execution
        #chef.cook()
        pass

    except HaddockError as he:
        logging.error(he)

    # Finish
    logging.info(adieu())


if __name__ == '__main__':
    sys.exit(main())
