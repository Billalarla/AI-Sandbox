from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Account
from contacts.models import Contact
from leads.models import Lead
from opportunities.models import Opportunity
from tasks.models import Task
from campaigns.models import Campaign
from datetime import datetime, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Create sample data for the CRM system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data for CRM system...')
        
        # Create sample users if they don't exist
        if not User.objects.filter(username='demo_user').exists():
            demo_user = User.objects.create_user(
                username='demo_user',
                email='demo@example.com',
                password='demo123',
                first_name='Demo',
                last_name='User'
            )
        else:
            demo_user = User.objects.get(username='demo_user')
        
        # Create sample accounts
        accounts_data = [
            {'name': 'Tech Solutions Inc.', 'industry': 'technology', 'annual_revenue': 5000000},
            {'name': 'Global Healthcare Corp.', 'industry': 'healthcare', 'annual_revenue': 2500000},
            {'name': 'Financial Services LLC', 'industry': 'finance', 'annual_revenue': 8000000},
            {'name': 'Education Partners', 'industry': 'education', 'annual_revenue': 1200000},
            {'name': 'Retail Chain Co.', 'industry': 'retail', 'annual_revenue': 15000000},
        ]
        
        for account_data in accounts_data:
            account, created = Account.objects.get_or_create(
                name=account_data['name'],
                defaults={
                    'account_type': 'customer',
                    'industry': account_data['industry'],
                    'annual_revenue': account_data['annual_revenue'],
                    'employees': random.randint(50, 500),
                    'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    'email': f'info@{account_data["name"].lower().replace(" ", "").replace(".", "")}.com',
                    'assigned_to': demo_user,
                    'created_by': demo_user,
                }
            )
            if created:
                self.stdout.write(f'Created account: {account.name}')
        
        # Create sample contacts
        contacts_data = [
            {'first_name': 'John', 'last_name': 'Smith', 'title': 'CEO'},
            {'first_name': 'Sarah', 'last_name': 'Johnson', 'title': 'CTO'},
            {'first_name': 'Michael', 'last_name': 'Brown', 'title': 'Sales Director'},
            {'first_name': 'Emily', 'last_name': 'Davis', 'title': 'Marketing Manager'},
            {'first_name': 'Robert', 'last_name': 'Wilson', 'title': 'IT Manager'},
        ]
        
        accounts = list(Account.objects.all())
        for contact_data in contacts_data:
            contact, created = Contact.objects.get_or_create(
                first_name=contact_data['first_name'],
                last_name=contact_data['last_name'],
                defaults={
                    'title': contact_data['title'],
                    'email': f'{contact_data["first_name"].lower()}.{contact_data["last_name"].lower()}@example.com',
                    'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    'account': random.choice(accounts),
                    'assigned_to': demo_user,
                    'created_by': demo_user,
                }
            )
            if created:
                self.stdout.write(f'Created contact: {contact.full_name}')
        
        # Create sample leads
        leads_data = [
            {'first_name': 'Alex', 'last_name': 'Thompson', 'company': 'StartupTech'},
            {'first_name': 'Lisa', 'last_name': 'Garcia', 'company': 'Innovation Labs'},
            {'first_name': 'David', 'last_name': 'Miller', 'company': 'Future Systems'},
            {'first_name': 'Jessica', 'last_name': 'Taylor', 'company': 'Digital Solutions'},
            {'first_name': 'Chris', 'last_name': 'Anderson', 'company': 'CloudFirst'},
        ]
        
        for lead_data in leads_data:
            lead, created = Lead.objects.get_or_create(
                first_name=lead_data['first_name'],
                last_name=lead_data['last_name'],
                company=lead_data['company'],
                defaults={
                    'email': f'{lead_data["first_name"].lower()}.{lead_data["last_name"].lower()}@{lead_data["company"].lower()}.com',
                    'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    'status': random.choice(['new', 'assigned', 'in_process']),
                    'lead_source': random.choice(['web_site', 'email', 'conference', 'partner']),
                    'industry': random.choice(['technology', 'healthcare', 'finance']),
                    'assigned_to': demo_user,
                    'created_by': demo_user,
                }
            )
            if created:
                self.stdout.write(f'Created lead: {lead.full_name}')
        
        # Create sample opportunities
        opps_data = [
            {'name': 'Enterprise Software Deal', 'amount': 150000, 'stage': 'proposal'},
            {'name': 'Cloud Migration Project', 'amount': 75000, 'stage': 'needs_analysis'},
            {'name': 'Security Audit Services', 'amount': 25000, 'stage': 'qualification'},
            {'name': 'Training and Support', 'amount': 45000, 'stage': 'negotiation'},
            {'name': 'Custom Development', 'amount': 200000, 'stage': 'value_proposition'},
        ]
        
        contacts = list(Contact.objects.all())
        for opp_data in opps_data:
            contact = random.choice(contacts)
            opp, created = Opportunity.objects.get_or_create(
                name=opp_data['name'],
                defaults={
                    'account': contact.account,
                    'contact': contact,
                    'amount': opp_data['amount'],
                    'sales_stage': opp_data['stage'],
                    'probability': random.randint(20, 80),
                    'expected_close_date': datetime.now().date() + timedelta(days=random.randint(30, 120)),
                    'opportunity_type': random.choice(['new_business', 'existing_business']),
                    'lead_source': random.choice(['existing_customer', 'partner', 'web_site']),
                    'assigned_to': demo_user,
                    'created_by': demo_user,
                }
            )
            if created:
                self.stdout.write(f'Created opportunity: {opp.name}')
        
        # Create sample tasks
        tasks_data = [
            {'subject': 'Follow up with prospect', 'priority': 'high'},
            {'subject': 'Prepare proposal document', 'priority': 'medium'},
            {'subject': 'Schedule demo meeting', 'priority': 'high'},
            {'subject': 'Send product information', 'priority': 'low'},
            {'subject': 'Review contract terms', 'priority': 'medium'},
        ]
        
        for task_data in tasks_data:
            task, created = Task.objects.get_or_create(
                subject=task_data['subject'],
                defaults={
                    'status': random.choice(['not_started', 'in_progress']),
                    'priority': task_data['priority'],
                    'task_type': random.choice(['call', 'email', 'meeting', 'task']),
                    'due_date': datetime.now() + timedelta(days=random.randint(1, 14)),
                    'assigned_to': demo_user,
                    'created_by': demo_user,
                }
            )
            if created:
                self.stdout.write(f'Created task: {task.subject}')
        
        # Create sample campaigns
        campaigns_data = [
            {'name': 'Spring Product Launch', 'type': 'email'},
            {'name': 'Trade Show Booth', 'type': 'trade_show'},
            {'name': 'Webinar Series', 'type': 'webinar'},
            {'name': 'Direct Mail Campaign', 'type': 'direct_mail'},
        ]
        
        for campaign_data in campaigns_data:
            campaign, created = Campaign.objects.get_or_create(
                name=campaign_data['name'],
                defaults={
                    'status': random.choice(['planning', 'active']),
                    'campaign_type': campaign_data['type'],
                    'start_date': datetime.now().date() - timedelta(days=random.randint(0, 30)),
                    'end_date': datetime.now().date() + timedelta(days=random.randint(30, 90)),
                    'budgeted_cost': random.randint(5000, 50000),
                    'expected_revenue': random.randint(25000, 200000),
                    'assigned_to': demo_user,
                    'created_by': demo_user,
                }
            )
            if created:
                self.stdout.write(f'Created campaign: {campaign.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
