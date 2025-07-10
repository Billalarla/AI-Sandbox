from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


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
