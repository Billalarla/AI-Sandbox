from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'title', 'account', 'email', 'phone', 'assigned_to', 'created_at']
    list_filter = ['account', 'department', 'lead_source', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'account__name']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('salutation', 'first_name', 'last_name', 'title', 'account')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'mobile', 'fax')
        }),
        ('Mailing Address', {
            'fields': ('mailing_street', 'mailing_city', 'mailing_state', 'mailing_postal_code', 'mailing_country'),
            'classes': ('collapse',)
        }),
        ('Other Address', {
            'fields': ('other_street', 'other_city', 'other_state', 'other_postal_code', 'other_country'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('department', 'reports_to', 'lead_source', 'do_not_call', 'email_opt_out', 'description', 'assigned_to')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
