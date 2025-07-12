from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Lead(models.Model):
    LEAD_STATUS = [
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('in_process', 'In Process'),
        ('converted', 'Converted'),
        ('recycled', 'Recycled'),
        ('dead', 'Dead'),
    ]
    
    LEAD_SOURCE = [
        ('cold_call', 'Cold Call'),
        ('existing_customer', 'Existing Customer'),
        ('partner', 'Partner'),
        ('public_relations', 'Public Relations'),
        ('direct_mail', 'Direct Mail'),
        ('conference', 'Conference'),
        ('trade_show', 'Trade Show'),
        ('web_site', 'Web Site'),
        ('word_of_mouth', 'Word of mouth'),
        ('email', 'Email'),
        ('campaign', 'Campaign'),
        ('other', 'Other'),
    ]
    
    # FUNNEL STAGE TRACKING - NEW!
    FUNNEL_STAGE_CHOICES = [
        ('form_submitted', 'Form Submitted'),
        ('meeting_booked', 'Meeting Booked'),
        ('meeting_held', 'Meeting Held'),
        ('pilot_signed', 'Pilot Signed'),
        ('deal_closed', 'Deal Closed'),
        ('churned', 'Churned'),
    ]
    
    SALUTATIONS = [
        ('mr', 'Mr.'),
        ('mrs', 'Mrs.'),
        ('ms', 'Ms.'),
        ('dr', 'Dr.'),
        ('prof', 'Prof.'),
    ]
    
    # Personal Info
    salutation = models.CharField(max_length=10, choices=SALUTATIONS, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=200)
    
    # Contact Info
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Address
    street = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Lead Info
    lead_source = models.CharField(max_length=20, choices=LEAD_SOURCE, blank=True)
    status = models.CharField(max_length=20, choices=LEAD_STATUS, default='new')
    industry = models.CharField(max_length=100, blank=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    employees = models.IntegerField(null=True, blank=True)
    
    # FUNNEL TRACKING FIELDS - NEW!
    funnel_stage = models.CharField(max_length=20, choices=FUNNEL_STAGE_CHOICES, default='form_submitted')
    funnel_stage_updated_at = models.DateTimeField(auto_now=True)
    
    # Funnel progression timestamps
    form_submitted_at = models.DateTimeField(null=True, blank=True)
    meeting_booked_at = models.DateTimeField(null=True, blank=True)
    meeting_held_at = models.DateTimeField(null=True, blank=True)
    pilot_signed_at = models.DateTimeField(null=True, blank=True)
    deal_closed_at = models.DateTimeField(null=True, blank=True)
    churned_at = models.DateTimeField(null=True, blank=True)
    
    # Additional funnel metrics
    lead_score = models.IntegerField(default=0, help_text="Lead quality score 0-100")
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Communication preferences
    do_not_call = models.BooleanField(default=False)
    email_opt_out = models.BooleanField(default=False)
    
    description = models.TextField(blank=True)
    
    # Tracking
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_leads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse('leads:detail', kwargs={'pk': self.pk})
    
    def move_to_next_stage(self):
        """Move lead to the next funnel stage and update timestamp"""
        stage_progression = {
            'form_submitted': ('meeting_booked', 'meeting_booked_at'),
            'meeting_booked': ('meeting_held', 'meeting_held_at'),
            'meeting_held': ('pilot_signed', 'pilot_signed_at'),
            'pilot_signed': ('deal_closed', 'deal_closed_at'),
        }
        
        if self.funnel_stage in stage_progression:
            next_stage, timestamp_field = stage_progression[self.funnel_stage]
            old_stage = self.funnel_stage
            self.funnel_stage = next_stage
            setattr(self, timestamp_field, timezone.now())
            self.save()
            
            # Create history record
            FunnelStageHistory.objects.create(
                lead=self,
                from_stage=old_stage,
                to_stage=next_stage,
                changed_by=None  # You can pass user in view
            )
            return True
        return False
    
    def get_funnel_progress_percentage(self):
        """Calculate how far through the funnel this lead is"""
        stages = ['form_submitted', 'meeting_booked', 'meeting_held', 'pilot_signed', 'deal_closed']
        try:
            current_index = stages.index(self.funnel_stage)
            return (current_index + 1) / len(stages) * 100
        except ValueError:
            return 0


class FunnelStageHistory(models.Model):
    """Track when leads move between funnel stages"""
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='stage_history')
    from_stage = models.CharField(max_length=20, choices=Lead.FUNNEL_STAGE_CHOICES, null=True, blank=True)
    to_stage = models.CharField(max_length=20, choices=Lead.FUNNEL_STAGE_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-changed_at']
        
    def __str__(self):
        return f"{self.lead} moved from {self.from_stage} to {self.to_stage}"
