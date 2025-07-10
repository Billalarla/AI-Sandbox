from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'industry', 'phone', 'email', 'assigned_to', 'created_at']
    list_filter = ['account_type', 'industry', 'created_at']
    search_fields = ['name', 'email', 'phone']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'account_type', 'industry', 'website', 'phone', 'email')
        }),
        ('Billing Address', {
            'fields': ('billing_street', 'billing_city', 'billing_state', 'billing_postal_code', 'billing_country'),
            'classes': ('collapse',)
        }),
        ('Shipping Address', {
            'fields': ('shipping_street', 'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'),
            'classes': ('collapse',)
        }),
        ('Financial Information', {
            'fields': ('annual_revenue', 'employees'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('description', 'assigned_to')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
