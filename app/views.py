from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    UserProfile, LoanType, InterestRate, LoanApplication, 
    LoanDisbursement, EMISchedule, Payment, Document,
    LoanAmountSlab, EMIConfiguration
)
from .forms import (
    SignUpForm, AdminSignUpForm, LoanTypeForm, InterestRateForm, EMICalculatorForm,
    LoanAmountSlabForm, EMIConfigurationForm, EMICalculatorAdvancedForm
)

# Create your views here.

# Admin Authentication and Access Control
def admin_required(view_func):
    """Decorator to ensure only admin users can access certain views"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            user_profile = request.user.userprofile
            if not user_profile.is_admin:
                messages.error(request, 'Access denied. Admin privileges required.')
                return redirect('index')
        except UserProfile.DoesNotExist:
            messages.error(request, 'User profile not found. Please contact administrator.')
            return redirect('index')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def landing_page(request):
    return render(request, 'app/landing.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone = form.cleaned_data.get('phone')
            UserProfile.objects.create(user=user, phone=phone)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'app/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'app/login.html')

@login_required
def index_view(request):
    return render(request, 'app/index.html')

def logout_view(request):
    logout(request)
    return redirect('landing')

# Bank Portal Views
@login_required
def apply_loan_view(request):
    """View for loan application form"""
    return render(request, 'app/apply_loan.html')

@login_required
def loan_plans_view(request):
    """View for displaying loan plans"""
    loan_types = LoanType.objects.filter(is_active=True)
    context = {
        'loan_types': loan_types,
    }
    return render(request, 'app/loan_plans.html', context)

@login_required
def emi_calculator_view(request):
    """View for EMI calculator"""
    return render(request, 'app/emi_calculator.html')

@login_required
def my_applications_view(request):
    """View for user's loan applications"""
    applications = LoanApplication.objects.filter(user=request.user).order_by('-applied_date')
    context = {
        'applications': applications,
    }
    return render(request, 'app/my_applications.html', context)

@login_required
def account_services_view(request):
    """View for account services"""
    return render(request, 'app/account_services.html')

@login_required
def support_view(request):
    """View for customer support"""
    return render(request, 'app/support.html')

def about_us_view(request):
    """View for about us page"""
    return render(request, 'app/about_us.html')

def contact_us_view(request):
    """View for contact us page"""
    return render(request, 'app/contact_us.html')

def privacy_policy_view(request):
    """View for privacy policy page"""
    return render(request, 'app/privacy_policy.html')

def terms_conditions_view(request):
    """View for terms and conditions page"""
    return render(request, 'app/terms_conditions.html')

# Admin Access to Banking Portal Features
@admin_required
def admin_banking_portal(request):
    """Admin access to all banking portal features"""
    return render(request, 'app/admin_banking_portal.html')

@admin_required
def admin_apply_loan_view(request):
    """Admin view for loan application management"""
    applications = LoanApplication.objects.all().order_by('-applied_date')
    context = {
        'applications': applications,
    }
    return render(request, 'app/admin_apply_loan.html', context)

@admin_required
def admin_loan_plans_view(request):
    """Admin view for managing loan plans"""
    loan_types = LoanType.objects.all()
    context = {
        'loan_types': loan_types,
    }
    return render(request, 'app/admin_loan_plans.html', context)

@admin_required
def admin_user_management(request):
    """Admin view for user management"""
    users = User.objects.all().order_by('-date_joined')
    context = {
        'users': users,
    }
    return render(request, 'app/admin_user_management.html', context)

@admin_required
def admin_system_settings(request):
    """Admin view for system settings"""
    return render(request, 'app/admin_system_settings.html')

def admin_signup_view(request):
    """Admin signup view with authorization code"""
    if request.method == 'POST':
        form = AdminSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create admin user profile
            UserProfile.objects.create(
                user=user, 
                phone=form.cleaned_data.get('phone'),
                user_type='admin'
            )
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Admin account created successfully!')
            return redirect('admin_dashboard')
    else:
        form = AdminSignUpForm()
    return render(request, 'app/admin_signup.html', {'form': form})

