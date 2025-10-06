from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

# Create your models here.

class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('loan_officer', 'Loan Officer'),
        ('borrower', 'Borrower'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='borrower')
    
    # Additional borrower fields
    aadhar_number = models.CharField(max_length=12, blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dairy_license_number = models.CharField(max_length=50, blank=True, null=True)
    business_name = models.CharField(max_length=100, blank=True, null=True)
    milk_supply_daily = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Daily milk supply in liters")
    herd_size = models.IntegerField(blank=True, null=True, help_text="Number of cattle")
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, help_text="Monthly income in INR")
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.user_type}"
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_loan_officer(self):
        return self.user_type == 'loan_officer'
    
    @property
    def is_borrower(self):
        return self.user_type == 'borrower'

class LoanType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    eligibility_rules = models.TextField(help_text="Eligibility criteria like Dairy License, ID Proof requirements")
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    allow_custom_amount = models.BooleanField(default=True, help_text="Allow borrowers to request custom amounts within limits")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class InterestRate(models.Model):
    DURATION_CHOICES = [
        (12, '1 Year'),
        (24, '2 Years'),
        (36, '3 Years'),
        (48, '4 Years'),
        (60, '5 Years'),
    ]
    
    RISK_PROFILE_CHOICES = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ]
    
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE, related_name='interest_rates')
    duration_months = models.IntegerField(choices=DURATION_CHOICES)
    risk_profile = models.CharField(max_length=10, choices=RISK_PROFILE_CHOICES, default='medium')
    annual_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('50.00'))])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['loan_type', 'duration_months', 'risk_profile']
    
    def __str__(self):
        return f"{self.loan_type.name} - {self.get_duration_months_display()} - {self.get_risk_profile_display()} ({self.annual_rate}%)"

class LoanApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
    ]
    
    application_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loan_applications')
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE)
    requested_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    purpose = models.TextField(help_text="Purpose of the loan")
    
    # Business Information
    business_experience_years = models.IntegerField(help_text="Years of dairy business experience")
    current_monthly_income = models.DecimalField(max_digits=12, decimal_places=2, help_text="Current monthly income")
    existing_loans = models.BooleanField(default=False, help_text="Do you have any existing loans?")
    existing_loan_details = models.TextField(blank=True, null=True, help_text="Details of existing loans if any")
    
    # Application Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    reviewed_date = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviewed_applications')
    rejection_reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, help_text="Internal notes for review")
    
    def __str__(self):
        return f"{self.borrower.get_full_name()} - {self.loan_type.name} - {self.requested_amount}"

class LoanDisbursement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('disbursed', 'Disbursed'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
    ]
    
    loan_application = models.OneToOneField(LoanApplication, on_delete=models.CASCADE, related_name='disbursement')
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.ForeignKey(InterestRate, on_delete=models.CASCADE)
    tenure_months = models.IntegerField()
    emi_amount = models.DecimalField(max_digits=12, decimal_places=2)
    total_interest = models.DecimalField(max_digits=12, decimal_places=2)
    total_repayment = models.DecimalField(max_digits=12, decimal_places=2)
    
    disbursement_date = models.DateField(blank=True, null=True)
    first_emi_date = models.DateField()
    last_emi_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Loan #{self.loan_application.application_id} - {self.approved_amount}"
    
    def calculate_emi_details(self):
        """Calculate EMI amount, total interest, and total repayment"""
        principal = self.approved_amount
        rate = self.interest_rate.annual_rate / 100 / 12  # Monthly rate
        months = self.tenure_months
        
        if rate == 0:
            self.emi_amount = principal / months
        else:
            self.emi_amount = principal * (rate * (1 + rate) ** months) / ((1 + rate) ** months - 1)
        
        self.total_repayment = self.emi_amount * months
        self.total_interest = self.total_repayment - principal
        
        return {
            'emi_amount': self.emi_amount,
            'total_interest': self.total_interest,
            'total_repayment': self.total_repayment
        }

class EMISchedule(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('partial', 'Partial Payment'),
    ]
    
    loan_disbursement = models.ForeignKey(LoanDisbursement, on_delete=models.CASCADE, related_name='emi_schedule')
    emi_number = models.IntegerField()
    due_date = models.DateField()
    emi_amount = models.DecimalField(max_digits=12, decimal_places=2)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_date = models.DateField(blank=True, null=True)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['loan_disbursement', 'emi_number']
        ordering = ['emi_number']
    
    def __str__(self):
        return f"EMI #{self.emi_number} - {self.loan_disbursement.loan_application.borrower.get_full_name()} - {self.due_date}"
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status != 'paid'
    
    @property
    def remaining_amount(self):
        return self.emi_amount - self.paid_amount

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('upi', 'UPI'),
        ('other', 'Other'),
    ]
    
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    emi_schedule = models.ForeignKey(EMISchedule, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateField()
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='received_payments')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount} - {self.payment_date}"

