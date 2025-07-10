from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils import timezone


class Task(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('pending_input', 'Pending Input'),
        ('deferred', 'Deferred'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    TYPE_CHOICES = [
        ('call', 'Call'),
        ('meeting', 'Meeting'),
        ('email', 'Email'),
        ('task', 'Task'),
        ('demo', 'Demo'),
        ('other', 'Other'),
    ]
    
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    task_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='task')
    
    due_date = models.DateTimeField()
    start_date = models.DateTimeField(null=True, blank=True)
    
    description = models.TextField(blank=True)
    
    # Generic relation to link to any model (Account, Contact, Lead, Opportunity)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_to = GenericForeignKey('content_type', 'object_id')
    
    # Tracking
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['due_date']
    
    def __str__(self):
        return self.subject
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now() and self.status != 'completed'
    
    def get_absolute_url(self):
        return reverse('tasks:detail', kwargs={'pk': self.pk})


class Call(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_answer', 'No Answer'),
        ('busy', 'Busy'),
        ('left_message', 'Left Message'),
    ]
    
    CALL_TYPE_CHOICES = [
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ]
    
    CALL_RESULT_CHOICES = [
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('callback_requested', 'Callback Requested'),
        ('voicemail', 'Voicemail'),
        ('busy', 'Busy'),
        ('no_answer', 'No Answer'),
        ('wrong_number', 'Wrong Number'),
        ('meeting_scheduled', 'Meeting Scheduled'),
        ('sale_closed', 'Sale Closed'),
    ]
    
    subject = models.CharField(max_length=200)
    call_type = models.CharField(max_length=10, choices=CALL_TYPE_CHOICES, default='outbound')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='planned')
    call_result = models.CharField(max_length=20, choices=CALL_RESULT_CHOICES, blank=True)
    
    # Phone information
    phone_number = models.CharField(max_length=20)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in minutes")
    
    # Timing
    scheduled_datetime = models.DateTimeField()
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    
    # Content
    description = models.TextField(blank=True, help_text="Call agenda or notes")
    call_notes = models.TextField(blank=True, help_text="Notes taken during/after the call")
    
    # Related objects
    related_account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, null=True, blank=True, related_name='calls')
    related_contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, null=True, blank=True, related_name='calls')
    related_lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE, null=True, blank=True, related_name='calls')
    related_opportunity = models.ForeignKey('opportunities.Opportunity', on_delete=models.CASCADE, null=True, blank=True, related_name='calls')
    
    # Tracking
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_calls')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_calls')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_datetime']
    
    def __str__(self):
        return f"{self.subject} - {self.get_call_type_display()}"
    
    def get_absolute_url(self):
        return reverse('tasks:call_detail', kwargs={'pk': self.pk})
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def is_overdue(self):
        return self.scheduled_datetime < timezone.now() and not self.is_completed
    
    @property
    def related_object(self):
        """Return the main related object for this call"""
        if self.related_contact:
            return self.related_contact
        elif self.related_lead:
            return self.related_lead
        elif self.related_account:
            return self.related_account
        elif self.related_opportunity:
            return self.related_opportunity
        return None


class Meeting(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('postponed', 'Postponed'),
        ('no_show', 'No Show'),
    ]
    
    MEETING_TYPE_CHOICES = [
        ('sales_meeting', 'Sales Meeting'),
        ('demo', 'Product Demo'),
        ('follow_up', 'Follow-up Meeting'),
        ('negotiation', 'Negotiation'),
        ('kickoff', 'Project Kickoff'),
        ('review', 'Review Meeting'),
        ('training', 'Training'),
        ('other', 'Other'),
    ]
    
    subject = models.CharField(max_length=200)
    meeting_type = models.CharField(max_length=15, choices=MEETING_TYPE_CHOICES, default='sales_meeting')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='planned')
    
    # Location and logistics
    location = models.CharField(max_length=200, blank=True, help_text="Meeting location or 'Online'")
    meeting_url = models.URLField(blank=True, help_text="Video conference URL")
    
    # Timing
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Planned duration in minutes")
    
    # Content
    agenda = models.TextField(blank=True, help_text="Meeting agenda")
    meeting_notes = models.TextField(blank=True, help_text="Notes taken during/after the meeting")
    outcome = models.TextField(blank=True, help_text="Meeting outcome and next steps")
    
    # Attendees (we'll track the primary contact, but could extend this)
    primary_contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, null=True, blank=True, related_name='primary_meetings')
    attendees_notes = models.TextField(blank=True, help_text="List of attendees")
    
    # Related objects
    related_account = models.ForeignKey('accounts.Account', on_delete=models.CASCADE, null=True, blank=True, related_name='meetings')
    related_contact = models.ForeignKey('contacts.Contact', on_delete=models.CASCADE, null=True, blank=True, related_name='meetings')
    related_lead = models.ForeignKey('leads.Lead', on_delete=models.CASCADE, null=True, blank=True, related_name='meetings')
    related_opportunity = models.ForeignKey('opportunities.Opportunity', on_delete=models.CASCADE, null=True, blank=True, related_name='meetings')
    
    # Tracking
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_meetings')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_meetings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_datetime']
    
    def __str__(self):
        return f"{self.subject} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    def get_absolute_url(self):
        return reverse('tasks:meeting_detail', kwargs={'pk': self.pk})
    
    @property
    def is_completed(self):
        return self.status == 'completed'
    
    @property
    def is_overdue(self):
        return self.start_datetime < timezone.now() and not self.is_completed
    
    @property
    def related_object(self):
        """Return the main related object for this meeting"""
        if self.related_contact:
            return self.related_contact
        elif self.related_lead:
            return self.related_lead
        elif self.related_account:
            return self.related_account
        elif self.related_opportunity:
            return self.related_opportunity
        return None
