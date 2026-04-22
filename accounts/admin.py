from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html, mark_safe
from django.utils.timezone import localtime

from .models import (
    CustomUser, SkillCategory, SkillBadge,
    AssessmentQuestion, JobPost, JobProposal,
    ServiceAgreement, Milestone, Transaction, Notification
)


# ─────────────────────────────────────────────────────────────
#  CUSTOM USER ADMIN
# ─────────────────────────────────────────────────────────────
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display  = [
        'username', 'email', 'role',
        'nid_tin_number', 'verification_status_badge',
        'is_identity_verified', 'wallet_balance',
    ]
    list_filter   = ['role', 'verification_status', 'is_identity_verified']
    search_fields = ['username', 'email', 'nid_tin_number']
    list_editable = ['is_identity_verified']        # ← tick directly in list view

    fieldsets = UserAdmin.fieldsets + (
        ('Platform Info', {
            'fields': (
                'role', 'nid_tin_number', 'bio', 'avatar',
                'wallet_balance',
            )
        }),
        ('Identity Verification', {
            'fields': ('id_document', 'verification_status', 'is_identity_verified'),
            'description': (
                '⚠️ Ticking "Is identity verified" will automatically set '
                'Verification Status → Approved and notify the user.'
            ),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Platform Info', {
            'fields': ('role', 'nid_tin_number', 'wallet_balance',
                       'verification_status', 'is_identity_verified'),
        }),
    )

    # ── Coloured badge for verification_status ──
    @admin.display(description='Verification Status')
    def verification_status_badge(self, obj):
        colours = {
            'Approved':   ('#dcfce7', '#15803d'),
            'Pending':    ('#fef9c3', '#92400e'),
            'Rejected':   ('#fee2e2', '#991b1b'),
            'Unverified': ('#f3f4f6', '#6b7280'),
        }
        bg, fg = colours.get(obj.verification_status, ('#f3f4f6', '#6b7280'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;'
            'border-radius:12px;font-size:0.78rem;font-weight:700;">{}</span>',
            bg, fg, obj.verification_status
        )

    # ── Auto-sync: ticking is_identity_verified → Approved ──
    def save_model(self, request, obj, form, change):
        if obj.is_identity_verified and obj.verification_status != 'Approved':
            obj.verification_status = 'Approved'
            # Create in-app notification for the user
            Notification.objects.get_or_create(
                user=obj,
                message='✅ Your identity has been verified by the admin!',
                defaults={'link': '/identity-vault/'},
            )
        elif not obj.is_identity_verified and obj.verification_status == 'Approved':
            # If admin un-ticks, revert to Unverified
            obj.verification_status = 'Unverified'
        super().save_model(request, obj, form, change)

    # ── Bulk actions ──
    @admin.action(description='✅ Approve selected identities')
    def approve_identities(self, request, queryset):
        for user in queryset:
            user.is_identity_verified = True
            user.verification_status  = 'Approved'
            user.save()
            Notification.objects.get_or_create(
                user=user,
                message='✅ Your identity has been verified by the admin!',
                defaults={'link': '/identity-vault/'},
            )
        self.message_user(request, f'{queryset.count()} identities approved.')

    @admin.action(description='❌ Reject selected identities')
    def reject_identities(self, request, queryset):
        queryset.update(is_identity_verified=False, verification_status='Rejected')
        self.message_user(request, f'{queryset.count()} identities rejected.')

    actions = ['approve_identities', 'reject_identities']


# ─────────────────────────────────────────────────────────────
#  JOB PROPOSAL INLINE (shown inside Job detail page)
# ─────────────────────────────────────────────────────────────
class JobProposalInline(admin.TabularInline):
    model        = JobProposal
    extra        = 0
    readonly_fields = ['applicant', 'cover_letter', 'proposed_terms', 'created_at', 'status']
    can_delete   = True
    show_change_link = True


# ─────────────────────────────────────────────────────────────
#  JOB POST ADMIN
# ─────────────────────────────────────────────────────────────
@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display  = [
        'title', 'author', 'category', 'type_badge',
        'budget_or_terms', 'status_badge', 'proposal_count', 'created_at',
    ]
    list_filter   = ['status', 'interaction_type', 'category', 'created_at']
    search_fields = ['title', 'description', 'author__username']
    ordering      = ['-created_at']
    date_hierarchy = 'created_at'
    inlines       = [JobProposalInline]

    fieldsets = (
        ('Job Details', {
            'fields': ('author', 'title', 'description', 'category',
                       'interaction_type', 'budget_or_terms', 'status')
        }),
    )

    # ── Coloured type badge ──
    @admin.display(description='Type')
    def type_badge(self, obj):
        if obj.interaction_type == 'Paid Service':
            return mark_safe(
                '<span style="background:#dcfce7;color:#15803d;padding:2px 9px;'
                'border-radius:12px;font-size:.75rem;font-weight:700;">💰 Paid</span>'
            )
        return mark_safe(
            '<span style="background:#ede9fe;color:#6d28d9;padding:2px 9px;'
            'border-radius:12px;font-size:.75rem;font-weight:700;">🔄 Barter</span>'
        )

    # ── Coloured status badge ──
    @admin.display(description='Status')
    def status_badge(self, obj):
        colours = {
            'Open':        ('#dcfce7', '#15803d'),
            'In Progress': ('#fef9c3', '#92400e'),
            'Completed':   ('#e0e7ff', '#4338ca'),
        }
        bg, fg = colours.get(obj.status, ('#f3f4f6', '#6b7280'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 9px;'
            'border-radius:12px;font-size:.75rem;font-weight:700;">{}</span>',
            bg, fg, obj.status
        )

    # ── Proposal count ──
    @admin.display(description='Proposals')
    def proposal_count(self, obj):
        count = obj.proposals.count()
        return format_html(
            '<span style="background:#f3f4f6;padding:2px 8px;border-radius:8px;'
            'font-weight:700;">{}</span>', count
        )

    # ── Bulk actions ──
    @admin.action(description='📌 Mark selected jobs as Open')
    def mark_open(self, request, queryset):
        queryset.update(status='Open')
        self.message_user(request, f'{queryset.count()} jobs marked as Open.')

    @admin.action(description='🏁 Mark selected jobs as Completed')
    def mark_completed(self, request, queryset):
        queryset.update(status='Completed')
        self.message_user(request, f'{queryset.count()} jobs marked as Completed.')

    actions = ['mark_open', 'mark_completed']


# ─────────────────────────────────────────────────────────────
#  JOB PROPOSAL ADMIN (standalone)
# ─────────────────────────────────────────────────────────────
@admin.register(JobProposal)
class JobProposalAdmin(admin.ModelAdmin):
    list_display  = ['job', 'applicant', 'proposed_terms', 'status', 'created_at']
    list_filter   = ['status', 'created_at']
    search_fields = ['job__title', 'applicant__username']
    ordering      = ['-created_at']

    @admin.action(description='✅ Accept selected proposals')
    def accept_proposals(self, request, queryset):
        queryset.update(status='Accepted')
        self.message_user(request, f'{queryset.count()} proposals accepted.')

    @admin.action(description='❌ Reject selected proposals')
    def reject_proposals(self, request, queryset):
        queryset.update(status='Rejected')
        self.message_user(request, f'{queryset.count()} proposals rejected.')

    actions = ['accept_proposals', 'reject_proposals']


# ─────────────────────────────────────────────────────────────
#  REMAINING MODELS
# ─────────────────────────────────────────────────────────────
@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'description']
    search_fields = ['name']


@admin.register(SkillBadge)
class SkillBadgeAdmin(admin.ModelAdmin):
    list_display  = ['user', 'category', 'level', 'date_earned']
    list_filter   = ['category', 'level']
    search_fields = ['user__username', 'category__name']


@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display  = ['category', 'question_text', 'correct_option']
    list_filter   = ['category']
    search_fields = ['question_text']


class MilestoneInline(admin.TabularInline):
    model  = Milestone
    extra  = 0
    fields = ['title', 'amount', 'due_date', 'status']

@admin.register(ServiceAgreement)
class ServiceAgreementAdmin(admin.ModelAdmin):
    list_display  = ['id', 'client', 'provider', 'status', 'created_at']
    list_filter   = ['status']
    search_fields = ['client__username', 'provider__username']
    inlines       = [MilestoneInline]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'transaction_type', 'amount', 'payment_method', 'status', 'reference_id', 'timestamp']
    list_filter   = ['transaction_type', 'status', 'payment_method']
    search_fields = ['user__username', 'reference_id']
    ordering      = ['-timestamp']
    readonly_fields = ['reference_id', 'timestamp']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['user', 'message', 'is_read', 'created_at']
    list_filter   = ['is_read']
    search_fields = ['user__username', 'message']
    ordering      = ['-created_at']
