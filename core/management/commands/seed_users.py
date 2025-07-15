from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import User

class Command(BaseCommand):
    help = 'Seeds the database with default users'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding default users...')
        
        # Define default users
        default_users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'manager1',
                'password': 'manager123',
                'role': 'case_manager',
                'is_staff': True,
                'is_superuser': False,
            },
            {
                'username': 'officer1',
                'password': 'officer123',
                'role': 'field_officer',
                'is_staff': False,
                'is_superuser': False,
            },
        ]
        
        # Create users
        with transaction.atomic():
            for user_data in default_users:
                username = user_data.pop('username')
                password = user_data.pop('password')
                
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.WARNING(f'User {username} already exists, skipping...'))
                    continue
                
                # Create user
                user = User.objects.create_user(username=username, **user_data)
                user.set_password(password)
                user.save()
                
                self.stdout.write(self.style.SUCCESS(f'Successfully created user: {username} with role: {user.get_role_display()}'))
        
        self.stdout.write(self.style.SUCCESS('Default users seeded successfully!'))