def admin_login_view(request):
    """Admin-specific login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                user_profile = user.userprofile
                if user_profile.is_admin:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.first_name}!')
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Access denied. Admin privileges required.')
            except UserProfile.DoesNotExist:
                messages.error(request, 'User profile not found. Please contact administrator.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'app/admin_login.html')

@admin_required
def admin_dashboard(request):
    """Admin dashboard with overview cards and statistics"""
    
    # Calculate dashboard statistics
    total_loans_disbursed = LoanDisbursement.objects.filter(status='disbursed').aggregate(
        total=Sum('approved_amount')
    )['total'] or 0
    
    active_emi_accounts = LoanDisbursement.objects.filter(
        status='disbursed'
    ).exclude(
        emi_schedule__status='paid'
    ).distinct().count()
    
    pending_payments = EMISchedule.objects.filter(
        status='pending',
        due_date__lte=timezone.now().date()
    ).count()
    
    overdue_payments = EMISchedule.objects.filter(
        status='overdue'
    ).count()
    
    # Recent loan applications
    recent_applications = LoanApplication.objects.filter(
        status='pending'
    ).order_by('-applied_date')[:5]
    
    # Recent disbursements
    recent_disbursements = LoanDisbursement.objects.filter(
        status='disbursed'
    ).order_by('-disbursement_date')[:5]
    
    # Monthly statistics
    current_month = timezone.now().replace(day=1)
    monthly_disbursements = LoanDisbursement.objects.filter(
        disbursement_date__gte=current_month,
        status='disbursed'
    ).aggregate(total=Sum('approved_amount'))['total'] or 0
    
    monthly_payments = Payment.objects.filter(
        payment_date__gte=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Loan type distribution
    loan_type_stats = LoanType.objects.annotate(
        application_count=Count('loanapplication'),
        disbursed_count=Count('loanapplication__disbursement', filter=Q(loanapplication__disbursement__status='disbursed'))
    )
    
    context = {
        'total_loans_disbursed': total_loans_disbursed,
        'active_emi_accounts': active_emi_accounts,
        'pending_payments': pending_payments,
        'overdue_payments': overdue_payments,
        'recent_applications': recent_applications,
        'recent_disbursements': recent_disbursements,
        'monthly_disbursements': monthly_disbursements,
        'monthly_payments': monthly_payments,
        'loan_type_stats': loan_type_stats,
    }
    
    return render(request, 'app/admin_dashboard.html', context)

@admin_required
def admin_loan_applications(request):
    """Admin view for managing loan applications"""
    applications = LoanApplication.objects.all().order_by('-applied_date')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    context = {
        'applications': applications,
        'status_choices': LoanApplication.STATUS_CHOICES,
        'current_filter': status_filter,
    }
    
    return render(request, 'app/admin_loan_applications.html', context)

@admin_required
def admin_loan_disbursements(request):
    """Admin view for managing loan disbursements"""
    disbursements = LoanDisbursement.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        disbursements = disbursements.filter(status=status_filter)
    
    context = {
        'disbursements': disbursements,
        'status_choices': LoanDisbursement.STATUS_CHOICES,
        'current_filter': status_filter,
    }
    
    return render(request, 'app/admin_loan_disbursements.html', context)

@admin_required
def admin_emi_tracking(request):
    """Admin view for EMI tracking and management"""
    emi_schedules = EMISchedule.objects.all().order_by('due_date')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        emi_schedules = emi_schedules.filter(status=status_filter)
    
    # Filter overdue EMIs
    overdue_only = request.GET.get('overdue')
    if overdue_only:
        emi_schedules = emi_schedules.filter(
            due_date__lt=timezone.now().date(),
            status__in=['pending', 'partial']
        )
    
    context = {
        'emi_schedules': emi_schedules,
        'status_choices': EMISchedule.STATUS_CHOICES,
        'current_filter': status_filter,
        'overdue_only': overdue_only,
    }
    
    return render(request, 'app/admin_emi_tracking.html', context)

# Loan Type Management Views
@admin_required
def admin_loan_types(request):
    """Admin view for managing loan types"""
    loan_types = LoanType.objects.all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        loan_types = loan_types.filter(is_active=True)
    elif status_filter == 'inactive':
        loan_types = loan_types.filter(is_active=False)
    
    context = {
        'loan_types': loan_types,
        'current_filter': status_filter,
    }
    
    return render(request, 'app/admin_loan_types.html', context)

@admin_required
def admin_add_loan_type(request):
    """Admin view for adding new loan type"""
    if request.method == 'POST':
        form = LoanTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan type created successfully!')
            return redirect('admin_loan_types')
    else:
        form = LoanTypeForm()
    
    return render(request, 'app/admin_loan_type_form.html', {
        'form': form,
        'title': 'Add New Loan Type',
        'action': 'Add'
    })

@admin_required
def admin_edit_loan_type(request, loan_type_id):
    """Admin view for editing loan type"""
    loan_type = get_object_or_404(LoanType, id=loan_type_id)
    
    if request.method == 'POST':
        form = LoanTypeForm(request.POST, instance=loan_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan type updated successfully!')
            return redirect('admin_loan_types')
    else:
        form = LoanTypeForm(instance=loan_type)
    
    return render(request, 'app/admin_loan_type_form.html', {
        'form': form,
        'title': 'Edit Loan Type',
        'action': 'Update',
        'loan_type': loan_type
    })

@admin_required
def admin_delete_loan_type(request, loan_type_id):
    """Admin view for deleting loan type"""
    loan_type = get_object_or_404(LoanType, id=loan_type_id)
    
    if request.method == 'POST':
        # Check if loan type is being used in any applications
        if loan_type.loanapplication_set.exists():
            messages.error(request, 'Cannot delete loan type. It is being used in loan applications.')
        else:
            loan_type.delete()
            messages.success(request, 'Loan type deleted successfully!')
        return redirect('admin_loan_types')
    
    return render(request, 'app/admin_confirm_delete.html', {
        'object': loan_type,
        'object_type': 'Loan Type',
        'return_url': 'admin_loan_types'
    })

# Interest Rate Management Views
@admin_required
def admin_interest_rates(request):
    """Admin view for managing interest rates"""
    interest_rates = InterestRate.objects.select_related('loan_type').all().order_by('loan_type__name', 'duration_months', 'risk_profile')
    
    # Filter by loan type if provided
    loan_type_filter = request.GET.get('loan_type')
    if loan_type_filter:
        interest_rates = interest_rates.filter(loan_type_id=loan_type_filter)
    
    loan_types = LoanType.objects.filter(is_active=True)
    
    context = {
        'interest_rates': interest_rates,
        'loan_types': loan_types,
        'current_filter': loan_type_filter,
    }
    
    return render(request, 'app/admin_interest_rates.html', context)

@admin_required
def admin_add_interest_rate(request):
    """Admin view for adding new interest rate"""
    if request.method == 'POST':
        form = InterestRateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interest rate created successfully!')
            return redirect('admin_interest_rates')
    else:
        form = InterestRateForm()
    
    return render(request, 'app/admin_interest_rate_form.html', {
        'form': form,
        'title': 'Add New Interest Rate',
        'action': 'Add'
    })

@admin_required
def admin_edit_interest_rate(request, interest_rate_id):
    """Admin view for editing interest rate"""
    interest_rate = get_object_or_404(InterestRate, id=interest_rate_id)
    
    if request.method == 'POST':
        form = InterestRateForm(request.POST, instance=interest_rate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interest rate updated successfully!')
            return redirect('admin_interest_rates')
    else:
        form = InterestRateForm(instance=interest_rate)
    
    return render(request, 'app/admin_interest_rate_form.html', {
        'form': form,
        'title': 'Edit Interest Rate',
        'action': 'Update',
        'interest_rate': interest_rate
    })

@admin_required
def admin_delete_interest_rate(request, interest_rate_id):
    """Admin view for deleting interest rate"""
    interest_rate = get_object_or_404(InterestRate, id=interest_rate_id)
    
    if request.method == 'POST':
        interest_rate.delete()
        messages.success(request, 'Interest rate deleted successfully!')
        return redirect('admin_interest_rates')
    
    return render(request, 'app/admin_confirm_delete.html', {
        'object': interest_rate,
        'object_type': 'Interest Rate',
        'return_url': 'admin_interest_rates'
    })

# EMI Calculator View
@admin_required
def admin_emi_calculator(request):
    """Admin view for EMI calculator"""
    calculation_result = None
    
    if request.method == 'POST':
        form = EMICalculatorForm(request.POST)
        if form.is_valid():
            calculation_result = form.calculate_emi()
    else:
        form = EMICalculatorForm()
    
    return render(request, 'app/admin_emi_calculator.html', {
        'form': form,
        'calculation_result': calculation_result
    })

# AJAX view for EMI calculation
@admin_required
def calculate_emi_ajax(request):
    """AJAX endpoint for EMI calculation"""
    if request.method == 'POST':
        form = EMICalculatorForm(request.POST)
        if form.is_valid():
            result = form.calculate_emi()
            return JsonResponse({
                'success': True,
                'emi_amount': float(result['emi_amount']),
                'total_repayment': float(result['total_repayment']),
                'total_interest': float(result['total_interest'])
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Loan Amount Slab Management Views
@admin_required
def admin_loan_amount_slabs(request):
    """Admin view for managing loan amount slabs"""
    slabs = LoanAmountSlab.objects.select_related('loan_type').all().order_by('loan_type__name', 'min_amount')
    
    # Filter by loan type if provided
    loan_type_filter = request.GET.get('loan_type')
    if loan_type_filter:
        slabs = slabs.filter(loan_type_id=loan_type_filter)
    
    loan_types = LoanType.objects.filter(is_active=True)
    
    context = {
        'slabs': slabs,
        'loan_types': loan_types,
        'current_filter': loan_type_filter,
    }
    
    return render(request, 'app/admin_loan_amount_slabs.html', context)

@admin_required
def admin_add_loan_amount_slab(request):
    """Admin view for adding new loan amount slab"""
    if request.method == 'POST':
        form = LoanAmountSlabForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan amount slab created successfully!')
            return redirect('admin_loan_amount_slabs')
    else:
        form = LoanAmountSlabForm()
    
    return render(request, 'app/admin_loan_amount_slab_form.html', {
        'form': form,
        'title': 'Add New Loan Amount Slab',
        'action': 'Add'
    })

@admin_required
def admin_edit_loan_amount_slab(request, slab_id):
    """Admin view for editing loan amount slab"""
    slab = get_object_or_404(LoanAmountSlab, id=slab_id)
    
    if request.method == 'POST':
        form = LoanAmountSlabForm(request.POST, instance=slab)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan amount slab updated successfully!')
            return redirect('admin_loan_amount_slabs')
    else:
        form = LoanAmountSlabForm(instance=slab)
    
    return render(request, 'app/admin_loan_amount_slab_form.html', {
        'form': form,
        'title': 'Edit Loan Amount Slab',
        'action': 'Update',
        'slab': slab
    })

@admin_required
def admin_delete_loan_amount_slab(request, slab_id):
    """Admin view for deleting loan amount slab"""
    slab = get_object_or_404(LoanAmountSlab, id=slab_id)
    
    if request.method == 'POST':
        # Check if slab is being used in any EMI configurations
        if slab.emi_configurations.exists():
            messages.error(request, 'Cannot delete loan amount slab. It is being used in EMI configurations.')
        else:
            slab.delete()
            messages.success(request, 'Loan amount slab deleted successfully!')
        return redirect('admin_loan_amount_slabs')
    
    return render(request, 'app/admin_confirm_delete.html', {
        'object': slab,
        'object_type': 'Loan Amount Slab',
        'return_url': 'admin_loan_amount_slabs'
    })

# EMI Configuration Management Views
@admin_required
def admin_emi_configurations(request):
    """Admin view for managing EMI configurations"""
    configurations = EMIConfiguration.objects.select_related(
        'loan_type', 'amount_slab', 'interest_rate'
    ).all().order_by('loan_type__name', 'tenure_months')
    
    # Filter by loan type if provided
    loan_type_filter = request.GET.get('loan_type')
    if loan_type_filter:
        configurations = configurations.filter(loan_type_id=loan_type_filter)
    
    loan_types = LoanType.objects.filter(is_active=True)
    
    context = {
        'configurations': configurations,
        'loan_types': loan_types,
        'current_filter': loan_type_filter,
    }
    
    return render(request, 'app/admin_emi_configurations.html', context)

@admin_required
def admin_add_emi_configuration(request):
    """Admin view for adding new EMI configuration"""
    if request.method == 'POST':
        form = EMIConfigurationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'EMI configuration created successfully!')
            return redirect('admin_emi_configurations')
    else:
        form = EMIConfigurationForm()
    
    return render(request, 'app/admin_emi_configuration_form.html', {
        'form': form,
        'title': 'Add New EMI Configuration',
        'action': 'Add'
    })

@admin_required
def admin_edit_emi_configuration(request, config_id):
    """Admin view for editing EMI configuration"""
    config = get_object_or_404(EMIConfiguration, id=config_id)
    
    if request.method == 'POST':
        form = EMIConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'EMI configuration updated successfully!')
            return redirect('admin_emi_configurations')
    else:
        form = EMIConfigurationForm(instance=config)
    
    return render(request, 'app/admin_emi_configuration_form.html', {
        'form': form,
        'title': 'Edit EMI Configuration',
        'action': 'Update',
        'config': config
    })

@admin_required
def admin_delete_emi_configuration(request, config_id):
    """Admin view for deleting EMI configuration"""
    config = get_object_or_404(EMIConfiguration, id=config_id)
    
    if request.method == 'POST':
        config.delete()
        messages.success(request, 'EMI configuration deleted successfully!')
        return redirect('admin_emi_configurations')
    
    return render(request, 'app/admin_confirm_delete.html', {
        'object': config,
        'object_type': 'EMI Configuration',
        'return_url': 'admin_emi_configurations'
    })

# Advanced EMI Calculator View
@admin_required
def admin_advanced_emi_calculator(request):
    """Admin view for advanced EMI calculator with loan types and amount slabs"""
    calculation_result = None
    
    if request.method == 'POST':
        form = EMICalculatorAdvancedForm(request.POST)
        if form.is_valid():
            calculation_result = form.calculate_emi()
    else:
        form = EMICalculatorAdvancedForm()
    
    return render(request, 'app/admin_advanced_emi_calculator.html', {
        'form': form,
        'calculation_result': calculation_result
    })

# AJAX view for getting amount slabs and interest rates based on loan type
@admin_required
def get_loan_type_data(request):
    """AJAX endpoint to get amount slabs and interest rates for a loan type"""
    if request.method == 'GET':
        loan_type_id = request.GET.get('loan_type_id')
        
        if loan_type_id:
            try:
                amount_slabs = LoanAmountSlab.objects.filter(
                    loan_type_id=loan_type_id, is_active=True
                ).values('id', 'slab_name', 'min_amount', 'max_amount')
                
                interest_rates = InterestRate.objects.filter(
                    loan_type_id=loan_type_id, is_active=True
                ).values('id', 'annual_rate', 'duration_months', 'risk_profile')
                
                return JsonResponse({
                    'success': True,
                    'amount_slabs': list(amount_slabs),
                    'interest_rates': list(interest_rates)
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
