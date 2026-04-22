from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('Unskilled', 'Unskilled'),
        ('Skilled', 'Skilled'),
        ('Buyer', 'Buyer'),
    )
    
    VERIFICATION_CHOICES = (
        ('Unverified', 'Unverified'),
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Unskilled')
    nid_tin_number = models.CharField(max_length=50, blank=True, null=True)
    is_identity_verified = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.9) # Mock default for search

    
    id_document = models.FileField(upload_to='identity_docs/', blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='Unverified')
    
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # Unique User ID — format: SC-YYYYMM-XXXXX
    user_uid = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

class SkillCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class SkillBadge(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='skill_badges')
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category')

    @property
    def badge_label(self):
        return f"Skilled at {self.category.name}"

    def __str__(self):
        return f"{self.user.username} - Skilled at {self.category.name} (Lvl {self.level})"

class AssessmentQuestion(models.Model):
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    
    CORRECT_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    correct_option = models.CharField(max_length=1, choices=CORRECT_CHOICES)

class JobPost(models.Model):
    INTERACTION_CHOICES = [
        ('Paid Service', 'Paid Service'),
        ('Skill Barter', 'Skill Barter'),
    ]
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(SkillCategory, on_delete=models.SET_NULL, null=True)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_CHOICES)
    budget_or_terms = models.CharField(max_length=255) # e.g. "$500" or "I will design your logo if you build my website"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"

class JobProposal(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='proposals')
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submitted_proposals')
    cover_letter = models.TextField()
    cv_file = models.FileField(upload_to='cvs/', blank=True, null=True)
    proposed_terms = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"Proposal by {self.applicant.username} for {self.job.title}"

class ServiceAgreement(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('In Dispute', 'In Dispute'),
        ('Completed', 'Completed'),
    ]
    
    proposal = models.OneToOneField(JobProposal, on_delete=models.CASCADE, related_name='agreement')
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='client_agreements')
    provider = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='provider_agreements')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Agreement: {self.client.username} & {self.provider.username}"

class Milestone(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('In Review', 'In Review'),
        ('Completed', 'Completed'),
    ]
    
    agreement = models.ForeignKey(ServiceAgreement, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return self.title

class EncryptedMessage(models.Model):
    agreement = models.ForeignKey(ServiceAgreement, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    encrypted_content = models.TextField() # Base64 encoded encrypted string
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg from {self.sender.username} at {self.timestamp}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
        ('Escrow Hold', 'Escrow Hold'),
        ('Earnings', 'Earnings'),
        ('Service Fee', 'Service Fee'),
    ]
    
    PAYMENT_METHODS = [
        ('bKash', 'bKash'),
        ('SSLCommerz', 'SSLCommerz'),
        ('Internal Wallet', 'Internal Wallet'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reference_id = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} by {self.user.username}"

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
