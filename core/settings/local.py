from .base import *

# speed up dev appserver code change detection by ignoring a bunch of dirs
DJANGAE_RUNSERVER_IGNORED_DIR_REGEXES += ['^sitepackages$', '^tests$']
