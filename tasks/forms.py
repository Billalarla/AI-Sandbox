from django import forms
from django.contrib.auth.models import User
from .models import Task, Call, Meeting


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['subject', 'status', 'priority', 'task_type', 'due_date', 'start_date', 'description', 'assigned_to']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task subject'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'task_type': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter task description'
            }),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Select assignee"


class CallForm(forms.ModelForm):
    class Meta:
        model = Call
        fields = ['subject', 'call_type', 'status', 'phone_number', 'scheduled_datetime', 'description', 
                  'related_account', 'related_contact', 'related_lead', 'related_opportunity', 'assigned_to']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter call subject'
            }),
            'call_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'scheduled_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter call description'
            }),
            'related_account': forms.Select(attrs={'class': 'form-select'}),
            'related_contact': forms.Select(attrs={'class': 'form-select'}),
            'related_lead': forms.Select(attrs={'class': 'form-select'}),
            'related_opportunity': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Select assignee"
        self.fields['related_account'].empty_label = "Select account (optional)"
        self.fields['related_contact'].empty_label = "Select contact (optional)"
        self.fields['related_lead'].empty_label = "Select lead (optional)"
        self.fields['related_opportunity'].empty_label = "Select opportunity (optional)"


class CallUpdateForm(forms.ModelForm):
    class Meta:
        model = Call
        fields = ['subject', 'call_type', 'status', 'call_result', 'phone_number', 'scheduled_datetime', 
                  'actual_start_time', 'actual_end_time', 'duration_minutes', 'description', 'call_notes',
                  'related_account', 'related_contact', 'related_lead', 'related_opportunity', 'assigned_to']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter call subject'
            }),
            'call_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'call_result': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'scheduled_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'actual_start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'actual_end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Duration in minutes'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter call description'
            }),
            'call_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter call notes'
            }),
            'related_account': forms.Select(attrs={'class': 'form-select'}),
            'related_contact': forms.Select(attrs={'class': 'form-select'}),
            'related_lead': forms.Select(attrs={'class': 'form-select'}),
            'related_opportunity': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Select assignee"
        self.fields['related_account'].empty_label = "Select account (optional)"
        self.fields['related_contact'].empty_label = "Select contact (optional)"
        self.fields['related_lead'].empty_label = "Select lead (optional)"
        self.fields['related_opportunity'].empty_label = "Select opportunity (optional)"


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['subject', 'meeting_type', 'status', 'location', 'meeting_url', 'start_datetime', 'end_datetime',
                  'agenda', 'primary_contact', 'attendees_notes', 'related_account', 'related_contact', 
                  'related_lead', 'related_opportunity', 'assigned_to']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meeting subject'
            }),
            'meeting_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meeting location'
            }),
            'meeting_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meeting URL (for virtual meetings)'
            }),
            'start_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'agenda': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter meeting agenda'
            }),
            'primary_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter primary contact name'
            }),
            'attendees_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter attendees notes'
            }),
            'related_account': forms.Select(attrs={'class': 'form-select'}),
            'related_contact': forms.Select(attrs={'class': 'form-select'}),
            'related_lead': forms.Select(attrs={'class': 'form-select'}),
            'related_opportunity': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Select assignee"
        self.fields['related_account'].empty_label = "Select account (optional)"
        self.fields['related_contact'].empty_label = "Select contact (optional)"
        self.fields['related_lead'].empty_label = "Select lead (optional)"
        self.fields['related_opportunity'].empty_label = "Select opportunity (optional)"


class MeetingUpdateForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['subject', 'meeting_type', 'status', 'location', 'meeting_url', 'start_datetime', 'end_datetime',
                  'duration_minutes', 'agenda', 'meeting_notes', 'outcome', 'primary_contact', 'attendees_notes',
                  'related_account', 'related_contact', 'related_lead', 'related_opportunity', 'assigned_to']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meeting subject'
            }),
            'meeting_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meeting location'
            }),
            'meeting_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meeting URL (for virtual meetings)'
            }),
            'start_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Duration in minutes'
            }),
            'agenda': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter meeting agenda'
            }),
            'meeting_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter meeting notes'
            }),
            'outcome': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter meeting outcome'
            }),
            'primary_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter primary contact name'
            }),
            'attendees_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter attendees notes'
            }),
            'related_account': forms.Select(attrs={'class': 'form-select'}),
            'related_contact': forms.Select(attrs={'class': 'form-select'}),
            'related_lead': forms.Select(attrs={'class': 'form-select'}),
            'related_opportunity': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_to'].empty_label = "Select assignee"
        self.fields['related_account'].empty_label = "Select account (optional)"
        self.fields['related_contact'].empty_label = "Select contact (optional)"
        self.fields['related_lead'].empty_label = "Select lead (optional)"
        self.fields['related_opportunity'].empty_label = "Select opportunity (optional)"
