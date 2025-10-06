from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import LoanType, InterestRate, LoanAmountSlab, EMIConfiguration
from decimal import Decimal

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class AdminSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=True)
    admin_code = forms.CharField(max_length=20, required=True, help_text="Enter admin authorization code")
    
    # Additional admin fields
    employee_id = forms.CharField(max_length=20, required=True)
    department = forms.CharField(max_length=50, required=True)
    designation = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'employee_id', 'department', 'designation', 'admin_code', 'password1', 'password2')

    def clean_admin_code(self):
        admin_code = self.cleaned_data.get('admin_code')
        # You can set a secret admin code here
        valid_admin_codes = ['ADMIN2024', 'SECUREBANK', 'MASTERADMIN']
        if admin_code not in valid_admin_codes:
            raise forms.ValidationError("Invalid admin authorization code.")
        return admin_code

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = True  # Make admin a staff member
        user.is_superuser = True  # Give superuser privileges
        if commit:
            user.save()
        return user

class LoanTypeForm(forms.ModelForm):
    class Meta:
        model = LoanType
        fields = ['name', 'description', 'eligibility_rules', 'min_amount', 'max_amount', 'allow_custom_amount', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'eligibility_rules': forms.Textarea(attrs={'rows': 3}),
            'min_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'max_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_amount = cleaned_data.get('min_amount')
        max_amount = cleaned_data.get('max_amount')
        
        if min_amount and max_amount and min_amount >= max_amount:
            raise forms.ValidationError("Maximum amount must be greater than minimum amount.")
        
        return cleaned_data

class InterestRateForm(forms.ModelForm):
    class Meta:
        model = InterestRate
        fields = ['loan_type', 'duration_months', 'risk_profile', 'annual_rate', 'is_active']
        widgets = {
            'annual_rate': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'max': '50.00'}),
        }
    
    def clean_annual_rate(self):
        annual_rate = self.cleaned_data.get('annual_rate')
        if annual_rate and (annual_rate < 0.01 or annual_rate > 50.00):
            raise forms.ValidationError("Annual rate must be between 0.01% and 50.00%.")
        return annual_rate

class EMICalculatorForm(forms.Form):
    loan_amount = forms.DecimalField(
        max_digits=12, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'class': 'form-control'})
    )
    annual_rate = forms.DecimalField(
        max_digits=5, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'max': '50.00', 'class': 'form-control'})
    )
    tenure_months = forms.IntegerField(
        widget=forms.NumberInput(attrs={'min': '1', 'max': '60', 'class': 'form-control'})
    )
    
    def calculate_emi(self):
        """Calculate EMI using standard loan formula"""
        if not self.is_valid():
            return None
            
        principal = self.cleaned_data['loan_amount']
        rate = self.cleaned_data['annual_rate'] / 100 / 12  # Monthly rate
        months = self.cleaned_data['tenure_months']
        
        if rate == 0:
            emi_amount = principal / months
        else:
            emi_amount = principal * (rate * (1 + rate) ** months) / ((1 + rate) ** months - 1)
        
        total_repayment = emi_amount * months
        total_interest = total_repayment - principal
        
        return {
            'emi_amount': round(emi_amount, 2),
            'total_repayment': round(total_repayment, 2),
            'total_interest': round(total_interest, 2),
            'principal': principal,
            'rate': self.cleaned_data['annual_rate'],
            'months': months
        }

