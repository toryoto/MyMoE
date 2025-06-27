from django.core.management.base import BaseCommand
from departments.models import Department, DTE

class Command(BaseCommand):
    help = 'Populates initial Department and DTE data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating organizational data...'))

        # Create Departments
        tech_dept, created = Department.objects.get_or_create(name='Technology', code='TECH', defaults={'description': 'Technology Department'})
        if created: self.stdout.write(self.style.SUCCESS(f'Created Department: {tech_dept.name}'))

        sc_dept, created = Department.objects.get_or_create(name='S&C', code='SC', defaults={'description': 'Strategy & Consulting Department'})
        if created: self.stdout.write(self.style.SUCCESS(f'Created Department: {sc_dept.name}'))

        hr_dept, created = Department.objects.get_or_create(name='HR', code='HR', defaults={'description': 'Human Resources Department'})
        if created: self.stdout.write(self.style.SUCCESS(f'Created Department: {hr_dept.name}'))

        # Create DTEs for Technology
        dtes_tech = [
            {'name': 'Quality Engineering & Assurance', 'code': 'QEA', 'department': tech_dept},
            {'name': 'Application Services - Financial Services', 'code': 'AS-FS', 'department': tech_dept},
            {'name': 'Health & Public Service', 'code': 'H&PS', 'department': tech_dept},
            {'name': 'Intelligent Cloud & Engineering', 'code': 'ICE', 'department': tech_dept},
        ]
        for dte_data in dtes_tech:
            dte, created = DTE.objects.get_or_create(code=dte_data['code'], department=dte_data['department'], defaults={'name': dte_data['name']})
            if created: self.stdout.write(self.style.SUCCESS(f'Created DTE: {dte.name} ({dte.department.code})'))

        # Create DTEs for S&C
        dtes_sc = [
            {'name': 'Strategy', 'code': 'Strategy', 'department': sc_dept},
            {'name': 'Data & AI', 'code': 'Data & AI', 'department': sc_dept},
            {'name': 'Industry Consulting', 'code': 'Industry Consulting', 'department': sc_dept},
        ]
        for dte_data in dtes_sc:
            dte, created = DTE.objects.get_or_create(code=dte_data['code'], department=dte_data['department'], defaults={'name': dte_data['name']})
            if created: self.stdout.write(self.style.SUCCESS(f'Created DTE: {dte.name} ({dte.department.code})'))

        # Create DTEs for HR
        dtes_hr = [
            {'name': 'People Operations', 'code': 'People Operations', 'department': hr_dept},
        ]
        for dte_data in dtes_hr:
            dte, created = DTE.objects.get_or_create(code=dte_data['code'], department=dte_data['department'], defaults={'name': dte_data['name']})
            if created: self.stdout.write(self.style.SUCCESS(f'Created DTE: {dte.name} ({dte.department.code})'))

        self.stdout.write(self.style.SUCCESS('Organizational data population complete.'))
