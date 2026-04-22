from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import SkillCategory, JobPost

User = get_user_model()

JOBS_DATA = [
    # --- Web Development ---
    {
        'category': 'Web Development',
        'title': 'Build a Django REST API for an E-Commerce Platform',
        'description': (
            'We need an experienced backend developer to design and implement a fully functional '
            'REST API using Django REST Framework. The API should handle product listings, cart '
            'management, user authentication (JWT), and order processing. PostgreSQL is the '
            'preferred database. Proper documentation with Swagger/OpenAPI is required.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$400 – $600',
    },
    {
        'category': 'Web Development',
        'title': 'React Dashboard UI for Analytics SaaS',
        'description': (
            'Looking for a React developer to build an interactive analytics dashboard. '
            'The UI should include dynamic charts (using Recharts or Chart.js), a data table '
            'with pagination and export, and a responsive layout. Figma mockups will be provided. '
            'Must integrate with a provided REST API.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$300 – $500',
    },
    {
        'category': 'Web Development',
        'title': 'Fix Critical Bugs on WordPress WooCommerce Store',
        'description': (
            'Our WooCommerce store has several critical issues: checkout is failing for guest '
            'users, product images are not loading on mobile, and the shipping calculator shows '
            'incorrect rates. We need someone who can diagnose and fix these within 48 hours. '
            'Site access will be provided under NDA.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$80 – $150',
    },
    {
        'category': 'Web Development',
        'title': 'Portfolio Website in Exchange for SEO Audit',
        'description': (
            'I am a web developer who can build you a stunning personal portfolio website using '
            'HTML/CSS/JS with smooth animations and mobile responsiveness. In exchange, I am looking '
            'for someone who can perform a comprehensive SEO audit on my existing blog, including '
            'keyword analysis, backlink review, and technical SEO recommendations.'
        ),
        'interaction_type': 'Skill Barter',
        'budget_or_terms': 'Portfolio site (5 pages) ↔ Full SEO Audit Report',
    },
    # --- Graphic Design ---
    {
        'category': 'Graphic Design',
        'title': 'Brand Identity Package for a FinTech Startup',
        'description': (
            'We are a newly funded FinTech startup seeking a talented designer to create a complete '
            'brand identity. Deliverables include: logo (primary + variants), color palette, '
            'typography guide, business card design, and a basic brand style guide (PDF). '
            'We prefer a modern, trustworthy, and minimal aesthetic.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$250 – $400',
    },
    {
        'category': 'Graphic Design',
        'title': 'Social Media Content Pack – 30 Posts',
        'description': (
            'Looking for a creative designer to produce 30 unique social media post templates '
            'for Instagram and LinkedIn. Each template should be editable in Canva or Adobe '
            'Illustrator. The brand is an online education platform – clean, colorful, and '
            'professional. Delivery required within 7 days.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$120 – $200',
    },
    {
        'category': 'Graphic Design',
        'title': 'Logo Design for Illustration Work',
        'description': (
            'I am a graphic designer who will craft a professional logo for your business. '
            'In return, I need hand-drawn illustrations (5 custom pieces) for my portfolio project. '
            'This is a great opportunity for illustrators looking to add branding collaboration '
            'to their resume.'
        ),
        'interaction_type': 'Skill Barter',
        'budget_or_terms': 'Full Logo Package ↔ 5 Custom Illustrations',
    },
    # --- UI/UX Principles ---
    {
        'category': 'UI/UX Principles',
        'title': 'UX Research & Usability Testing for Mobile App',
        'description': (
            'We have a beta version of our healthcare mobile app and need a UX researcher to '
            'conduct usability testing with 5–8 participants, analyze results, and produce a '
            'detailed report with actionable recommendations. Experience with tools like Maze, '
            'UserTesting, or similar is a plus.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$180 – $300',
    },
    {
        'category': 'UI/UX Principles',
        'title': 'Figma Prototype for a Travel Booking App',
        'description': (
            'Create a high-fidelity interactive Figma prototype for a travel booking mobile '
            'application. The prototype should cover: home screen, search results, hotel/flight '
            'detail page, booking flow, and confirmation screen. Must include component library '
            'and auto-layout. Deadline: 10 days.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$200 – $350',
    },
    {
        'category': 'UI/UX Principles',
        'title': 'UX Audit in Exchange for Copywriting',
        'description': (
            'I am a UX designer offering a full UX audit of your product – including heuristic '
            'evaluation, user flow analysis, and a prioritized list of improvements. In exchange, '
            'I need a skilled copywriter to write compelling landing page copy for my design '
            'studio website (approximately 800 words).'
        ),
        'interaction_type': 'Skill Barter',
        'budget_or_terms': 'Full UX Audit ↔ Landing Page Copywriting',
    },
    # --- Advanced Python Structures ---
    {
        'category': 'Advanced Python Structures',
        'title': 'Build a Data Pipeline with Python & Apache Airflow',
        'description': (
            'We need an experienced Python developer to build an ETL (Extract, Transform, Load) '
            'data pipeline using Apache Airflow. The pipeline should pull data from multiple '
            'REST APIs, transform it using Pandas, and load it into a PostgreSQL warehouse. '
            'Scheduling, error handling, and alerting are required.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$500 – $800',
    },
    {
        'category': 'Advanced Python Structures',
        'title': 'Scrape & Aggregate Product Data from 5 E-Commerce Sites',
        'description': (
            'We need a Python developer to build robust web scrapers for 5 specified e-commerce '
            'websites using Scrapy or BeautifulSoup+Selenium. The scrapers should extract product '
            'name, price, SKU, rating, and availability. Data should be stored in a structured '
            'CSV and SQLite database. Anti-bot bypass techniques may be required.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$200 – $350',
    },
    {
        'category': 'Advanced Python Structures',
        'title': 'Python Automation Script for Office Workflow',
        'description': (
            'Need a Python script to automate our monthly report generation. The script should '
            'read data from multiple Excel files, calculate KPIs, generate a formatted PDF report '
            'using ReportLab, and email it to a distribution list using SMTP. Must include '
            'comprehensive logging and error handling.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$100 – $180',
    },
    {
        'category': 'Advanced Python Structures',
        'title': 'Python ML Model Integration for Web App',
        'description': (
            'We have a trained scikit-learn classification model (.pkl) and need a Python/Flask '
            'developer to wrap it in a REST API, deploy it on a VPS (Ubuntu), and integrate the '
            'prediction endpoint into our existing React frontend. Docker deployment preferred. '
            'Must handle batch predictions and return confidence scores.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$300 – $450',
    },
    {
        'category': 'Advanced Python Structures',
        'title': 'Python Dev Help in Exchange for English Tutoring',
        'description': (
            'I am a senior Python developer offering to build a command-line tool or automation '
            'script of your choice (up to 200 lines of clean, documented code). In return, '
            'I need 5 sessions (1 hour each) of conversational English tutoring focused on '
            'business communication and presentation skills.'
        ),
        'interaction_type': 'Skill Barter',
        'budget_or_terms': 'Custom Python CLI Tool ↔ 5 × 1hr English Tutoring Sessions',
    },
    # --- Project Management (Agile) ---
    {
        'category': 'Project Management (Agile)',
        'title': 'Scrum Master for 3-Month Software Project',
        'description': (
            'We are a 6-person remote software team seeking an experienced Scrum Master for a '
            '3-month engagement. Responsibilities include facilitating daily stand-ups, sprint '
            'planning, retrospectives, and backlog grooming. Experience with Jira and remote team '
            'management is essential. PSM I or CSM certification preferred.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$1,200 / month',
    },
    {
        'category': 'Project Management (Agile)',
        'title': 'Agile Transformation Consultant for Mid-Size Company',
        'description': (
            'We are transitioning our 40-person engineering department from Waterfall to Agile/Scrum. '
            'Looking for an experienced Agile coach to assess current workflows, design a transition '
            'roadmap, conduct training workshops, and provide 2 months of mentorship. Must have '
            'documented case studies of similar transformations.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$2,500 – $4,000 total',
    },
    {
        'category': 'Project Management (Agile)',
        'title': 'Agile Project Plan for Startup MVP',
        'description': (
            'Need an Agile project manager to help structure our startup\'s 6-month MVP roadmap. '
            'Deliverables: user story backlog (50+ stories), sprint breakdown (2-week sprints), '
            'velocity estimates, risk register, and a Jira board setup. One-time engagement '
            'with a 2-hour Q&A follow-up.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$300 – $500',
    },
    {
        'category': 'Project Management (Agile)',
        'title': 'Project Manager Skills for Graphic Design Mentorship',
        'description': (
            'I am a certified PMP and SAFe Agilist offering to create a complete project plan, '
            'risk register, and sprint schedule for your startup or personal project. In exchange, '
            'I am seeking 4 sessions of graphic design mentorship to improve my Figma and visual '
            'design skills.'
        ),
        'interaction_type': 'Skill Barter',
        'budget_or_terms': 'Full Project Plan & Sprint Schedule ↔ 4 × Design Mentorship Sessions',
    },
    {
        'category': 'Project Management (Agile)',
        'title': 'Technical Writer for Agile Documentation',
        'description': (
            'Looking for a technical writer with experience in Agile environments to document '
            'our team\'s engineering processes. Deliverables include a sprint runbook, definition '
            'of done checklist, onboarding guide for new developers, and API documentation '
            'templates. Must be familiar with Confluence or Notion.'
        ),
        'interaction_type': 'Paid Service',
        'budget_or_terms': '$150 – $250',
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with 20 diverse, realistic job posts across all skill categories.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('Starting job seeding...'))

        # We need a "system" user to be the author of seeded jobs.
        # We'll use the first superuser, or create a dedicated seed user.
        author = User.objects.filter(is_superuser=True).first()
        if not author:
            self.stdout.write(self.style.WARNING(
                'No superuser found. Creating a seed author account: seed_admin / seed_pass_123'
            ))
            author = User.objects.create_user(
                username='seed_admin',
                password='seed_pass_123',
                email='seed@skillcurrency.dev',
                role='Buyer',
                is_staff=True,
            )
            self.stdout.write(self.style.SUCCESS(f'Created seed user: {author.username}'))

        created_count = 0
        skipped_count = 0

        for job_data in JOBS_DATA:
            category_name = job_data.pop('category')
            try:
                category = SkillCategory.objects.get(name=category_name)
            except SkillCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'  [SKIP] Category "{category_name}" not found. Run seed_skills first.'
                ))
                job_data['category'] = category_name  # restore for safety
                skipped_count += 1
                continue

            # Avoid duplicates by checking title
            if JobPost.objects.filter(title=job_data['title']).exists():
                self.stdout.write(f'  [EXISTS] "{job_data["title"]}" already seeded.')
                job_data['category'] = category_name
                skipped_count += 1
                continue

            JobPost.objects.create(
                author=author,
                category=category,
                status='Open',
                **job_data
            )
            self.stdout.write(self.style.SUCCESS(f'  [CREATE] "{job_data["title"]}"'))
            created_count += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! {created_count} jobs created, {skipped_count} skipped.'
        ))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(
                'Tip: Run `python manage.py seed_skills` first to ensure all categories exist.'
            ))
