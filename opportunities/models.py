from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Account
from contacts.models import Contact


class Opportunity(models.Model):
    SALES_STAGE = [
        ('prospecting', 'Prospecting'),
        ('qualification', 'Qualification'),
        ('needs_analysis', 'Needs Analysis'),
        ('value_proposition', 'Value Proposition'),
        ('id_decision_makers', 'Id. Decision Makers'),
        ('perception_analysis', 'Perception Analysis'),
        ('proposal', 'Proposal/Price Quote'),
        ('negotiation', 'Negotiation/Review'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]
    
    LEAD_SOURCE = [
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
    
    TYPE_CHOICES = [
        ('existing_business', 'Existing Business'),
        ('new_business', 'New Business'),
    ]
    
    name = models.CharField(max_length=200)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='opportunities')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Opportunity details
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    sales_stage = models.CharField(max_length=20, choices=SALES_STAGE, default='prospecting')
    probability = models.IntegerField(default=0, help_text='Probability of closing (0-100%)')
    expected_close_date = models.DateField()
    
    opportunity_type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=True)
    lead_source = models.CharField(max_length=20, choices=LEAD_SOURCE, blank=True)
    
    next_step = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # Tracking
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_opportunities')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expected_close_date']
        verbose_name_plural = 'Opportunities'
    
    def __str__(self):
        return f"{self.name} - {self.account}"
    
    @property
    def weighted_amount(self):
        return self.amount * (self.probability / 100)
    
    @property
    def is_won(self):
        return self.sales_stage == 'closed_won'
    
    @property
    def is_lost(self):
        return self.sales_stage == 'closed_lost'
    
    @property
    def is_open(self):
        return self.sales_stage not in ['closed_won', 'closed_lost']
    
    def get_absolute_url(self):
        return reverse('opportunities:detail', kwargs={'pk': self.pk})