class LoanAmountSlabForm(forms.ModelForm):
    class Meta:
        model = LoanAmountSlab
        fields = ['loan_type', 'slab_name', 'min_amount', 'max_amount', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'min_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'max_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_amount = cleaned_data.get('min_amount')
        max_amount = cleaned_data.get('max_amount')
        loan_type = cleaned_data.get('loan_type')
        
        if min_amount and max_amount and min_amount >= max_amount:
            raise forms.ValidationError("Maximum amount must be greater than minimum amount.")
        
        # Check for overlapping slabs
        if loan_type and min_amount and max_amount:
            existing_slabs = LoanAmountSlab.objects.filter(
                loan_type=loan_type,
                is_active=True
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            for slab in existing_slabs:
                if (min_amount <= slab.max_amount and max_amount >= slab.min_amount):
                    raise forms.ValidationError(
                        f"This amount range overlaps with existing slab '{slab.slab_name}' "
                        f"(₹{slab.min_amount} - ₹{slab.max_amount})"
                    )
        
        return cleaned_data

class EMIConfigurationForm(forms.ModelForm):
    class Meta:
        model = EMIConfiguration
        fields = ['loan_type', 'amount_slab', 'interest_rate', 'frequency', 'tenure_months', 'is_active']
        widgets = {
            'tenure_months': forms.NumberInput(attrs={'min': '1', 'max': '60'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter interest rates and amount slabs based on selected loan type
        if 'loan_type' in self.data:
            try:
                loan_type_id = int(self.data.get('loan_type'))
                self.fields['interest_rate'].queryset = InterestRate.objects.filter(
                    loan_type_id=loan_type_id, is_active=True
                )
                self.fields['amount_slab'].queryset = LoanAmountSlab.objects.filter(
                    loan_type_id=loan_type_id, is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['interest_rate'].queryset = self.instance.loan_type.interestrate_set.filter(is_active=True)
            self.fields['amount_slab'].queryset = self.instance.loan_type.amount_slabs.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        loan_type = cleaned_data.get('loan_type')
        amount_slab = cleaned_data.get('amount_slab')
        interest_rate = cleaned_data.get('interest_rate')
        tenure_months = cleaned_data.get('tenure_months')
        
        # Validate that interest rate matches loan type
        if loan_type and interest_rate and interest_rate.loan_type != loan_type:
            raise forms.ValidationError("Selected interest rate does not match the loan type.")
        
        # Validate that amount slab matches loan type
        if loan_type and amount_slab and amount_slab.loan_type != loan_type:
            raise forms.ValidationError("Selected amount slab does not match the loan type.")
        
        # Check for duplicate configuration
        if loan_type and amount_slab and interest_rate and tenure_months:
            existing = EMIConfiguration.objects.filter(
                loan_type=loan_type,
                amount_slab=amount_slab,
                interest_rate=interest_rate,
                tenure_months=tenure_months,
                frequency=cleaned_data.get('frequency', 'monthly')
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            
            if existing.exists():
                raise forms.ValidationError("An EMI configuration with these parameters already exists.")
        
        return cleaned_data

class EMICalculatorAdvancedForm(forms.Form):
    """Advanced EMI calculator form with loan type and amount slab selection"""
    loan_type = forms.ModelChoiceField(
        queryset=LoanType.objects.filter(is_active=True),
        empty_label="Select Loan Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    amount_slab = forms.ModelChoiceField(
        queryset=LoanAmountSlab.objects.none(),
        empty_label="Select Amount Slab (Optional)",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    custom_amount = forms.DecimalField(
        max_digits=12, 
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'class': 'form-control'})
    )
    interest_rate = forms.ModelChoiceField(
        queryset=InterestRate.objects.none(),
        empty_label="Select Interest Rate",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tenure_months = forms.IntegerField(
        widget=forms.NumberInput(attrs={'min': '1', 'max': '60', 'class': 'form-control'})
    )
    frequency = forms.ChoiceField(
        choices=EMIConfiguration.FREQUENCY_CHOICES,
        initial='monthly',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter interest rates and amount slabs based on selected loan type
        if 'loan_type' in self.data:
            try:
                loan_type_id = int(self.data.get('loan_type'))
                self.fields['interest_rate'].queryset = InterestRate.objects.filter(
                    loan_type_id=loan_type_id, is_active=True
                )
                self.fields['amount_slab'].queryset = LoanAmountSlab.objects.filter(
                    loan_type_id=loan_type_id, is_active=True
                )
            except (ValueError, TypeError):
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        amount_slab = cleaned_data.get('amount_slab')
        custom_amount = cleaned_data.get('custom_amount')
        
        if not amount_slab and not custom_amount:
            raise forms.ValidationError("Please select an amount slab or enter a custom amount.")
        
        if amount_slab and custom_amount:
            if not (amount_slab.min_amount <= custom_amount <= amount_slab.max_amount):
                raise forms.ValidationError(
                    f"Custom amount must be between ₹{amount_slab.min_amount} and ₹{amount_slab.max_amount} for the selected slab."
                )
        
        return cleaned_data
    
    def calculate_emi(self):
        """Calculate EMI using the selected parameters"""
        if not self.is_valid():
            return None
        
        # Determine loan amount
        if self.cleaned_data.get('custom_amount'):
            loan_amount = self.cleaned_data['custom_amount']
        elif self.cleaned_data.get('amount_slab'):
            loan_amount = self.cleaned_data['amount_slab'].min_amount
        else:
            return None
        
        # Get interest rate and calculate monthly rate
        annual_rate = self.cleaned_data['interest_rate'].annual_rate
        monthly_rate = annual_rate / 100 / 12
        months = self.cleaned_data['tenure_months']
        frequency = self.cleaned_data['frequency']
        
        # Calculate EMI using standard formula
        if monthly_rate == 0:
            emi_amount = loan_amount / months
        else:
            emi_amount = loan_amount * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
        
        # Adjust for frequency
        if frequency == 'quarterly':
            emi_amount = emi_amount * 3
        elif frequency == 'yearly':
            emi_amount = emi_amount * 12
        
        total_repayment = emi_amount * months
        total_interest = total_repayment - loan_amount
        
        return {
            'emi_amount': round(emi_amount, 2),
            'total_repayment': round(total_repayment, 2),
            'total_interest': round(total_interest, 2),
            'loan_amount': loan_amount,
            'annual_rate': annual_rate,
            'monthly_rate': monthly_rate,
            'months': months,
            'frequency': frequency
        }
