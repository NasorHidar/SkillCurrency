from django import forms
from .models import IdentityDocument

class IdentityUploadForm(forms.ModelForm):
    class Meta:
        model = IdentityDocument
        fields = ['id_type', 'full_name', 'id_number', 'date_of_birth', 'front_side', 'back_side']