from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from djangae.contrib.consistency.signals import connect_signals
        connect_signals()
