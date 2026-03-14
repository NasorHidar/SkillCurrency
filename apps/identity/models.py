from django.db import models
from django.contrib.auth.models import User

class IdentityDocument(models.Model):
    ID_CHOICES = (('NID', 'National ID'), ('TIN', 'Tax ID (TIN)'))
    STATUS_CHOICES = (('PENDING', 'Pending AI Check'), ('VERIFIED', 'Verified'))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_type = models.CharField(max_length=3, choices=ID_CHOICES, default='NID')
    full_name = models.CharField(max_length=255)
    id_number = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    front_side = models.ImageField(upload_to='nids/front/')
    back_side = models.ImageField(upload_to='nids/back/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')