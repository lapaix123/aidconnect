from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from core.models import BeneficiaryCategory, Program, Beneficiary
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Seeds the database with dummy data including categories, programs, and beneficiaries'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding dummy data...')
        
        # Create categories
        categories = [
            {
                'name': 'Category 1',
                'description': 'First category of beneficiaries',
                'max_annual_amount': 500000.00,
            },
            {
                'name': 'Category 2',
                'description': 'Second category of beneficiaries',
                'max_annual_amount': 750000.00,
            },
            {
                'name': 'Category 3',
                'description': 'Third category of beneficiaries',
                'max_annual_amount': 1000000.00,
            },
        ]
        
        # Create programs
        programs = [
            {
                'name': 'Girinka',
                'description': 'One Cow per Poor Family Program',
                'monthly_amount': 50000.00,
            },
            {
                'name': 'VUP',
                'description': 'Vision 2020 Umurenge Program',
                'monthly_amount': 30000.00,
            },
            {
                'name': 'Twiyubake',
                'description': 'Self-reliance and economic empowerment program',
                'monthly_amount': 40000.00,
            },
        ]
        
        # Create beneficiaries
        first_names = ['John', 'Mary', 'James', 'Sarah', 'Michael', 'Emma', 'David', 'Olivia', 'Robert', 'Sophia']
        last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor']
        genders = ['male', 'female']
        addresses = [
            'Kigali, Rwanda', 
            'Musanze, Rwanda', 
            'Rubavu, Rwanda', 
            'Huye, Rwanda', 
            'Muhanga, Rwanda',
            'Nyagatare, Rwanda',
            'Rusizi, Rwanda',
            'Karongi, Rwanda',
            'Rwamagana, Rwanda',
            'Nyanza, Rwanda'
        ]
        
        # Number of beneficiaries to create (random between 20 and 30)
        num_beneficiaries = random.randint(20, 30)
        
        with transaction.atomic():
            # Create categories
            created_categories = []
            for category_data in categories:
                name = category_data['name']
                
                # Check if category already exists
                if BeneficiaryCategory.objects.filter(name=name).exists():
                    self.stdout.write(self.style.WARNING(f'Category {name} already exists, skipping...'))
                    created_categories.append(BeneficiaryCategory.objects.get(name=name))
                    continue
                
                # Create category
                category = BeneficiaryCategory.objects.create(**category_data)
                created_categories.append(category)
                self.stdout.write(self.style.SUCCESS(f'Successfully created category: {name}'))
            
            # Create programs
            created_programs = []
            for program_data in programs:
                name = program_data['name']
                
                # Check if program already exists
                if Program.objects.filter(name=name).exists():
                    self.stdout.write(self.style.WARNING(f'Program {name} already exists, skipping...'))
                    created_programs.append(Program.objects.get(name=name))
                    continue
                
                # Create program
                program = Program.objects.create(**program_data)
                created_programs.append(program)
                self.stdout.write(self.style.SUCCESS(f'Successfully created program: {name}'))
            
            # Create beneficiaries
            for i in range(num_beneficiaries):
                # Generate random data for beneficiary
                name = f"{random.choice(first_names)} {random.choice(last_names)}"
                # Random date of birth between 18 and 70 years ago
                days_old = random.randint(18*365, 70*365)
                dob = (timezone.now() - timedelta(days=days_old)).date()
                gender = random.choice(genders)
                address = random.choice(addresses)
                category = random.choice(created_categories)
                program = random.choice(created_programs)
                
                # Create beneficiary
                beneficiary = Beneficiary.objects.create(
                    name=name,
                    dob=dob,
                    gender=gender,
                    address=address,
                    category=category,
                    program=program
                )
                
                self.stdout.write(self.style.SUCCESS(f'Successfully created beneficiary: {name} in {program.name} program'))
            
        self.stdout.write(self.style.SUCCESS(f'Dummy data seeded successfully! Created {num_beneficiaries} beneficiaries.'))