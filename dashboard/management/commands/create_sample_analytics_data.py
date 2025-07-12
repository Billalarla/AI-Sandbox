import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from accounts.models import Account
from contacts.models import Contact
from leads.models import Lead
from opportunities.models import Opportunity
from tasks.models import Task, Call, Meeting


class Command(BaseCommand):
    help = 'Generate sample analytics data for charts and dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of sample records to create for each model',
        )

    def handle(self, *args, **options):
        count = options['count']
        
        self.stdout.write(self.style.SUCCESS(f'Creating {count} sample records for analytics...'))
        
        # Get or create a sample user
        user, created = User.objects.get_or_create(
            username='sample_user',
            defaults={
                'email': 'sample@example.com',
                'first_name': 'Sample',
                'last_name': 'User'
            }
        )
        
        # Create sample accounts if they don't exist
        accounts = list(Account.objects.all())
        if len(accounts) < 10:
            for i in range(10):
                account, created = Account.objects.get_or_create(
                    name=f'Sample Company {i+1}',
                    defaults={
                        'account_type': random.choice(['customer', 'prospect', 'partner']),
                        'industry': random.choice(['technology', 'healthcare', 'finance', 'manufacturing']),
                        'website': f'https://company{i+1}.com',
                        'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                        'email': f'info@company{i+1}.com',
                        'annual_revenue': random.randint(100000, 50000000),
                        'employees': random.randint(10, 5000),
                        'assigned_to': user,
                        'created_by': user,
                    }
                )
                if created:
                    accounts.append(account)
        
        # Create sample leads with funnel tracking
        lead_sources = ['website', 'referral', 'cold_call', 'email', 'social_media', 'event']
        statuses = ['new', 'contacted', 'qualified', 'converted', 'dead']
        funnel_stages = ['form_submitted', 'meeting_booked', 'meeting_held', 'pilot_signed', 'deal_closed']
        
        for i in range(count):
            created_date = timezone.now() - timedelta(days=random.randint(1, 365))
            
            # Randomly assign funnel stage (weighted towards earlier stages)
            stage_weights = [0.4, 0.25, 0.15, 0.1, 0.1]  # Most leads in early stages
            funnel_stage = random.choices(funnel_stages, weights=stage_weights)[0]
            
            # Set timestamps based on funnel progression
            timestamps = {}
            stage_index = funnel_stages.index(funnel_stage)
            
            for j, stage in enumerate(funnel_stages[:stage_index + 1]):
                timestamp_field = f'{stage}_at'
                timestamp_value = created_date + timedelta(days=j * random.randint(1, 7))
                timestamps[timestamp_field] = timestamp_value
            
            lead, created = Lead.objects.get_or_create(
                email=f'lead{i}@example.com',
                defaults={
                    'first_name': f'Lead{i}',
                    'last_name': f'Person{i}',
                    'company': f'Lead Company {i}',
                    'title': random.choice(['Manager', 'Director', 'VP', 'CEO', 'Engineer']),
                    'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    'lead_source': random.choice(lead_sources),
                    'status': random.choice(statuses),
                    'funnel_stage': funnel_stage,
                    'lead_score': random.randint(0, 100),
                    'estimated_value': random.randint(5000, 250000) if random.choice([True, False]) else None,
                    'assigned_to': user,
                    'created_by': user,
                    'created_at': created_date,
                    'updated_at': created_date,
                    **timestamps  # Add all the timestamp fields
                }
            )
        
        # Create sample opportunities
        sales_stages = ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost']
        
        for i in range(count):
            created_date = timezone.now() - timedelta(days=random.randint(1, 365))
            close_date = created_date + timedelta(days=random.randint(30, 180))
            
            Opportunity.objects.get_or_create(
                name=f'Opportunity {i}',
                defaults={
                    'account': random.choice(accounts),
                    'amount': random.randint(5000, 500000),
                    'sales_stage': random.choice(sales_stages),
                    'probability': random.randint(10, 90),
                    'expected_close_date': close_date,
                    'description': f'Sample opportunity {i} description',
                    'assigned_to': user,
                    'created_by': user,
                    'created_at': created_date,
                    'updated_at': created_date,
                }
            )
        
        # Create sample calls
        call_types = ['inbound', 'outbound']
        call_statuses = ['planned', 'completed', 'cancelled', 'no_answer']
        call_results = ['interested', 'not_interested', 'voicemail', 'meeting_scheduled', 'sale_closed']
        
        for i in range(count):
            created_date = timezone.now() - timedelta(days=random.randint(1, 90))
            scheduled_date = created_date + timedelta(hours=random.randint(1, 24))
            
            Call.objects.get_or_create(
                subject=f'Sales Call {i}',
                defaults={
                    'call_type': random.choice(call_types),
                    'status': random.choice(call_statuses),
                    'call_result': random.choice(call_results),
                    'phone_number': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                    'scheduled_datetime': scheduled_date,
                    'duration_minutes': random.randint(5, 60),
                    'call_notes': f'Sample call {i} notes',
                    'description': f'Sample call {i} agenda',
                    'related_account': random.choice(accounts),
                    'assigned_to': user,
                    'created_by': user,
                    'created_at': created_date,
                    'updated_at': created_date,
                }
            )
        
        # Create sample meetings
        meeting_types = ['sales_meeting', 'demo', 'follow_up', 'negotiation', 'kickoff']
        meeting_statuses = ['planned', 'completed', 'cancelled', 'postponed']
        
        for i in range(count):
            created_date = timezone.now() - timedelta(days=random.randint(1, 90))
            start_date = created_date + timedelta(hours=random.randint(1, 168))  # within a week
            
            Meeting.objects.get_or_create(
                subject=f'Business Meeting {i}',
                defaults={
                    'meeting_type': random.choice(meeting_types),
                    'status': random.choice(meeting_statuses),
                    'start_datetime': start_date,
                    'end_datetime': start_date + timedelta(hours=random.randint(1, 4)),
                    'location': f'Conference Room {random.randint(1, 10)}' if random.choice([True, False]) else 'Online',
                    'agenda': f'Discuss business opportunities for meeting {i}',
                    'attendees_notes': f'attendee{i}@example.com',
                    'meeting_notes': f'Sample meeting {i} notes',
                    'related_account': random.choice(accounts),
                    'assigned_to': user,
                    'created_by': user,
                    'created_at': created_date,
                    'updated_at': created_date,
                }
            )
        
        # Create sample tasks
        task_types = ['email', 'call', 'meeting', 'follow_up', 'proposal']
        task_statuses = ['not_started', 'in_progress', 'completed', 'cancelled']
        priorities = ['low', 'medium', 'high', 'urgent']
        
        for i in range(count):
            created_date = timezone.now() - timedelta(days=random.randint(1, 60))
            due_date = created_date + timedelta(days=random.randint(1, 30))
            
            Task.objects.get_or_create(
                subject=f'Task {i}',
                defaults={
                    'task_type': random.choice(task_types),
                    'status': random.choice(task_statuses),
                    'priority': random.choice(priorities),
                    'due_date': due_date,
                    'description': f'Sample task {i} description',
                    'assigned_to': user,
                    'created_by': user,
                    'created_at': created_date,
                    'updated_at': created_date,
                }
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {Lead.objects.count()} leads\n'
                f'- {Opportunity.objects.count()} opportunities\n'
                f'- {Call.objects.count()} calls\n'
                f'- {Meeting.objects.count()} meetings\n'
                f'- {Task.objects.count()} tasks\n'
                f'- {Account.objects.count()} accounts'
            )
        )
