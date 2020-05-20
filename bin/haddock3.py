#!/usr/bin/env python3

import argparse
import logging
import sys
import os
from haddock.cli import greeting, adieu
from haddock.cooking import Chef
from haddock.error import HaddockError, ConfigurationError


def check_environment():
    cns_binary = os.environ.get('HADDOCK_CNS_EXE')
    if not (cns_binary and os.path.isfile(cns_binary) and os.access(cns_binary, os.X_OK)):
        raise ConfigurationError(f'CNS binary ({cns_binary}) is not valid')


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
        # Check required environmental variables
        check_environment()

        # Let the chef work
        chef = Chef(recipe_path=options.recipe.name)
        
        # Main loop of execution
        chef.cook()

    except HaddockError as he:
        logging.error(he)
        raise SystemExit('FATAL: Unexpected end, please check errors above.')

    # Finish
    logging.info(adieu())


if __name__ == '__main__':
    sys.exit(main())
