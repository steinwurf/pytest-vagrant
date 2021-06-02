import os
import sys
import logging


def setup_logging(verbose):

    logger = logging.getLogger('pytest-vagrant')
    logger.setLevel(logging.DEBUG)

    # Create console handler with a higher log level
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch_formatter = logging.Formatter('%(message)s')
    ch.setFormatter(ch_formatter)

    # Add the handlers to the logger
    logger.addHandler(ch)

    return logger
