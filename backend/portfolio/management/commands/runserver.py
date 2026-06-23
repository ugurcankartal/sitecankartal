from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import (
    Command as StaticfilesRunserverCommand,
)


class Command(StaticfilesRunserverCommand):
    def handle(self, *args, **options):
        if not options.get('addrport'):
            options['addrport'] = f'{settings.BIND_HOST}:{settings.DEV_PORT}'
        super().handle(*args, **options)
