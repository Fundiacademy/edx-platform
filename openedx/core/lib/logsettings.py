"""Get log settings."""

import logging
import os
import platform
import sys
import warnings
from logging.handlers import SysLogHandler

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


def get_logger_config(log_dir,
                      logging_env="no_env",
                      syslog_addr=None,
                      local_loglevel='INFO',
                      console_loglevel=None,
                      service_variant=""):

    """

    Return the appropriate logging config dictionary. You should assign the
    result of this to the LOGGING var in your settings. The reason it's done
    this way instead of registering directly is because I didn't want to worry
    about resetting the logging state if this is called multiple times when
    settings are extended.
    """

    # Revert to INFO if an invalid string is passed in
    if local_loglevel not in LOG_LEVELS:
        local_loglevel = 'INFO'

    if console_loglevel is None or console_loglevel not in LOG_LEVELS:
        console_loglevel = 'INFO'

    hostname = platform.node().split(".")[0]
    syslog_format = ("[service_variant={service_variant}]"
                     "[%(name)s][env:{logging_env}] %(levelname)s "
                     "[{hostname}  %(process)d] [%(filename)s:%(lineno)d] "
                     "- %(message)s").format(service_variant=service_variant,
                                             logging_env=logging_env,
                                             hostname=hostname)

    handlers = ['console', 'local']
    if syslog_addr:
        handlers.append('syslogger-remote')

    logger_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s %(levelname)s %(process)d '
                          '[%(name)s] %(filename)s:%(lineno)d - %(message)s',
            },
            'syslog_format': {'format': syslog_format},
            'raw': {'format': '%(message)s'},
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            }
        },
        'handlers': {
            'console': {
                'level': console_loglevel,
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'stream': sys.stderr,
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
        },
        'loggers': {
            'tracking': {
                'handlers': ['tracking'],
                'level': 'DEBUG',
                'propagate': False,
            },
            '': {
                'handlers': handlers,
                'level': 'DEBUG',
                'propagate': False
            },
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    }
    if syslog_addr:
        logger_config['handlers'].update({
            'syslogger-remote': {
                'level': 'INFO',
                'class': 'logging.handlers.SysLogHandler',
                'address': syslog_addr,
                'formatter': 'syslog_format',
            },
        })

    # for production environments we will only
    # log INFO and up
    logger_config['loggers']['']['level'] = 'INFO'
    # requests is so loud at INFO (logs every connection) that we force it to warn in production environments
    logger_config['loggers']['requests.packages.urllib3'] = {'level': 'WARN'}
    logger_config['handlers'].update({
        'local': {
            'level': local_loglevel,
            'class': 'logging.handlers.SysLogHandler',
            'address': '/dev/log',
            'formatter': 'syslog_format',
            'facility': SysLogHandler.LOG_LOCAL0,
        },
        'tracking': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'address': '/dev/log',
            'facility': SysLogHandler.LOG_LOCAL1,
            'formatter': 'raw',
        },
    })

    return logger_config


def log_python_warnings():
    """
    Stop ignoring DeprecationWarning, ImportWarning, and PendingDeprecationWarning;
    log all Python warnings to the main log file.

    Not used in test runs, so pytest can collect the warnings triggered for
    each test case.
    """
    warnings.simplefilter('default')
    logging.captureWarnings(True)
