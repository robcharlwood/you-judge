import os

from djangae.environment import is_production_environment

# production settings
SETTINGS_MAPPING = {
    'you-judge-app': 'prod',
}

APPLICATION_ID = os.getenv('APPLICATION_ID', 'localhost')
APPLICATION_NAME = APPLICATION_ID.replace('g~', '')


def get_settings_name(env_name='local'):
    if is_production_environment():
        env_name = SETTINGS_MAPPING[APPLICATION_NAME]
    return 'core.settings.' + env_name
