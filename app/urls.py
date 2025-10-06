from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.landing_page, name='landing'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('index/', views.index_view, name='index'),
    path('logout/', views.logout_view, name='logout'),
    
    # Bank Portal Pages
    path('apply-loan/', views.apply_loan_view, name='apply_loan'),
    path('loan-plans/', views.loan_plans_view, name='loan_plans'),
    path('emi-calculator/', views.emi_calculator_view, name='emi_calculator'),
    path('my-applications/', views.my_applications_view, name='my_applications'),
    path('account-services/', views.account_services_view, name='account_services'),
    path('support/', views.support_view, name='support'),
    path('about-us/', views.about_us_view, name='about_us'),
    path('contact-us/', views.contact_us_view, name='contact_us'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions_view, name='terms_conditions'),
    
    # Admin pages
    path('admin/signup/', views.admin_signup_view, name='admin_signup'),
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/banking-portal/', views.admin_banking_portal, name='admin_banking_portal'),
    path('admin/user-management/', views.admin_user_management, name='admin_user_management'),
    path('admin/system-settings/', views.admin_system_settings, name='admin_system_settings'),
    path('admin/applications/', views.admin_loan_applications, name='admin_loan_applications'),
    path('admin/disbursements/', views.admin_loan_disbursements, name='admin_loan_disbursements'),
    path('admin/emi-tracking/', views.admin_emi_tracking, name='admin_emi_tracking'),
    
    # Loan Type Management
    path('admin/loan-types/', views.admin_loan_types, name='admin_loan_types'),
    path('admin/loan-types/add/', views.admin_add_loan_type, name='admin_add_loan_type'),
    path('admin/loan-types/edit/<int:loan_type_id>/', views.admin_edit_loan_type, name='admin_edit_loan_type'),
    path('admin/loan-types/delete/<int:loan_type_id>/', views.admin_delete_loan_type, name='admin_delete_loan_type'),
    
    # Interest Rate Management
    path('admin/interest-rates/', views.admin_interest_rates, name='admin_interest_rates'),
    path('admin/interest-rates/add/', views.admin_add_interest_rate, name='admin_add_interest_rate'),
    path('admin/interest-rates/edit/<int:interest_rate_id>/', views.admin_edit_interest_rate, name='admin_edit_interest_rate'),
    path('admin/interest-rates/delete/<int:interest_rate_id>/', views.admin_delete_interest_rate, name='admin_delete_interest_rate'),
    
    # EMI Calculator
    path('admin/emi-calculator/', views.admin_emi_calculator, name='admin_emi_calculator'),
    path('admin/calculate-emi/', views.calculate_emi_ajax, name='calculate_emi_ajax'),
    
    # Loan Amount Slab Management
    path('admin/loan-amount-slabs/', views.admin_loan_amount_slabs, name='admin_loan_amount_slabs'),
    path('admin/loan-amount-slabs/add/', views.admin_add_loan_amount_slab, name='admin_add_loan_amount_slab'),
    path('admin/loan-amount-slabs/edit/<int:slab_id>/', views.admin_edit_loan_amount_slab, name='admin_edit_loan_amount_slab'),
    path('admin/loan-amount-slabs/delete/<int:slab_id>/', views.admin_delete_loan_amount_slab, name='admin_delete_loan_amount_slab'),
    
    # EMI Configuration Management
    path('admin/emi-configurations/', views.admin_emi_configurations, name='admin_emi_configurations'),
    path('admin/emi-configurations/add/', views.admin_add_emi_configuration, name='admin_add_emi_configuration'),
    path('admin/emi-configurations/edit/<int:config_id>/', views.admin_edit_emi_configuration, name='admin_edit_emi_configuration'),
    path('admin/emi-configurations/delete/<int:config_id>/', views.admin_delete_emi_configuration, name='admin_delete_emi_configuration'),
    
    # Advanced EMI Calculator
    path('admin/advanced-emi-calculator/', views.admin_advanced_emi_calculator, name='admin_advanced_emi_calculator'),
    path('admin/get-loan-type-data/', views.get_loan_type_data, name='get_loan_type_data'),
]
