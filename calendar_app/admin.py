from django.contrib import admin
from .models import CalendarView, CalendarEvent, CalendarShare, CalendarNotification


@admin.register(CalendarView)
class CalendarViewAdmin(admin.ModelAdmin):
    list_display = ['user', 'default_view', 'show_weekends', 'start_time', 'end_time', 'updated_at']
    list_filter = ['default_view', 'show_weekends', 'timezone']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('View Preferences', {
            'fields': ('default_view', 'show_weekends', 'start_time', 'end_time', 'timezone')
        }),
        ('Default Filters', {
            'fields': ('default_event_types', 'default_account_filter'),
            'description': 'Default filters that will be applied when user opens calendar'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'status', 'start_datetime', 'end_datetime', 'assigned_to', 'created_by']
    list_filter = ['event_type', 'status', 'is_all_day', 'is_recurring', 'created_at']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at', 'duration_minutes']
    date_hierarchy = 'start_datetime'
    
    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'event_type', 'status')
        }),
        ('Date & Time', {
            'fields': ('start_datetime', 'end_datetime', 'is_all_day', 'duration_minutes')
        }),
        ('Location', {
            'fields': ('location', 'meeting_url')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',),
            'description': 'Link this event to an account, contact, lead, etc.'
        }),
        ('Recurrence', {
            'fields': ('is_recurring', 'recurrence_rule'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def duration_minutes(self, obj):
        return f"{obj.duration_minutes} minutes"
    duration_minutes.short_description = "Duration"


@admin.register(CalendarShare)
class CalendarShareAdmin(admin.ModelAdmin):
    list_display = ['owner', 'shared_with', 'permission', 'include_tasks', 'include_calls', 'include_meetings', 'created_at']
    list_filter = ['permission', 'include_tasks', 'include_calls', 'include_meetings', 'created_at']
    search_fields = ['owner__username', 'shared_with__username']
    
    fieldsets = (
        ('Sharing Details', {
            'fields': ('owner', 'shared_with', 'permission')
        }),
        ('Event Type Permissions', {
            'fields': ('include_tasks', 'include_calls', 'include_meetings', 'include_custom_events'),
            'description': 'Which types of events the shared user can see'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(CalendarNotification)
class CalendarNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'minutes_before', 'is_sent', 'sent_at', 'created_at']
    list_filter = ['notification_type', 'is_sent', 'minutes_before', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['sent_at', 'created_at']
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'notification_type', 'minutes_before')
        }),
        ('Event Reference', {
            'fields': ('content_type', 'object_id'),
            'description': 'The event this notification is for'
        }),
        ('Status', {
            'fields': ('is_sent', 'sent_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


# Register your models here.
