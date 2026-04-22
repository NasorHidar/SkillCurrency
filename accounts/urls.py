from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('signup/', views.sign_up, name='signup'),
    path('signin/', views.sign_in, name='signin'),
    path('logout/', views.log_out, name='logout'),
    path('identity-vault/', views.identity_vault, name='identity_vault'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
    path('users/search/', views.search_users, name='search_users'),
    path('skill-lab/', views.skill_lab_dashboard, name='skill_lab_dashboard'),
    path('skill-lab/take/<int:category_id>/', views.take_assessment, name='take_assessment'),
    path('skill-lab/grade/<int:category_id>/', views.grade_assessment, name='grade_assessment'),
    path('skill-lab/results/', views.assessment_results, name='assessment_results'),
    path('skill-lab/mint/', views.mint_skillcurrency, name='mint_skillcurrency'),
    
    # Marketplace URLs
    path('marketplace/', views.marketplace_feed, name='marketplace_feed'),
    path('marketplace/create/', views.create_job, name='create_job'),
    path('marketplace/job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('marketplace/job/<int:job_id>/propose/', views.submit_proposal, name='submit_proposal'),
    path('marketplace/proposal/<int:proposal_id>/accept/', views.accept_proposal, name='accept_proposal'),
    path('marketplace/job/<int:job_id>/bulk-accept/', views.bulk_accept_proposals, name='bulk_accept_proposals'),
    path('marketplace/activity/', views.my_activity, name='my_activity'),
    
    # Workspace URLs
    path('workspace/<int:agreement_id>/', views.workspace, name='workspace'),
    path('workspace/milestone/<int:milestone_id>/update/', views.update_milestone, name='update_milestone'),
    
    # Financial Hub URLs
    path('financial-hub/', views.financial_hub, name='financial_hub'),
    path('financial-hub/top-up/', views.top_up_wallet, name='top_up_wallet'),
    path('financial-hub/withdraw/', views.withdraw_funds, name='withdraw_funds'),
    path('financial-hub/invoice/<str:reference_id>/', views.invoice_receipt, name='invoice_receipt'),
    
    # Settings & Notifications
    path('settings/', views.settings_page, name='settings_page'),
    path('notification/<int:notif_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]
