"""
Management command: python manage.py seed_users

Creates 3 verified skilled users with skill badges, wallet balance,
and mock profile data for testing purposes.
"""
import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import SkillCategory, SkillBadge

User = get_user_model()

SEED_USERS = [
    {
        "username": "arafat_dev",
        "password": "Test@12345",
        "first_name": "Arafat",
        "last_name": "Hossain",
        "email": "arafat@skillcurrency.test",
        "bio": "Full-stack developer with 5 years of experience in Django and React. Passionate about building scalable web apps.",
        "role": "Skilled",
        "wallet_balance": 1250.00,
        "skills": ["Web Development", "Python Programming"],
    },
    {
        "username": "nusrat_design",
        "password": "Test@12345",
        "first_name": "Nusrat",
        "last_name": "Jahan",
        "email": "nusrat@skillcurrency.test",
        "bio": "Creative UI/UX designer specialising in Figma, branding, and motion graphics. 50+ projects delivered.",
        "role": "Skilled",
        "wallet_balance": 850.50,
        "skills": ["Graphic Design", "Video Editing"],
    },
    {
        "username": "rakib_ml",
        "password": "Test@12345",
        "first_name": "Rakib",
        "last_name": "Islam",
        "email": "rakib@skillcurrency.test",
        "bio": "Machine learning engineer and data analyst. Expert in Python, TensorFlow, and SQL.",
        "role": "Skilled",
        "wallet_balance": 2100.75,
        "skills": ["Data Science", "Python Programming"],
    },
]


class Command(BaseCommand):
    help = "Seeds 3 verified Skilled users with badges and wallet balances."

    def _make_uid(self, username):
        from django.utils import timezone
        prefix = "SC"
        date_part = timezone.now().strftime("%Y%m")
        return f"{prefix}-{date_part}-{username[:5].upper()}"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\nSeeding verified users...\n"))

        for data in SEED_USERS:
            if User.objects.filter(username=data["username"]).exists():
                self.stdout.write(self.style.WARNING(f"  [!]  {data['username']} already exists — skipping."))
                continue

            user = User.objects.create_user(
                username=data["username"],
                password=data["password"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                bio=data["bio"],
                role=data["role"],
                wallet_balance=data["wallet_balance"],
                is_identity_verified=True,
                verification_status="Approved",
                nid_tin_number=str(uuid.uuid4().int)[:14],
                user_uid=self._make_uid(data["username"]),
            )

            # Assign skill badges
            for skill_name in data["skills"]:
                category, _ = SkillCategory.objects.get_or_create(
                    name=skill_name,
                    defaults={"description": f"Skills related to {skill_name}"},
                )
                SkillBadge.objects.get_or_create(
                    user=user,
                    category=category,
                    defaults={"level": 3},
                )

            self.stdout.write(self.style.SUCCESS(
                f"  [+]  Created: {user.first_name} {user.last_name} (@{user.username})"
                f" | Wallet: ${user.wallet_balance}"
                f" | Badges: {', '.join(data['skills'])}"
            ))

        self.stdout.write(self.style.SUCCESS("\nSeeding complete!\n"))
        self.stdout.write("   Login credentials for all seed users: password = Test@12345\n")
