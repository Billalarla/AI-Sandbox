from django import forms
from django.contrib.auth.models import User
from .models import Opportunity
from accounts.models import Account
from contacts.models import Contact


class OpportunityForm(forms.ModelForm):
    class Meta:
        model = Opportunity
        fields = ['name', 'account', 'contact', 'amount', 'sales_stage', 'probability', 'expected_close_date',
                  'opportunity_type', 'lead_source', 'next_step', 'description', 'assigned_to']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter opportunity name'
            }),
            'account': forms.Select(attrs={'class': 'form-select'}),
            'contact': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter amount'
            }),
            'sales_stage': forms.Select(attrs={'class': 'form-select'}),
            'probability': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'placeholder': 'Enter probability (0-100%)'
            }),
            'expected_close_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'opportunity_type': forms.Select(attrs={'class': 'form-select'}),
            'lead_source': forms.Select(attrs={'class': 'form-select'}),
            'next_step': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter next step'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter opportunity description'
            }),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Select assignee"
        self.fields['account'].queryset = Account.objects.all()
        self.fields['contact'].queryset = Contact.objects.all()
        self.fields['contact'].empty_label = "Select contact (optional)"
