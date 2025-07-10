from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Account


class Contact(models.Model):
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
    
    # Contact Info
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    
    # Address
    mailing_street = models.TextField(blank=True)
    mailing_city = models.CharField(max_length=100, blank=True)
    mailing_state = models.CharField(max_length=100, blank=True)
    mailing_postal_code = models.CharField(max_length=20, blank=True)
    mailing_country = models.CharField(max_length=100, blank=True)
    
    other_street = models.TextField(blank=True)
    other_city = models.CharField(max_length=100, blank=True)
    other_state = models.CharField(max_length=100, blank=True)
    other_postal_code = models.CharField(max_length=20, blank=True)
    other_country = models.CharField(max_length=100, blank=True)
    
    # Relationships
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='contacts')
    reports_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Additional Info
    department = models.CharField(max_length=100, blank=True)
    lead_source = models.CharField(max_length=100, blank=True)
    do_not_call = models.BooleanField(default=False)
    email_opt_out = models.BooleanField(default=False)
    
    description = models.TextField(blank=True)
    
    # Tracking
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contacts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse('contacts:detail', kwargs={'pk': self.pk})
