from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.users.models import User
from apps.departments.models import Department
from apps.doctors.models import Doctor
from apps.patients.models import Patient
from apps.specializations.models import Specialization
from faker import Faker
import random

fake = Faker()


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding Clinic Management database...')

        # Create admin
        if not User.objects.filter(email='admin@clinic.com').exists():
            User.objects.create_superuser(
                email='admin@clinic.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )

        # Create departments
        departments = ['Cardiology', 'Neurology', 'Pediatrics', 'Orthopedics', 'Dermatology', 'General Medicine']
        for dept in departments:
            Department.objects.get_or_create(name=dept)

        # Create specializations
        specs = ['Heart Specialist', 'Brain Specialist', 'Bone Specialist', 'Skin Specialist', 'Child Specialist']
        for spec in specs:
            Specialization.objects.get_or_create(name=spec)

        # Create doctors
        departments = Department.objects.all()
        specs = Specialization.objects.all()

        for i in range(10):
            Doctor.objects.get_or_create(
                license_number=f'DR{i+1}000',
                defaults={
                    'user': None,
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'specialization': random.choice(specs),
                    'department': random.choice(departments),
                    'phone': fake.phone_number(),
                    'years_experience': random.randint(1, 20),
                    'is_available': True
                }
            )

        # Create patients
        for i in range(10):
            email = f'patient{i+1}@example.com'
            if not Patient.objects.filter(email=email).exists():
                Patient.objects.create(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=email,
                    phone=fake.phone_number(),
                    date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
                    address=fake.address()
                )

        self.stdout.write(self.style.SUCCESS('Successfully seeded Clinic database!'))