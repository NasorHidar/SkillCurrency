from django.urls import path
from . import views

urlpatterns = [
    path('vault/', views.identity_vault, name='identity_vault'),
    path('vault/success/', views.vault_success, name='vault_success'), # Added
    path('vault/deny/', views.vault_deny, name='vault_deny'),          # Added
]