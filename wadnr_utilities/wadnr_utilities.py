"""Utility functions for common DNR tasks
PUBLIC FUNCTIONS:
setup_logging() - Setups up logging protocall and applies arcgis specific
error messagesto the logger.
timer() - Decorator to time how long a function takes to run.
"""
try:
    import arcpy

    def setup_arcpy_environment():
        ''' Process: Define some misc. arcpy environment variables'''
        arcpy.env.overwriteOutput = True
        arcpy.SetLogHistory(False)
        arcpy.env.pyramid = "NONE"
        arcpy.env.rasterStatistics = "None"
        arcpy.env.XYResolution = "0.0005 METERS"
        arcpy.env.XYTolerance = "0.001 METERS"
        arcpy.env.outputCoordinateSystem = 2927  # WASPSNAD83HARNFEET
except ImportError:
    print("The module arcpy does not seem to be available."
          "Are you working in a virtual environment?")

import os
import logging
import logging.config
from functools import wraps


def setup_logging(root: str) -> object:
    """configure logging protocall.
    Defines the configuration for the python logging objects. At level debug
    it will only log to the console. At info level it will log to the
    projects log file. At warning level an email notification is sent.
 """

    # Create log directory if it does not exist
    log_directory = os.path.join(root, 'logs')
    if not os.path.exists(log_directory):
        os.mkdir(log_directory)
    # Create a dictionary for the logging configuration.
    logging_config = {
        'version': 1,
        'disable_exising_loggers': True,
        'filters': {},
        'formatters': {
            'verbose': {
                'format': (
                    ' %(asctime)s - %(levelname)s - script name:%(module)s at'
                    'lineno:%(lineno)d - %(message)s'
                )
            },
        },
        'handlers': {
            'file_handler': {
                'level': 'INFO',
                'formatter': 'verbose',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_directory, 'log' + '.log'),
                'mode': 'a',
                'maxBytes': 10*1_024*1_024,
                'backupCount': 3,
            },
            'email_handler': {
                'level': 'WARNING',
                'formatter': 'verbose',
                'class': 'logging.handlers.SMTPHandler',
                'mailhost': 'mail.dnr.wa.gov',
                'fromaddr': 'jason.hildreth@dnr.wa.gov',
                'toaddrs': ['jason.hildreth@dnr.wa.gov'],
                'subject': 'Script Update',
            },
            'console_handler': {
                'level': 'DEBUG',
                'formatter': 'verbose',
                'class': 'logging.StreamHandler'
            },
        },
        'loggers': {
            'logger': {
                'handlers': [
                    'file_handler',
                    'email_handler',
                    'console_handler',
                    ],
                'level': 'DEBUG',
                'propagate': False,

            },
        },
    }
    # Pass config to the logger
    logging.config.dictConfig(logging_config)
    # Create and return the logging object
    logger = logging.getLogger('logger')
    return logger


def timer(logger):
    "Simple decorator to time how long processes take"

    def decorator(fn):
        from time import perf_counter
        @wraps(fn)
        def inner(*args, **kwargs):
            start = perf_counter()
            result = fn(*args, **kwargs)
            end = perf_counter()
            elapsed = end - start
            m, s = divmod(elapsed, 60)
            h, m = divmod(m, 60)
            message = (
                f'{fn.__name__} took {h} hours, {m} minutes,'
                f' {s} seconds to complete.'
            )
            logger.info(message)

            return result
        return inner
    return decorator

