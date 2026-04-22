from django.core.management.base import BaseCommand
from accounts.models import SkillCategory, AssessmentQuestion

class Command(BaseCommand):
    help = 'Seeds the database with initial Skill Categories and Assessment Questions'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Category 1: Web Development
        web_dev, created = SkillCategory.objects.get_or_create(
            name='Web Development',
            defaults={'description': 'Test your knowledge on HTML, CSS, JavaScript, and backend frameworks.'}
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Created Web Development category.'))
            questions = [
                {
                    'question_text': 'What does HTML stand for?',
                    'option_a': 'Hyper Text Markup Language',
                    'option_b': 'High Tech Machine Learning',
                    'option_c': 'Hyperlink and Text Markup Language',
                    'option_d': 'Home Tool Markup Language',
                    'correct_option': 'A'
                },
                {
                    'question_text': 'Which property is used to change the background color in CSS?',
                    'option_a': 'color',
                    'option_b': 'background-color',
                    'option_c': 'bgcolor',
                    'option_d': 'background-style',
                    'correct_option': 'B'
                },
                {
                    'question_text': 'Inside which HTML element do we put the JavaScript?',
                    'option_a': '<javascript>',
                    'option_b': '<scripting>',
                    'option_c': '<js>',
                    'option_d': '<script>',
                    'correct_option': 'D'
                },
                {
                    'question_text': 'How do you create a function in JavaScript?',
                    'option_a': 'function:myFunction()',
                    'option_b': 'function = myFunction()',
                    'option_c': 'function myFunction()',
                    'option_d': 'create myFunction()',
                    'correct_option': 'C'
                },
                {
                    'question_text': 'Which of the following is a Python web framework?',
                    'option_a': 'Laravel',
                    'option_b': 'Spring Boot',
                    'option_c': 'Django',
                    'option_d': 'Ruby on Rails',
                    'correct_option': 'C'
                }
            ]
            for q_data in questions:
                AssessmentQuestion.objects.create(category=web_dev, **q_data)

        # Category 2: Graphic Design
        design, created = SkillCategory.objects.get_or_create(
            name='Graphic Design',
            defaults={'description': 'Assess your understanding of design principles, typography, and color theory.'}
        )

        if created:
            self.stdout.write(self.style.SUCCESS('Created Graphic Design category.'))
            questions = [
                {
                    'question_text': 'What does RGB stand for?',
                    'option_a': 'Red, Green, Blue',
                    'option_b': 'Red, Gray, Black',
                    'option_c': 'Red, Green, Black',
                    'option_d': 'Royal, Green, Basic',
                    'correct_option': 'A'
                },
                {
                    'question_text': 'Which file format is best for preserving transparency?',
                    'option_a': 'JPEG',
                    'option_b': 'PNG',
                    'option_c': 'BMP',
                    'option_d': 'PDF',
                    'correct_option': 'B'
                },
                {
                    'question_text': 'Kerning refers to:',
                    'option_a': 'The space between lines of text',
                    'option_b': 'The overall tracking of a word',
                    'option_c': 'The space between two individual characters',
                    'option_d': 'The font weight',
                    'correct_option': 'C'
                },
                {
                    'question_text': 'Which Adobe software is primarily vector-based?',
                    'option_a': 'Photoshop',
                    'option_b': 'Illustrator',
                    'option_c': 'Premiere Pro',
                    'option_d': 'Lightroom',
                    'correct_option': 'B'
                },
                {
                    'question_text': 'What is the standard resolution for web images?',
                    'option_a': '300 ppi',
                    'option_b': '72 ppi',
                    'option_c': '150 ppi',
                    'option_d': '600 ppi',
                    'correct_option': 'B'
                }
            ]
            for q_data in questions:
                AssessmentQuestion.objects.create(category=design, **q_data)

        # Category 3: Advanced Python Structures
        py_adv, created = SkillCategory.objects.get_or_create(
            name='Advanced Python Structures',
            defaults={'description': 'Evaluate your mastery of advanced Python concepts, decorators, threading, and memory management.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Advanced Python Structures category.'))

        # Category 4: UI/UX Principles
        uiux, created = SkillCategory.objects.get_or_create(
            name='UI/UX Principles',
            defaults={'description': 'Test your understanding of user experience design, accessibility, and wireframing.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created UI/UX Principles category.'))

        # Category 5: Project Management (Agile)
        agile, created = SkillCategory.objects.get_or_create(
            name='Project Management (Agile)',
            defaults={'description': 'Assess your knowledge of Scrum frameworks, sprints, and agile methodology.'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created Project Management (Agile) category.'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded database with skills and questions!'))