class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('aadhar', 'Aadhaar Card'),
        ('pan', 'PAN Card'),
        ('voter_id', 'Voter ID'),
        ('dairy_license', 'Dairy License'),
        ('food_license', 'Food License'),
        ('bank_statement', 'Bank Statement'),
        ('income_proof', 'Income Proof'),
        ('business_license', 'Business License'),
        ('other', 'Other'),
    ]
    
    loan_application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='documents/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text="File size in bytes")
    uploaded_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='verified_documents')
    verification_notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.loan_application.borrower.get_full_name()} - {self.get_document_type_display()}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)

class LoanAmountSlab(models.Model):
    """Model for defining loan amount slabs/ranges for each loan type"""
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE, related_name='amount_slabs')
    slab_name = models.CharField(max_length=100, help_text="e.g., Small, Medium, Large")
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Minimum amount for this slab")
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maximum amount for this slab")
    description = models.TextField(blank=True, help_text="Description of this amount slab")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['loan_type', 'slab_name']
        ordering = ['min_amount']

    def __str__(self):
        return f"{self.loan_type.name} - {self.slab_name} (₹{self.min_amount} - ₹{self.max_amount})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.min_amount >= self.max_amount:
            raise ValidationError("Maximum amount must be greater than minimum amount.")

class EMIConfiguration(models.Model):
    """Model for EMI configuration with auto-calculation capabilities"""
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE, related_name='emi_configurations')
    amount_slab = models.ForeignKey(LoanAmountSlab, on_delete=models.CASCADE, related_name='emi_configurations', null=True, blank=True)
    interest_rate = models.ForeignKey(InterestRate, on_delete=models.CASCADE, related_name='emi_configurations')
    
    # EMI Configuration
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    tenure_months = models.IntegerField(help_text="Loan tenure in months")
    
    # Auto-calculated fields (will be calculated based on interest rate and tenure)
    emi_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_interest = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_repayment = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    # Configuration settings
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['loan_type', 'amount_slab', 'interest_rate', 'tenure_months', 'frequency']
        ordering = ['loan_type', 'tenure_months']

    def __str__(self):
        slab_info = f" - {self.amount_slab.slab_name}" if self.amount_slab else ""
        return f"{self.loan_type.name}{slab_info} - {self.tenure_months} months - {self.get_frequency_display()}"

    def calculate_emi_details(self, loan_amount=None):
        """Calculate EMI details using standard loan formula"""
        if not loan_amount:
            loan_amount = self.amount_slab.min_amount if self.amount_slab else 0
        
        # Get monthly interest rate
        monthly_rate = self.interest_rate.annual_rate / 100 / 12
        
        # Calculate EMI using standard formula
        if monthly_rate == 0:
            emi_amount = loan_amount / self.tenure_months
        else:
            emi_amount = loan_amount * (monthly_rate * (1 + monthly_rate) ** self.tenure_months) / ((1 + monthly_rate) ** self.tenure_months - 1)
        
        # Adjust for frequency
        if self.frequency == 'quarterly':
            emi_amount = emi_amount * 3
        elif self.frequency == 'yearly':
            emi_amount = emi_amount * 12
        
        total_repayment = emi_amount * self.tenure_months
        total_interest = total_repayment - loan_amount
        
        return {
            'emi_amount': round(emi_amount, 2),
            'total_repayment': round(total_repayment, 2),
            'total_interest': round(total_interest, 2),
            'loan_amount': loan_amount,
            'monthly_rate': monthly_rate,
            'tenure_months': self.tenure_months
        }

    def save(self, *args, **kwargs):
        # Auto-calculate EMI details if amount_slab exists
        if self.amount_slab and self.interest_rate:
            details = self.calculate_emi_details()
            self.emi_amount = details['emi_amount']
            self.total_interest = details['total_interest']
            self.total_repayment = details['total_repayment']
        super().save(*args, **kwargs)

    @property
    def effective_annual_rate(self):
        """Calculate effective annual rate based on frequency"""
        if self.frequency == 'monthly':
            return self.interest_rate.annual_rate
        elif self.frequency == 'quarterly':
            return self.interest_rate.annual_rate * 0.25
        elif self.frequency == 'yearly':
            return self.interest_rate.annual_rate / 12
        return self.interest_rate.annual_rate
