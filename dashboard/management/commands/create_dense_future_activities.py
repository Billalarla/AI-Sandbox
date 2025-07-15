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
    help = 'Create high-density sample future scheduled activities for better heatmap demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days in the future to create activities for (default: 90)'
        )

    def handle(self, *args, **options):
        days = options['days']
        
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

        # Clear existing future activities first
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

        # Create realistic activity patterns with heavy front-loading
        start_date = timezone.now().date()
        activities_created = {'tasks': 0, 'calls': 0, 'meetings': 0}

        for day_offset in range(days):
            current_date = start_date + timedelta(days=day_offset)
            
            # Calculate activity frequency with exponential decay
            # Very heavy activity in first week, tapering off dramatically
            if day_offset <= 3:  # Next 3 days - very high activity
                base_activities = random.randint(8, 15)
            elif day_offset <= 7:  # Next week - high activity
                base_activities = random.randint(5, 10)
            elif day_offset <= 14:  # Next 2 weeks - medium-high activity  
                base_activities = random.randint(3, 7)
            elif day_offset <= 30:  # Next month - medium activity
                base_activities = random.randint(1, 4)
            elif day_offset <= 60:  # Next 2 months - low activity
                base_activities = random.randint(0, 2)
            else:  # Beyond 2 months - very minimal activity
                base_activities = random.randint(0, 1)

            # Reduce activities on weekends
            if current_date.weekday() >= 5:  # Saturday or Sunday
                base_activities = max(0, base_activities // 3)

            # Create multiple activities throughout the day
            total_activities = base_activities
            
            for activity_num in range(total_activities):
                activity_type = random.choices(
                    ['task', 'call', 'meeting'], 
                    weights=[50, 30, 20],  # More tasks, fewer meetings
                    k=1
                )[0]
                
                # Spread activities throughout business hours
                activity_hour = random.randint(8, 17)
                activity_minute = random.choice([0, 15, 30, 45])
                activity_time = time(hour=activity_hour, minute=activity_minute)
                activity_datetime = timezone.make_aware(datetime.combine(current_date, activity_time))
                
                related_object = random.choice(contacts + leads + accounts) if (contacts or leads or accounts) else None
                
                if activity_type == 'task':
                    task = Task.objects.create(
                        subject=random.choice([
                            'Follow up on proposal discussion',
                            'Prepare presentation for client meeting',
                            'Send contract documents for review',
                            'Review customer technical requirements',
                            'Update project implementation status',
                            'Prepare demo environment for prospect',
                            'Send weekly progress report',
                            'Call customer for project feedback',
                            'Update CRM with latest interactions',
                            'Prepare agenda for upcoming meeting',
                            'Review pricing proposal with team',
                            'Send onboarding materials to new client',
                            'Schedule follow-up call with prospect',
                            'Finalize technical specifications',
                            'Conduct internal project review'
                        ]),
                        status='not_started',
                        priority=random.choices(
                            ['low', 'medium', 'high'],
                            weights=[20, 60, 20],
                            k=1
                        )[0],
                        task_type=random.choice(['task', 'email', 'call', 'other']),
                        due_date=activity_datetime,
                        description=f'Task scheduled for {current_date} - created for heatmap demo',
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
                
                elif activity_type == 'call':
                    related_contact = random.choice(contacts) if contacts else None
                    related_lead = random.choice(leads) if leads else None
                    
                    call = Call.objects.create(
                        subject=random.choice([
                            'Discovery call with new prospect',
                            'Follow-up call after proposal',
                            'Demo scheduling and coordination',
                            'Contract terms discussion',
                            'Customer success check-in call',
                            'Proposal review and Q&A call',
                            'Technical implementation discussion',
                            'Pricing and negotiation call',
                            'Project implementation planning',
                            'Customer support and training call',
                            'Strategic partnership discussion',
                            'Renewal conversation with existing client',
                            'Escalation resolution call',
                            'Onboarding walkthrough call',
                            'Requirements gathering call'
                        ]),
                        call_type='outbound',
                        status='planned',
                        phone_number='+1-555-' + ''.join([str(random.randint(0, 9)) for _ in range(7)]),
                        scheduled_datetime=activity_datetime,
                        description=f'Call scheduled for {current_date} - created for heatmap demo',
                        related_contact=related_contact,
                        related_lead=related_lead,
                        assigned_to=user,
                        created_by=user
                    )
                    activities_created['calls'] += 1
                
                elif activity_type == 'meeting':
                    # Meetings tend to be longer, so place them at specific times
                    meeting_hour = random.choice([9, 10, 11, 13, 14, 15, 16])
                    meeting_time = time(hour=meeting_hour, minute=0)
                    start_datetime = timezone.make_aware(datetime.combine(current_date, meeting_time))
                    duration_hours = random.choice([1, 1.5, 2])
                    end_datetime = start_datetime + timedelta(hours=duration_hours)
                    
                    related_account = random.choice(accounts) if accounts else None
                    related_opportunity = random.choice(opportunities) if opportunities else None
                    related_contact = random.choice(contacts) if contacts else None
                    
                    meeting = Meeting.objects.create(
                        subject=random.choice([
                            'Product demonstration and Q&A',
                            'Sales presentation and proposal review',
                            'Contract negotiation meeting',
                            'Project kickoff and planning session',
                            'Requirements gathering workshop',
                            'Solution architecture review',
                            'Implementation planning meeting',
                            'Strategic planning and roadmap review',
                            'Customer onboarding session',
                            'Quarterly business review',
                            'Technical deep-dive session',
                            'Partnership strategy meeting',
                            'Customer success review',
                            'Product training and enablement',
                            'Executive stakeholder meeting'
                        ]),
                        meeting_type=random.choice(['sales_meeting', 'demo', 'follow_up', 'negotiation', 'kickoff']),
                        status='planned',
                        location=random.choice([
                            'Conference Room A - Main Office',
                            'Online Video Conference',
                            'Client Office - Downtown',
                            'Teams Meeting',
                            'Zoom Conference Room',
                            'Customer Site Visit',
                            'Coffee Meeting - Local Café',
                            'Executive Boardroom',
                            'Training Room B',
                            'Virtual Meeting Room'
                        ]),
                        meeting_url='https://meet.company.com/room/' + str(random.randint(1000, 9999)) if random.choice([True, False]) else '',
                        start_datetime=start_datetime,
                        end_datetime=end_datetime,
                        duration_minutes=int(duration_hours * 60),
                        agenda=f'Meeting agenda for {current_date} - comprehensive discussion and planning session',
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
                f'Successfully created high-density future scheduled activities for {days} days:\n'
                f'- Tasks: {activities_created["tasks"]}\n'
                f'- Calls: {activities_created["calls"]}\n'
                f'- Meetings: {activities_created["meetings"]}\n'
                f'Total activities: {sum(activities_created.values())}\n\n'
                f'Activity distribution:\n'
                f'- Next 3 days: Very High (8-15 per day)\n'
                f'- Next 7 days: High (5-10 per day)\n'
                f'- Next 14 days: Medium-High (3-7 per day)\n'
                f'- Next 30 days: Medium (1-4 per day)\n'
                f'- 30-60 days: Low (0-2 per day)\n'
                f'- 60+ days: Minimal (0-1 per day)'
            )
        )
