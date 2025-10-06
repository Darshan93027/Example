from django.contrib import admin
from .models import (
    UserProfile, LoanType, InterestRate, LoanApplication,
    LoanDisbursement, EMISchedule, Payment, Document,
    LoanAmountSlab, EMIConfiguration
)

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'user_type', 'business_name', 'created_at')
    list_filter = ('user_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'business_name', 'aadhar_number')
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'phone', 'user_type')
        }),
        ('Personal Details', {
            'fields': ('aadhar_number', 'pan_number', 'address')
        }),
        ('Business Details', {
            'fields': ('business_name', 'dairy_license_number', 'milk_supply_daily', 'herd_size', 'monthly_income')
        }),
    )

@admin.register(LoanType)
class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_amount', 'max_amount', 'allow_custom_amount', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Loan Limits', {
            'fields': ('min_amount', 'max_amount', 'allow_custom_amount')
        }),
        ('Eligibility', {
            'fields': ('eligibility_rules',)
        }),
    )

@admin.register(InterestRate)
class InterestRateAdmin(admin.ModelAdmin):
    list_display = ('loan_type', 'duration_months', 'risk_profile', 'annual_rate', 'is_active')
    list_filter = ('loan_type', 'duration_months', 'risk_profile', 'is_active')
    search_fields = ('loan_type__name',)

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id', 'borrower', 'loan_type', 'requested_amount', 'status', 'applied_date')
    list_filter = ('status', 'loan_type', 'applied_date')
    search_fields = ('application_id', 'borrower__username', 'borrower__first_name', 'borrower__last_name')
    readonly_fields = ('application_id', 'applied_date')
    fieldsets = (
        ('Application Details', {
            'fields': ('application_id', 'borrower', 'loan_type', 'requested_amount', 'purpose')
        }),
        ('Business Information', {
            'fields': ('business_experience_years', 'current_monthly_income', 'existing_loans', 'existing_loan_details')
        }),
        ('Review Status', {
            'fields': ('status', 'reviewed_date', 'reviewed_by', 'rejection_reason', 'notes')
        }),
    )

@admin.register(LoanDisbursement)
class LoanDisbursementAdmin(admin.ModelAdmin):
    list_display = ('loan_application', 'approved_amount', 'tenure_months', 'emi_amount', 'status', 'disbursement_date')
    list_filter = ('status', 'disbursement_date', 'interest_rate__loan_type')
    search_fields = ('loan_application__application_id', 'loan_application__borrower__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Loan Details', {
            'fields': ('loan_application', 'approved_amount', 'interest_rate', 'tenure_months')
        }),
        ('EMI Calculation', {
            'fields': ('emi_amount', 'total_interest', 'total_repayment')
        }),
        ('Disbursement', {
            'fields': ('status', 'disbursement_date', 'first_emi_date', 'last_emi_date')
        }),
    )

@admin.register(EMISchedule)
class EMIScheduleAdmin(admin.ModelAdmin):
    list_display = ('loan_disbursement', 'emi_number', 'due_date', 'emi_amount', 'status', 'paid_amount')
    list_filter = ('status', 'due_date', 'loan_disbursement__loan_application__loan_type')
    search_fields = ('loan_disbursement__loan_application__application_id', 'loan_disbursement__loan_application__borrower__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('loan_disbursement', 'emi_number')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'emi_schedule', 'amount', 'payment_method', 'payment_date', 'received_by')
    list_filter = ('payment_method', 'payment_date', 'received_by')
    search_fields = ('payment_id', 'emi_schedule__loan_disbursement__loan_application__application_id')
    readonly_fields = ('payment_id', 'created_at')

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('loan_application', 'document_type', 'file_name', 'is_verified', 'uploaded_date', 'verified_by')
    list_filter = ('document_type', 'is_verified', 'uploaded_date')
    search_fields = ('loan_application__application_id', 'loan_application__borrower__username', 'file_name')
    readonly_fields = ('uploaded_date', 'file_size')

@admin.register(LoanAmountSlab)
class LoanAmountSlabAdmin(admin.ModelAdmin):
    list_display = ('loan_type', 'slab_name', 'min_amount', 'max_amount', 'is_active', 'created_at')
    list_filter = ('loan_type', 'is_active', 'created_at')
    search_fields = ('loan_type__name', 'slab_name', 'description')
    fieldsets = (
        ('Basic Info', {
            'fields': ('loan_type', 'slab_name', 'description', 'is_active')
        }),
        ('Amount Range', {
            'fields': ('min_amount', 'max_amount')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(EMIConfiguration)
class EMIConfigurationAdmin(admin.ModelAdmin):
    list_display = ('loan_type', 'amount_slab', 'interest_rate', 'frequency', 'tenure_months', 'emi_amount', 'is_active')
    list_filter = ('loan_type', 'frequency', 'is_active', 'created_at')
    search_fields = ('loan_type__name', 'amount_slab__slab_name')
    fieldsets = (
        ('Configuration', {
            'fields': ('loan_type', 'amount_slab', 'interest_rate', 'frequency', 'tenure_months', 'is_active')
        }),
        ('Calculated Values', {
            'fields': ('emi_amount', 'total_interest', 'total_repayment'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('emi_amount', 'total_interest', 'total_repayment', 'created_at', 'updated_at')
