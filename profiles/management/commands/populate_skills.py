from django.core.management.base import BaseCommand
from profiles.models import Skill

class Command(BaseCommand):
    help = 'Populate Skill master data'

    def handle(self, *args, **options):
        skills = [
            'Python',
            'Java',
            'Business English',
            'Project Management',
            '基本情報技術者試験',
        ]

        for skill_name in skills:
            Skill.objects.get_or_create(name=skill_name)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated skills'))
