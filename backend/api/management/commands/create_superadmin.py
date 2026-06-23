import os

from django.core.management.base import BaseCommand, CommandError

from api.models import PortfolioUser


class Command(BaseCommand):
    help = 'Create or update the portfolio super admin user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default=os.environ.get('SUPERADMIN_USERNAME', 'superadmin'),
            help='Super admin username (default: superadmin)',
        )
        parser.add_argument(
            '--password',
            default=os.environ.get('SUPERADMIN_PASSWORD'),
            help='Super admin password (or set SUPERADMIN_PASSWORD in .env)',
        )
        parser.add_argument(
            '--email',
            default=os.environ.get('SUPERADMIN_EMAIL', 'ugurcankartal9@gmail.com'),
            help='Super admin email',
        )
        parser.add_argument(
            '--full-name',
            default=os.environ.get('SUPERADMIN_FULL_NAME', 'Can Kartal'),
            help='Super admin full name',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update password and profile if the user already exists',
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        full_name = options['full_name']
        force = options['force']

        if not password:
            raise CommandError(
                'Password is required. Pass --password or set SUPERADMIN_PASSWORD in .env'
            )

        if len(password) < 8:
            raise CommandError('Password must be at least 8 characters long')

        user = PortfolioUser.objects.filter(username=username).first()

        if user and not force:
            raise CommandError(
                f'User "{username}" already exists. Use --force to update the password.'
            )

        if user:
            user.set_password(password)
            user.email = email
            user.full_name = full_name
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Super admin "{username}" updated.'))
            return

        user = PortfolioUser(
            username=username,
            email=email,
            full_name=full_name,
            bio='Portfolio super administrator',
            location='İzmir, Türkiye',
        )
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS(f'Super admin "{username}" created.'))
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Email: {email}')
        self.stdout.write('  Login at: /admin')
