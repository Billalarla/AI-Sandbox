from django import forms
from django.contrib.auth.models import User
from .models import Lead


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['salutation', 'first_name', 'last_name', 'title', 'company', 'industry', 'website',
                  'email', 'phone', 'mobile', 'fax', 'street', 'city', 'state',
                  'postal_code', 'country', 'lead_source', 'status', 'annual_revenue', 'employees',
                  'estimated_value', 'funnel_stage', 'lead_score', 'do_not_call', 'email_opt_out', 
                  'description', 'assigned_to']
        widgets = {
            'salutation': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job title'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name'
            }),
            'industry': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter industry'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter website URL'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter mobile number'
            }),
            'fax': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter fax number'
            }),
            'street': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter state/province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter postal code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter country'
            }),
            'lead_source': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'annual_revenue': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter annual revenue'
            }),
            'employees': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Enter number of employees'
            }),
            'estimated_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter estimated value'
            }),
            'funnel_stage': forms.Select(attrs={'class': 'form-select'}),
            'lead_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'placeholder': 'Enter lead score (0-100)'
            }),
            'do_not_call': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_opt_out': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter lead description'
            }),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Select assignee"
