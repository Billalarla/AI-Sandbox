from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime, time
import random

from tasks.models import Task, Call, Meeting
from contacts.models import Contact
from leads.models import Lead
from accounts.models import Account
from opportunities.models import Opportunity


class Command(BaseCommand):
    help = 'Create sample future scheduled activities for the heatmap demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days in the future to create activities for (default: 90)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing future activities before creating new ones'
        )

    def handle(self, *args, **options):
        days = options['days']
        clear_existing = options['clear']
        
        # Get or create a user for assignments
        try:
            user = User.objects.filter(is_active=True).first()
            if not user:
                user = User.objects.create_user(
                    username='demo_user',
                    email='demo@example.com',
                    first_name='Demo',
                    last_name='User'
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting user: {e}'))
            return

        # Clear existing future activities if requested
        if clear_existing:
            future_date = timezone.now()
            deleted_tasks = Task.objects.filter(due_date__gte=future_date).delete()[0]
            deleted_calls = Call.objects.filter(scheduled_datetime__gte=future_date).delete()[0]
            deleted_meetings = Meeting.objects.filter(start_datetime__gte=future_date).delete()[0]
            self.stdout.write(
                self.style.WARNING(
                    f'Cleared {deleted_tasks} tasks, {deleted_calls} calls, {deleted_meetings} meetings'
                )
            )

        # Get related objects for activities
        contacts = list(Contact.objects.all()[:20])  # Limit to first 20
        leads = list(Lead.objects.all()[:20])
        accounts = list(Account.objects.all()[:10])
        opportunities = list(Opportunity.objects.all()[:10])

        # Create realistic activity patterns
        start_date = timezone.now().date()
        activities_created = {'tasks': 0, 'calls': 0, 'meetings': 0}

        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            
            # Calculate activity frequency based on how far in the future
            # More activities in near future, fewer as we go further out
            if day_offset <= 7:  # Next week - high activity
                base_activities = random.randint(3, 8)
            elif day_offset <= 30:  # Next month - medium activity  
                base_activities = random.randint(1, 5)
            elif day_offset <= 60:  # Next 2 months - lower activity
                base_activities = random.randint(0, 3)
            else:  # Beyond 2 months - minimal activity
                base_activities = random.randint(0, 2)

            # Reduce activities on weekends
            if current_date.weekday() >= 5:  # Saturday or Sunday
                base_activities = max(0, base_activities - 2)

            # Create tasks for this day
            num_tasks = max(0, base_activities + random.randint(-1, 1))
            for _ in range(num_tasks):
                task_time = time(
                    hour=random.randint(8, 17),
                    minute=random.choice([0, 15, 30, 45])
                )
                due_datetime = timezone.make_aware(datetime.combine(current_date, task_time))
                
                related_object = random.choice(contacts + leads + accounts) if (contacts or leads or accounts) else None
                
                task = Task.objects.create(
                    subject=random.choice([
                        'Follow up on proposal',
                        'Prepare presentation materials',
                        'Send contract documents',
                        'Review customer requirements',
                        'Update project status',
                        'Prepare demo environment',
                        'Send weekly report',
                        'Call customer for feedback',
                        'Update CRM records',
                        'Prepare for next meeting'
                    ]),
                    status='not_started',
                    priority=random.choice(['low', 'medium', 'high']),
                    task_type=random.choice(['task', 'email', 'call', 'other']),
                    due_date=due_datetime,
                    description=f'Task scheduled for {current_date}',
                    assigned_to=user,
                    created_by=user
                )
                
                # Link to related object
                if related_object and hasattr(related_object, '_meta'):
                    from django.contrib.contenttypes.models import ContentType
                    task.content_type = ContentType.objects.get_for_model(related_object)
                    task.object_id = related_object.pk
                    task.save()
                
                activities_created['tasks'] += 1

            # Create calls for this day
            num_calls = max(0, (base_activities // 2) + random.randint(-1, 1))
            for _ in range(num_calls):
                call_time = time(
                    hour=random.randint(9, 16),
                    minute=random.choice([0, 15, 30, 45])
                )
                scheduled_datetime = timezone.make_aware(datetime.combine(current_date, call_time))
                
                related_contact = random.choice(contacts) if contacts else None
                related_lead = random.choice(leads) if leads else None
                
                call = Call.objects.create(
                    subject=random.choice([
                        'Discovery call',
                        'Follow-up call',
                        'Demo scheduling call',
                        'Contract discussion',
                        'Customer check-in',
                        'Proposal review call',
                        'Technical discussion',
                        'Pricing negotiation',
                        'Implementation planning',
                        'Support call'
                    ]),
                    call_type='outbound',
                    status='planned',
                    phone_number='+1-555-' + ''.join([str(random.randint(0, 9)) for _ in range(7)]),
                    scheduled_datetime=scheduled_datetime,
                    description=f'Call scheduled for {current_date}',
                    related_contact=related_contact,
                    related_lead=related_lead,
                    assigned_to=user,
                    created_by=user
                )
                activities_created['calls'] += 1

            # Create meetings for this day (fewer than calls/tasks)
            num_meetings = max(0, (base_activities // 3) + random.randint(-1, 1))
            for _ in range(num_meetings):
                start_time = time(
                    hour=random.randint(9, 15),
                    minute=random.choice([0, 30])
                )
                start_datetime = timezone.make_aware(datetime.combine(current_date, start_time))
                end_datetime = start_datetime + timedelta(hours=random.choice([1, 1.5, 2]))
                
                related_account = random.choice(accounts) if accounts else None
                related_opportunity = random.choice(opportunities) if opportunities else None
                related_contact = random.choice(contacts) if contacts else None
                
                meeting = Meeting.objects.create(
                    subject=random.choice([
                        'Product demonstration',
                        'Sales presentation',
                        'Contract negotiation',
                        'Project kickoff',
                        'Requirements gathering',
                        'Solution review',
                        'Implementation planning',
                        'Strategic planning',
                        'Customer onboarding',
                        'Quarterly review'
                    ]),
                    meeting_type=random.choice(['sales_meeting', 'demo', 'follow_up', 'negotiation']),
                    status='planned',
                    location=random.choice(['Conference Room A', 'Online', 'Client Office', 'Video Call']),
                    meeting_url='https://meet.company.com/room/' + str(random.randint(1000, 9999)) if random.choice([True, False]) else '',
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    duration_minutes=int((end_datetime - start_datetime).total_seconds() / 60),
                    agenda=f'Meeting agenda for {current_date}',
                    related_account=related_account,
                    related_opportunity=related_opportunity,
                    related_contact=related_contact,
                    primary_contact=related_contact,
                    assigned_to=user,
                    created_by=user
                )
                activities_created['meetings'] += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created future scheduled activities for {days} days:\n'
                f'- Tasks: {activities_created["tasks"]}\n'
                f'- Calls: {activities_created["calls"]}\n'
                f'- Meetings: {activities_created["meetings"]}\n'
                f'Total activities: {sum(activities_created.values())}'
            )
        )
