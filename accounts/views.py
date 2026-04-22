from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from .forms import CustomUserCreationForm
from .models import CustomUser, SkillCategory, SkillBadge, AssessmentQuestion, JobPost, JobProposal, ServiceAgreement, Milestone, EncryptedMessage, Transaction, Notification
import uuid as _uuid
from django.utils import timezone as _tz


def generate_user_uid():
    """Generate a unique structured User ID: SC-YYYYMM-XXXXX"""
    prefix = 'SC'
    date_part = _tz.now().strftime('%Y%m')
    while True:
        random_part = _uuid.uuid4().hex[:5].upper()
        uid = f"{prefix}-{date_part}-{random_part}"
        if not CustomUser.objects.filter(user_uid=uid).exists():
            return uid

def landing_page(request):
    return render(request, 'accounts/landing.html')

def sign_up(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_uid = generate_user_uid()
            user.save()
            login(request, user)
            return redirect('landing_page')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def sign_in(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing_page')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/signin.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .gemini_service import analyze_id_document

def log_out(request):
    logout(request)
    return redirect('landing_page')

@login_required
def identity_vault(request):
    user = request.user
    
    if request.method == 'POST':
        if user.verification_status in ['Pending', 'Approved']:
            messages.error(request, "You cannot upload a new document at this time.")
            return redirect('identity_vault')
            
        if 'id_document' in request.FILES:
            uploaded_file = request.FILES['id_document']
            
            if uploaded_file.size > 5 * 1024 * 1024:
                messages.error(request, "File size exceeds 5MB limit.")
                return redirect('identity_vault')
                
            ext = uploaded_file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
                messages.error(request, "Invalid file format. Please upload PDF, JPG, or PNG.")
                return redirect('identity_vault')
                
            # Temporarily save to trigger media upload
            user.id_document = uploaded_file
            user.save()
            
            # Analyze using Gemini
            is_valid, new_status, reason = analyze_id_document(user.id_document.path)
            
            user.verification_status = new_status
            user.save()
            
            if new_status == 'Approved':
                messages.success(request, f"Document verified! Welcome to the Trusted Marketplace. ({reason})")
            elif new_status == 'Rejected':
                messages.error(request, f"Verification failed: {reason}")
            else:
                messages.warning(request, f"Your document is pending manual review. ({reason})")
                
            return redirect('identity_vault')
        else:
            messages.error(request, "Please select a file to upload.")
            
    return render(request, 'accounts/identity_vault.html', {'user': user})

from django.shortcuts import get_object_or_404
from .models import CustomUser, SkillCategory, SkillBadge, AssessmentQuestion
import random

def public_profile(request, username):
    profile_user = get_object_or_404(CustomUser, username=username)
    badges = profile_user.skill_badges.all().select_related('category')
    
    # Professional title
    professional_title = "Unskilled User"
    if profile_user.role == 'Skilled' or profile_user.role == 'Buyer':
        if badges.exists():
            top_badge = max(badges, key=lambda b: b.level)
            professional_title = f"{top_badge.category.name} Specialist"
        else:
            professional_title = "Skilled User"

    # Real active orders: agreements where user is client or provider and status is Active
    from django.db.models import Q as DQ
    active_agreements = ServiceAgreement.objects.filter(
        DQ(client=profile_user) | DQ(provider=profile_user),
        status='Active'
    ).select_related('proposal__job')

    recent_orders = []
    for ag in active_agreements[:5]:
        job = ag.proposal.job
        recent_orders.append({
            "service": job.title,
            "buyer": ag.client.username,
            "due_date": "Ongoing",
            "status": "In Progress",
            "amount": f"${job.budget_or_terms}" if '$' not in job.budget_or_terms else job.budget_or_terms,
        })

    # Real total earnings from transactions
    from django.db.models import Sum
    total_earnings_qs = profile_user.transactions.filter(
        transaction_type='Earnings', status='Completed'
    ).aggregate(total=Sum('amount'))
    total_earnings = f"${total_earnings_qs['total'] or 0:.2f}"

    # Weekly activity: proposals submitted in last 7 days, one bar per day
    from django.utils import timezone
    from datetime import timedelta
    today = timezone.now().date()
    weekly_activity = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = profile_user.submitted_proposals.filter(
            created_at__date=day
        ).count() + profile_user.posted_jobs.filter(
            created_at__date=day
        ).count()
        weekly_activity.append(min(count * 20 + 10, 100))  # scale to % height

    return render(request, 'accounts/public_profile.html', {
        'profile_user': profile_user,
        'badges': badges,
        'professional_title': professional_title,
        'recent_orders': recent_orders,
        'weekly_activity': weekly_activity,
        'total_earnings': total_earnings,
        'active_orders': active_agreements.count(),
        'seller_rating': "4.9/5",
        'gig_views': "3.4k",
    })

@login_required
def skill_lab_dashboard(request):
    categories = SkillCategory.objects.all()
    user_badges = {badge.category_id: badge for badge in request.user.skill_badges.all()}
    return render(request, 'accounts/skill_lab_dashboard.html', {
        'categories': categories,
        'user_badges': user_badges
    })

from .gemini_exam_service import generate_assessment_questions

@login_required
def take_assessment(request, category_id):
    category = get_object_or_404(SkillCategory, id=category_id)
    
    # Try to get existing questions for this category
    questions = list(category.questions.all())
    
    # If we don't have enough questions (or we want to always generate dynamically)
    # Let's dynamically generate 10 new questions every time for an infinite test bank!
    try:
        new_q_data = generate_assessment_questions(category.name)
        if new_q_data:
            # Clear old questions or just append? Let's just append to build the bank!
            # But to ensure they get exactly 10 questions for this test, we'll fetch the newly created ones.
            new_questions = []
            for q_dict in new_q_data:
                q = AssessmentQuestion.objects.create(
                    category=category,
                    question_text=q_dict.get('question_text', ''),
                    option_a=q_dict.get('option_a', ''),
                    option_b=q_dict.get('option_b', ''),
                    option_c=q_dict.get('option_c', ''),
                    option_d=q_dict.get('option_d', ''),
                    correct_option=q_dict.get('correct_option', 'A')
                )
                new_questions.append(q)
            
            # Use the 10 newly generated questions for this specific test session
            questions = new_questions
        else:
            # Fallback to existing questions if API fails
            if len(questions) > 10:
                questions = random.sample(questions, 10)
    except Exception as e:
        # Fallback to existing questions if API fails
        if len(questions) > 10:
            questions = random.sample(questions, 10)

    # If the API failed and we had less than 10 questions in the DB, just show whatever we have
    if len(questions) > 10:
        questions = random.sample(questions, 10)

    return render(request, 'accounts/assessment_test.html', {
        'category': category,
        'questions': questions
    })

@login_required
def grade_assessment(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(SkillCategory, id=category_id)
        questions_ids = request.POST.getlist('question_id')
        
        if not questions_ids:
            messages.error(request, "No questions submitted.")
            return redirect('skill_lab_dashboard')
            
        correct_count = 0
        total_questions = len(questions_ids)
        
        for q_id in questions_ids:
            question = get_object_or_404(AssessmentQuestion, id=q_id)
            user_answer = request.POST.get(f'question_{q_id}')
            if user_answer == question.correct_option:
                correct_count += 1
                
        score_percentage = (correct_count / total_questions) * 100
        score_percentage = int(score_percentage)
        
        passed = score_percentage >= 80
        badge_label = f"Skilled at {category.name}"
        
        if passed:
            badge, created = SkillBadge.objects.get_or_create(
                user=request.user,
                category=category,
                defaults={'level': 1}
            )
            if not created and badge.level < 5:
                badge.level += 1
                badge.save()
                
            # Upgrade user to Skilled if they are Unskilled
            if request.user.role == 'Unskilled':
                request.user.role = 'Skilled'
                request.user.save()
                
        # Store results in session for the results page
        request.session['assessment_result'] = {
            'category_name': category.name,
            'badge_label': badge_label,
            'score': score_percentage,
            'passed': passed,
            'category_id': category.id
        }
            
        return redirect('assessment_results')
    
    return redirect('skill_lab_dashboard')

@login_required
def assessment_results(request):
    result = request.session.get('assessment_result')
    if not result:
        return redirect('skill_lab_dashboard')
        
    return render(request, 'accounts/assessment_results.html', {'result': result})

@login_required
def mint_skillcurrency(request):
    if request.method == 'POST':
        result = request.session.get('assessment_result')
        if result and result.get('passed'):
            # Award 500 SC
            request.user.wallet_balance += 500
            request.user.save()
            messages.success(request, "Successfully minted 500 SkillCurrency!")
            # Clear session to prevent double minting
            del request.session['assessment_result']
            return redirect('public_profile', username=request.user.username)
            
    return redirect('skill_lab_dashboard')

def marketplace_feed(request):
    base_qs = JobPost.objects.filter(status='Open').select_related('author', 'category')

    # ── Filters from GET params ──────────────────────────────────────────────
    category_id     = request.GET.get('category', '').strip()
    interaction_type = request.GET.get('interaction_type', '').strip()
    search_query    = request.GET.get('q', '').strip()
    budget_range    = request.GET.get('budget_range', '').strip()
    preference_mode = request.GET.get('preference_mode', '').strip()  # 'on' | ''

    jobs = base_qs

    if category_id:
        jobs = jobs.filter(category_id=category_id)
    if interaction_type:
        jobs = jobs.filter(interaction_type=interaction_type)
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(budget_or_terms__icontains=search_query)
        )
    if budget_range == 'low':
        # Paid jobs that look "cheap" (mention $ and numbers < 200)
        jobs = jobs.filter(budget_or_terms__iregex=r'\$\s*\d{1,2}[^0-9]')
    elif budget_range == 'mid':
        jobs = jobs.filter(budget_or_terms__iregex=r'\$\s*[1-9]\d{2}')
    elif budget_range == 'high':
        jobs = jobs.filter(budget_or_terms__iregex=r'\$\s*[1-9]\d{3}')
    elif budget_range == 'barter':
        jobs = jobs.filter(interaction_type='Skill Barter')

    # ── Preference-based personalisation ────────────────────────────────────
    recommended_jobs = None
    user_skill_category_ids = []

    if request.user.is_authenticated:
        # Collect the skill-category IDs the user has verified badges for
        user_skill_category_ids = list(
            request.user.skill_badges.values_list('category_id', flat=True)
        )

    if preference_mode == 'on' and user_skill_category_ids:
        # Surface jobs whose category matches ANY of the user's skill badges
        recommended_jobs = jobs.filter(category_id__in=user_skill_category_ids).order_by('-created_at')
        # Other (non-matching) jobs shown below as "Other Opportunities"
        jobs = jobs.exclude(category_id__in=user_skill_category_ids).order_by('-created_at')
    else:
        jobs = jobs.order_by('-created_at')

    categories = SkillCategory.objects.all()

    return render(request, 'accounts/marketplace_feed.html', {
        'jobs': jobs,
        'recommended_jobs': recommended_jobs,
        'categories': categories,
        'selected_category': int(category_id) if category_id else '',
        'selected_type': interaction_type or '',
        'search_query': search_query,
        'budget_range': budget_range,
        'preference_mode': preference_mode,
        'user_skill_category_ids': user_skill_category_ids,
    })

@login_required
def create_job(request):
    # Only Buyer role or Admin (is_staff) can create jobs
    if not (request.user.is_staff or request.user.role == 'Buyer'):
        messages.error(request, "Only Buyers and Admins can post jobs. Switch your role to Buyer in Settings to get started.")
        return redirect('marketplace_feed')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        interaction_type = request.POST.get('interaction_type')
        budget_or_terms = request.POST.get('budget_or_terms')
        
        category = get_object_or_404(SkillCategory, id=category_id)
        
        job = JobPost.objects.create(
            author=request.user,
            title=title,
            description=description,
            category=category,
            interaction_type=interaction_type,
            budget_or_terms=budget_or_terms
        )
        messages.success(request, "Job posted successfully!")
        return redirect('job_detail', job_id=job.id)
        
    categories = SkillCategory.objects.all()
    return render(request, 'accounts/create_job.html', {'categories': categories})

def job_detail(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    
    # If the user is the author, show the proposals
    proposals = None
    if request.user.is_authenticated and request.user == job.author:
        proposals = job.proposals.all().order_by('-created_at')
        
    return render(request, 'accounts/job_detail.html', {
        'job': job,
        'proposals': proposals
    })

@login_required
def submit_proposal(request, job_id):
    job = get_object_or_404(JobPost, id=job_id)
    
    if request.user.role != 'Skilled':
        messages.error(request, "Only verified Skilled users can submit proposals.")
        return redirect('job_detail', job_id=job.id)
        
    if not request.user.is_identity_verified:
        messages.error(request, "You must verify your identity before submitting proposals.")
        return redirect('job_detail', job_id=job.id)
        
    if request.user == job.author:
        messages.error(request, "You cannot propose to your own job.")
        return redirect('job_detail', job_id=job.id)
        
    # Check if already proposed
    if JobProposal.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already submitted a proposal for this job.")
        return redirect('job_detail', job_id=job.id)
        
    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter')
        proposed_terms = request.POST.get('proposed_terms')
        
        JobProposal.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=cover_letter,
            proposed_terms=proposed_terms
        )
        
        # Notify Job Author
        create_notification(
            user=job.author,
            message=f"{request.user.username} submitted a proposal for '{job.title}'",
            link=f"/accounts/job/{job.id}/"
        )
        
        messages.success(request, "Your proposal has been submitted!")
        return redirect('job_detail', job_id=job.id)
        
    return render(request, 'accounts/submit_proposal.html', {'job': job})

@login_required
def my_activity(request):
    posted_jobs = request.user.posted_jobs.all().order_by('-created_at')
    submitted_proposals = request.user.submitted_proposals.all().order_by('-created_at')
    
    return render(request, 'accounts/my_activity.html', {
        'posted_jobs': posted_jobs,
        'submitted_proposals': submitted_proposals
    })

@login_required
def accept_proposal(request, proposal_id):
    proposal = get_object_or_404(JobProposal, id=proposal_id)
    job = proposal.job
    
    if request.user != job.author:
        messages.error(request, "Only the job author can accept proposals.")
        return redirect('job_detail', job_id=job.id)
        
    if request.method == 'POST':
        # Accept this proposal
        proposal.status = 'Accepted'
        proposal.save()
        
        # Reject other pending proposals for this job
        JobProposal.objects.filter(job=job, status='Pending').exclude(id=proposal.id).update(status='Rejected')
        
        # Create Service Agreement
        agreement = ServiceAgreement.objects.create(
            proposal=proposal,
            client=job.author,
            provider=proposal.applicant
        )
        
        # Update Job Status
        job.status = 'In Progress'
        job.save()
        
        # Create an initial Milestone
        Milestone.objects.create(
            agreement=agreement,
            title='Initial Setup & Planning',
            description='Agree on terms and begin work.',
            amount=0.00,
            status='In Progress'
        )
        
        # Notify Provider
        create_notification(
            user=proposal.applicant,
            message=f"{request.user.username} accepted your proposal for '{job.title}'!",
            link=f"/accounts/workspace/{agreement.id}/"
        )
        
        messages.success(request, f"You have accepted {proposal.applicant.username}'s proposal! Workspace created.")
        return redirect('workspace', agreement_id=agreement.id)
        
    return redirect('job_detail', job_id=job.id)

@login_required
def workspace(request, agreement_id):
    agreement = get_object_or_404(ServiceAgreement, id=agreement_id)
    
    if request.user != agreement.client and request.user != agreement.provider:
        messages.error(request, "You do not have access to this workspace.")
        return redirect('marketplace_feed')
        
    milestones = agreement.milestones.all().order_by('id')
    encrypted_messages = agreement.messages.all().order_by('timestamp')
    
    # Decrypt messages for display
    from .utils import decrypt_message
    chat_history = []
    for msg in encrypted_messages:
        decrypted_text = decrypt_message(msg.encrypted_content)
        chat_history.append({
            'sender': msg.sender.username,
            'text': decrypted_text,
            'timestamp': msg.timestamp
        })
        
    return render(request, 'accounts/workspace.html', {
        'agreement': agreement,
        'milestones': milestones,
        'chat_history': chat_history
    })

@login_required
def update_milestone(request, milestone_id):
    milestone = get_object_or_404(Milestone, id=milestone_id)
    agreement = milestone.agreement
    
    if request.user != agreement.client and request.user != agreement.provider:
        return redirect('marketplace_feed')
        
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Milestone.STATUS_CHOICES):
            
            # Settlement Logic when completed by client
            if new_status == 'Completed' and milestone.status != 'Completed' and request.user == agreement.client:
                from django.db import transaction as db_transaction
                from django.db.models import F
                import uuid
                
                try:
                    with db_transaction.atomic():
                        client = CustomUser.objects.select_for_update().get(id=agreement.client.id)
                        provider = CustomUser.objects.select_for_update().get(id=agreement.provider.id)
                        
                        amount = milestone.amount
                        
                        if client.wallet_balance < amount:
                            messages.error(request, f"Insufficient funds in your wallet to settle milestone '{milestone.title}'. Please top up.")
                            return redirect('workspace', agreement_id=agreement.id)
                            
                        # Deduct from client
                        client.wallet_balance = F('wallet_balance') - amount
                        client.save()
                        
                        # Add to provider
                        provider.wallet_balance = F('wallet_balance') + amount
                        provider.save()
                        
                        ref_id = str(uuid.uuid4())[:12].upper()
                        
                        # Create Client Transaction
                        Transaction.objects.create(
                            user=client,
                            amount=-amount,
                            transaction_type='Escrow Hold', # Or 'Payment'
                            payment_method='Internal Wallet',
                            status='Completed',
                            reference_id=f"PAY-{ref_id}",
                            description=f"Payment for '{milestone.title}'"
                        )
                        
                        # Create Provider Transaction
                        Transaction.objects.create(
                            user=provider,
                            amount=amount,
                            transaction_type='Earnings',
                            payment_method='Internal Wallet',
                            status='Completed',
                            reference_id=f"EARN-{ref_id}",
                            description=f"Earnings from '{milestone.title}'"
                        )
                        
                        milestone.status = new_status
                        milestone.save()
                        
                        # Notify Provider
                        create_notification(
                            user=provider,
                            message=f"Milestone '{milestone.title}' completed. ${amount} added to your wallet!",
                            link=f"/accounts/financial-hub/"
                        )
                        
                        messages.success(request, f"Milestone '{milestone.title}' completed and ${amount} settled securely.")
                        
                except Exception as e:
                    messages.error(request, f"An error occurred during settlement: {str(e)}")
            else:
                milestone.status = new_status
                milestone.save()
                messages.success(request, f"Milestone '{milestone.title}' updated to {new_status}.")
            
    return redirect('workspace', agreement_id=agreement.id)

@login_required
def financial_hub(request):
    # Fetch fresh user data
    user = CustomUser.objects.get(id=request.user.id)
    transactions = user.transactions.all().order_by('-timestamp')
    
    return render(request, 'accounts/financial_hub.html', {
        'wallet_balance': user.wallet_balance,
        'transactions': transactions
    })

@login_required
def top_up_wallet(request):
    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        
        try:
            from decimal import Decimal, InvalidOperation
            amount = Decimal(str(amount_str))
            if amount <= 0:
                raise ValueError("Amount must be positive")
                
            from django.db import transaction as db_transaction
            from django.db.models import F
            import uuid
            
            with db_transaction.atomic():
                user = CustomUser.objects.select_for_update().get(id=request.user.id)
                user.wallet_balance = F('wallet_balance') + amount
                user.save()
                
                ref_id = str(uuid.uuid4())[:12].upper()
                
                Transaction.objects.create(
                    user=user,
                    amount=amount,
                    transaction_type='Deposit',
                    payment_method=payment_method,
                    status='Completed',
                    reference_id=f"DEP-{ref_id}",
                    description=f"Wallet Top-Up via {payment_method}"
                )
                
            messages.success(request, f"Successfully added ${amount} to your wallet!")
        except Exception as e:
            messages.error(request, f"Failed to top up: {str(e)}")
            
    return redirect('financial_hub')

@login_required
def withdraw_funds(request):
    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')

        try:
            from decimal import Decimal
            import uuid
            from django.db import transaction as db_transaction
            from django.db.models import F

            amount = Decimal(str(amount_str))
            if amount <= 0:
                raise ValueError("Amount must be positive")

            with db_transaction.atomic():
                user = CustomUser.objects.select_for_update().get(id=request.user.id)

                if user.wallet_balance < amount:
                    messages.error(request, f"Insufficient funds. Your balance is ${user.wallet_balance}.")
                    return redirect('public_profile', username=request.user.username)

                user.wallet_balance = F('wallet_balance') - amount
                user.save()

                ref_id = str(uuid.uuid4())[:12].upper()

                Transaction.objects.create(
                    user=user,
                    amount=-amount,
                    transaction_type='Withdrawal',
                    payment_method=payment_method,
                    status='Completed',
                    reference_id=f"WTH-{ref_id}",
                    description=f"Withdrawal via {payment_method}"
                )

            messages.success(request, f"Withdrawal of ${amount} via {payment_method} has been processed!")
        except Exception as e:
            messages.error(request, f"Withdrawal failed: {str(e)}")

    return redirect('financial_hub')

@login_required
def invoice_receipt(request, reference_id):
    transaction = get_object_or_404(Transaction, reference_id=reference_id)
    
    if request.user != transaction.user:
        messages.error(request, "You do not have permission to view this invoice.")
        return redirect('financial_hub')
        
    return render(request, 'accounts/invoice_receipt.html', {
        'transaction': transaction
    })

def create_notification(user, message, link=None):
    Notification.objects.create(user=user, message=message, link=link)

@login_required
def settings_page(request):
    user = CustomUser.objects.get(id=request.user.id)
    if request.method == 'POST':
        section = request.POST.get('section', 'public')

        if section == 'public':
            # Public profile section
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            bio = request.POST.get('bio', '')
            avatar = request.FILES.get('avatar')

            user.first_name = first_name
            user.last_name = last_name
            user.bio = bio

            if avatar:
                user.avatar = avatar

            user.save()
            messages.success(request, "Public profile updated successfully!")

        elif section == 'account':
            # Account settings section
            email = request.POST.get('email', '')
            nid = request.POST.get('nid', '')

            if email:
                user.email = email
            if nid:
                user.nid_tin_number = nid

            user.save()
            messages.success(request, "Account settings updated successfully!")

        return redirect('settings_page')

    return render(request, 'accounts/settings.html', {'user': user})

@login_required
def mark_notification_read(request, notif_id):
    try:
        notif = Notification.objects.get(id=notif_id, user=request.user)
        notif.is_read = True
        notif.save()
        if notif.link:
            return redirect(notif.link)
    except Notification.DoesNotExist:
        pass
    return redirect(request.META.get('HTTP_REFERER', 'landing_page'))


def search_users(request):
    """Search for users by full name or username."""
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(is_superuser=True).order_by('username')[:30]
    return render(request, 'accounts/user_search_results.html', {
        'query': query,
        'results': results,
    })
