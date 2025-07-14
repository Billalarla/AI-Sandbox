from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone


class CalendarView(models.Model):
    """User-specific calendar view preferences"""
    
    VIEW_CHOICES = [
        ('dayGridMonth', 'Month View'),
        ('timeGridWeek', 'Week View'),
        ('timeGridDay', 'Day View'),
        ('listWeek', 'List View'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='calendar_preferences')
    default_view = models.CharField(max_length=20, choices=VIEW_CHOICES, default='dayGridMonth')
    show_weekends = models.BooleanField(default=True)
    start_time = models.TimeField(default='08:00')  # Business hours start
    end_time = models.TimeField(default='18:00')    # Business hours end
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Filter preferences
    default_event_types = models.JSONField(default=list)  # ['tasks', 'calls', 'meetings']
    default_account_filter = models.ForeignKey(
        'accounts.Account', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Calendar View Preference"
        verbose_name_plural = "Calendar View Preferences"
    
    def __str__(self):
        return f"{self.user.username}'s Calendar Preferences"


class CalendarEvent(models.Model):
    """Custom calendar events not tied to tasks/calls/meetings"""
    
    EVENT_TYPES = [
        ('appointment', 'Appointment'),
        ('reminder', 'Reminder'),
        ('holiday', 'Holiday'),
        ('personal', 'Personal Event'),
        ('company', 'Company Event'),
        ('training', 'Training'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('tentative', 'Tentative'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    is_all_day = models.BooleanField(default=False)
    
    # Location/URL
    location = models.CharField(max_length=255, blank=True)
    meeting_url = models.URLField(blank=True)
    
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_calendar_events')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_calendar_events')
    
    # Generic relationship to any model (account, contact, lead, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Recurrence (simple implementation)
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.JSONField(null=True, blank=True)  # Store iCal RRULE data
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Calendar Event"
        verbose_name_plural = "Calendar Events"
        ordering = ['start_datetime']
    
    def __str__(self):
        return f"{self.title} - {self.start_datetime.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def duration_minutes(self):
        """Calculate event duration in minutes"""
        if self.end_datetime:
            delta = self.end_datetime - self.start_datetime
            return int(delta.total_seconds() / 60)
        return 60  # Default 1 hour
    
    def get_absolute_url(self):
        return f"/calendar/events/{self.id}/"


class CalendarShare(models.Model):
    """Calendar sharing permissions between users"""
    
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('edit', 'View and Edit'),
        ('admin', 'Full Access'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_calendars')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accessible_calendars')
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    
    # Optional: share specific event types only
    include_tasks = models.BooleanField(default=True)
    include_calls = models.BooleanField(default=True)
    include_meetings = models.BooleanField(default=True)
    include_custom_events = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Calendar Share"
        verbose_name_plural = "Calendar Shares"
        unique_together = ['owner', 'shared_with']
    
    def __str__(self):
        return f"{self.owner.username} shared with {self.shared_with.username} ({self.permission})"


class CalendarNotification(models.Model):
    """Event reminder notifications"""
    
    NOTIFICATION_TYPES = [
        ('email', 'Email'),
        ('browser', 'Browser Notification'),
        ('sms', 'SMS'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Generic relationship to any event type
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    event = GenericForeignKey('content_type', 'object_id')
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    minutes_before = models.PositiveIntegerField(default=15)  # Remind X minutes before event
    
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Calendar Notification"
        verbose_name_plural = "Calendar Notifications"
        unique_together = ['user', 'content_type', 'object_id', 'notification_type']
    
    def __str__(self):
        return f"Reminder for {self.user.username} - {self.minutes_before}min before"


# Create your models here.
