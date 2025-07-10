from django.contrib import admin
from .models import Task, Call, Meeting


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['subject', 'status', 'priority', 'task_type', 'assigned_to', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'task_type', 'assigned_to']
    search_fields = ['subject', 'description']
    date_hierarchy = 'due_date'
    ordering = ['-created_at']


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ['subject', 'call_type', 'status', 'phone_number', 'assigned_to', 'scheduled_datetime']
    list_filter = ['call_type', 'status', 'call_result', 'assigned_to']
    search_fields = ['subject', 'phone_number', 'call_notes']
    date_hierarchy = 'scheduled_datetime'
    ordering = ['-scheduled_datetime']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['subject', 'meeting_type', 'status', 'location', 'assigned_to', 'start_datetime']
    list_filter = ['meeting_type', 'status', 'assigned_to']
    search_fields = ['subject', 'location', 'agenda']
    date_hierarchy = 'start_datetime'
    ordering = ['-start_datetime']
