from .test import *

NOSE_ARGS = [
    '--cover-package=accounts',
    '--cover-package=core',
    '--cover-package=dashboard',
    '--cover-package=projects',
    '--cover-package=services',
    '--logging-level=CRITICAL',
    '--logging-clear-handlers',
    '-s'
]
