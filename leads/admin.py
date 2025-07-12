from django.contrib import admin
from .models import Lead, FunnelStageHistory


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'company', 'email', 'funnel_stage', 'lead_score', 'status', 'created_at']
    list_filter = ['funnel_stage', 'status', 'lead_source', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'company']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('salutation', 'first_name', 'last_name', 'title', 'company')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'mobile', 'fax', 'website')
        }),
        ('Address', {
            'fields': ('street', 'city', 'state', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Lead Information', {
            'fields': ('lead_source', 'status', 'industry', 'annual_revenue', 'employees')
        }),
        ('Funnel Tracking', {
            'fields': ('funnel_stage', 'lead_score', 'estimated_value'),
            'classes': ('wide',)
        }),
        ('Funnel Timestamps', {
            'fields': ('form_submitted_at', 'meeting_booked_at', 'meeting_held_at', 'pilot_signed_at', 'deal_closed_at', 'churned_at'),
            'classes': ('collapse',)
        }),
        ('Communication Preferences', {
            'fields': ('do_not_call', 'email_opt_out'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('assigned_to', 'created_by', 'description'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['funnel_stage_updated_at']


@admin.register(FunnelStageHistory)
class FunnelStageHistoryAdmin(admin.ModelAdmin):
    list_display = ['lead', 'from_stage', 'to_stage', 'changed_at', 'changed_by']
    list_filter = ['from_stage', 'to_stage', 'changed_at']
    search_fields = ['lead__first_name', 'lead__last_name', 'lead__company']
    ordering = ['-changed_at']
    readonly_fields = ['changed_at']
