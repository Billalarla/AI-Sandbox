from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import datetime, timedelta
import random

from tasks.models import Task, Call, Meeting
from accounts.models import Account
from contacts.models import Contact


class Command(BaseCommand):
    help = 'Create sample calendar events for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to create events for (default: 30)'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of events per type to create (default: 20)'
        )

    def handle(self, *args, **options):
        days = options['days']
        count = options['count']
        
        # Get existing data
        users = list(User.objects.filter(is_active=True))
        accounts = list(Account.objects.all())
        contacts = list(Contact.objects.all())
        
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return
        
        if not accounts:
            self.stdout.write(self.style.ERROR('No accounts found. Please create accounts first.'))
            return
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=days)
        
        # Create sample tasks
        self.stdout.write('Creating sample tasks...')
        task_subjects = [
            'Follow up with client',
            'Prepare proposal',
            'Review contract',
            'Send invoice',
            'Update CRM records',
            'Client onboarding',
            'Weekly team meeting',
            'Product demo preparation',
            'Market research',
            'Competitive analysis',
            'Budget review',
            'Quarterly planning',
            'Training session',
            'Documentation update',
            'System maintenance'
        ]
        
        for i in range(count):
            due_date = timezone.make_aware(
                datetime.combine(
                    start_date + timedelta(days=random.randint(0, days)),
                    datetime.min.time().replace(
                        hour=random.randint(9, 17),
                        minute=random.choice([0, 15, 30, 45])
                    )
                )
            )
            
            task = Task.objects.create(
                subject=random.choice(task_subjects),
                description=f'Sample task {i+1} created for calendar testing.',
                due_date=due_date,
                priority=random.choice(['low', 'medium', 'high']),
                status=random.choice(['not_started', 'in_progress', 'completed']),
                assigned_to=random.choice(users),
                created_by=random.choice(users)
            )
            
            # Randomly assign to an account using generic foreign key
            if random.choice([True, False]) and accounts:
                account = random.choice(accounts)
                task.content_type = ContentType.objects.get_for_model(Account)
                task.object_id = account.id
                task.save()
        
        # Create sample calls
        self.stdout.write('Creating sample calls...')
        call_subjects = [
            'Sales call with prospect',
            'Customer support call',
            'Project status update',
            'Technical consultation',
            'Contract negotiation',
            'Product demonstration',
            'Follow-up call',
            'Discovery call',
            'Closing call',
            'Check-in call',
            'Escalation call',
            'Onboarding call',
            'Training call',
            'Feedback session',
            'Partnership discussion'
        ]
        
        for i in range(count):
            call_datetime = timezone.make_aware(
                datetime.combine(
                    start_date + timedelta(days=random.randint(0, days)),
                    datetime.min.time().replace(
                        hour=random.randint(9, 17),
                        minute=random.choice([0, 15, 30, 45])
                    )
                )
            )
            
            Call.objects.create(
                subject=random.choice(call_subjects),
                description=f'Sample call {i+1} created for calendar testing.',
                scheduled_datetime=call_datetime,
                duration_minutes=random.choice([15, 30, 45, 60]),
                call_type=random.choice(['inbound', 'outbound']),
                status=random.choice(['planned', 'in_progress', 'completed', 'cancelled']),
                phone_number=f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                assigned_to=random.choice(users),
                related_account=random.choice(accounts) if random.choice([True, False]) else None,
                related_contact=random.choice(contacts) if random.choice([True, False]) else None,
                created_by=random.choice(users)
            )
        
        # Create sample meetings
        self.stdout.write('Creating sample meetings...')
        meeting_subjects = [
            'Kickoff meeting',
            'Project review',
            'Strategic planning',
            'Client presentation',
            'Team standup',
            'Budget discussion',
            'Product roadmap',
            'Risk assessment',
            'Quality review',
            'Stakeholder update',
            'Requirements gathering',
            'Sprint planning',
            'Retrospective',
            'All-hands meeting',
            'Board meeting'
        ]
        
        meeting_locations = [
            'Conference Room A',
            'Conference Room B',
            'Main Office',
            'Client Site',
            'Virtual Meeting',
            'Boardroom',
            'Training Room',
            'Lobby',
            'Cafeteria',
            'Outdoor Pavilion'
        ]
        
        for i in range(count):
            start_datetime = timezone.make_aware(
                datetime.combine(
                    start_date + timedelta(days=random.randint(0, days)),
                    datetime.min.time().replace(
                        hour=random.randint(9, 16),
                        minute=random.choice([0, 30])
                    )
                )
            )
            
            duration_hours = random.choice([1, 1.5, 2, 3])
            end_datetime = start_datetime + timedelta(hours=duration_hours)
            
            is_virtual = random.choice([True, False])
            
            Meeting.objects.create(
                subject=random.choice(meeting_subjects),
                agenda=f'Sample meeting {i+1} agenda created for calendar testing.',
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                meeting_type=random.choice(['sales_meeting', 'client_meeting', 'internal', 'training']),
                status=random.choice(['planned', 'in_progress', 'completed', 'cancelled']),
                location='Online' if is_virtual else random.choice(meeting_locations),
                meeting_url='https://zoom.us/j/1234567890' if is_virtual else '',
                assigned_to=random.choice(users),
                related_account=random.choice(accounts) if random.choice([True, False]) else None,
                related_contact=random.choice(contacts) if random.choice([True, False]) else None,
                created_by=random.choice(users)
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {count} tasks, {count} calls, and {count} meetings '
                f'spanning {days} days for calendar testing.'
            )
        )
        
        # Display summary
        total_tasks = Task.objects.count()
        total_calls = Call.objects.count()
        total_meetings = Meeting.objects.count()
        
        self.stdout.write(f'Total in database: {total_tasks} tasks, {total_calls} calls, {total_meetings} meetings')
