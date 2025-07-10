from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile for CRM-specific settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100, blank=True)
    
    # Dashboard preferences
    default_dashboard = models.CharField(max_length=50, default='overview')
    timezone = models.CharField(max_length=50, default='UTC')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"


class DashboardWidget(models.Model):
    """Track user's dashboard widget preferences"""
    WIDGET_TYPES = [
        ('sales_pipeline', 'Sales Pipeline'),
        ('recent_activities', 'Recent Activities'),
        ('my_tasks', 'My Tasks'),
        ('lead_conversion', 'Lead Conversion'),
        ('monthly_sales', 'Monthly Sales'),
        ('top_accounts', 'Top Accounts'),
        ('campaign_roi', 'Campaign ROI'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_widgets')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    position = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['position']
        unique_together = ['user', 'widget_type']
    
    def __str__(self):
        return f"{self.user.username} - {self.widget_type}"


class ActivityLog(models.Model):
    """Log important activities for audit trail"""
    ACTION_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed'),
        ('convert', 'Converted'),
        ('assign', 'Assigned'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_TYPES)
    object_type = models.CharField(max_length=50)  # e.g., 'Lead', 'Contact', 'Opportunity'
    object_id = models.PositiveIntegerField()
    object_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} {self.action} {self.object_type} {self.object_name}"
