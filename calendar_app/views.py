from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from datetime import datetime, timedelta
import json

from tasks.models import Task, Call, Meeting
from accounts.models import Account
from django.contrib.auth.models import User


class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar_app/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all accounts for the filter dropdown
        context['accounts'] = Account.objects.all().order_by('name')
        
        # Get all users for the filter dropdown  
        context['users'] = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
        # Add debug information
        context['debug_info'] = {
            'accounts_count': context['accounts'].count(),
            'users_count': context['users'].count(),
            'current_user': self.request.user.username if self.request.user.is_authenticated else 'Anonymous'
        }
        
        return context


class CalendarDebugView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar_app/calendar_debug.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all accounts for the filter dropdown
        context['accounts'] = Account.objects.all().order_by('name')
        
        # Get all users for the filter dropdown
        context['users'] = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
        # Add debug counts
        from datetime import date, timedelta
        today = date.today()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=30)
        
        context['debug_info'] = {
            'accounts_count': context['accounts'].count(),
            'users_count': context['users'].count(),
            'current_user': self.request.user.username if self.request.user.is_authenticated else 'Anonymous',
            'tasks_count': Task.objects.filter(due_date__range=[start_date, end_date]).count(),
            'calls_count': Call.objects.filter(scheduled_datetime__date__range=[start_date, end_date]).count(),
            'meetings_count': Meeting.objects.filter(start_datetime__date__range=[start_date, end_date]).count(),
            'date_range': f"{start_date} to {end_date}"
        }
        
        return context


class AccountCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar_app/account_calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        account_id = kwargs.get('account_id')
        try:
            account = Account.objects.get(id=account_id)
            context['account'] = account
        except Account.DoesNotExist:
            context['account'] = None
        
        return context


class CalendarSimpleView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar_app/calendar_simple.html'


class UserCalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'calendar_app/user_calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user_id = kwargs.get('user_id')
        try:
            calendar_user = User.objects.get(id=user_id)
            context['calendar_user'] = calendar_user
        except User.DoesNotExist:
            context['calendar_user'] = None
        
        return context


class CalendarQuickCreateView(LoginRequiredMixin, TemplateView):
    """Quick create view for calendar events"""
    template_name = 'calendar_app/quick_create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date from query params if provided
        date_str = self.request.GET.get('date')
        if date_str:
            try:
                from datetime import datetime
                context['selected_date'] = datetime.fromisoformat(date_str).date()
            except ValueError:
                context['selected_date'] = None
        
        # Get accounts and users for form fields
        context['accounts'] = Account.objects.all().order_by('name')
        context['users'] = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle quick event creation"""
        from django.shortcuts import redirect
        from django.contrib import messages
        
        event_type = request.POST.get('event_type')
        
        if event_type == 'task':
            return redirect('tasks:create')
        elif event_type == 'call':
            return redirect('tasks:call_create')
        elif event_type == 'meeting':
            return redirect('tasks:meeting_create')
        else:
            messages.error(request, 'Please select a valid event type.')
            return redirect('calendar_app:calendar')


def calendar_events_api(request):
    """API endpoint for calendar events"""
    import logging
    logger = logging.getLogger(__name__)
    
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    account_id = request.GET.get('account_id')
    user_id = request.GET.get('user_id')
    event_types = request.GET.getlist('types[]') or ['tasks', 'calls', 'meetings']
    
    logger.info(f"Calendar API called with: start={start_date}, end={end_date}, account={account_id}, user={user_id}, types={event_types}")
    
    events = []
    
    # Parse dates
    try:
        start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        logger.info(f"Parsed dates: {start_datetime} to {end_datetime}")
    except (ValueError, AttributeError) as e:
        logger.error(f"Date parsing error: {e}")
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Base filters for account
    account_filter = Q()
    if account_id:
        try:
            account = Account.objects.get(id=account_id)
            account_filter = Q(related_account=account)  # For Call and Meeting
        except Account.DoesNotExist:
            account_filter = Q(pk=None)  # No results
    
    # Base filters for user
    user_filter = Q()
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            user_filter = Q(assigned_to=user)
        except User.DoesNotExist:
            user_filter = Q(pk=None)  # No results
    
    # Get Tasks
    if 'tasks' in event_types:
        task_filters = user_filter & (
            Q(due_date__gte=start_datetime.date()) & 
            Q(due_date__lte=end_datetime.date())
        )
        
        # For tasks, handle account filtering with generic foreign key
        if account_id:
            try:
                account = Account.objects.get(id=account_id)
                account_content_type = ContentType.objects.get_for_model(Account)
                task_filters &= Q(content_type=account_content_type, object_id=account.id)
            except Account.DoesNotExist:
                task_filters &= Q(pk=None)  # No results
        
        tasks = Task.objects.filter(task_filters).select_related('assigned_to')
        
        for task in tasks:
            events.append({
                'id': f'task_{task.id}',
                'title': f'📋 {task.subject}',
                'start': task.due_date.isoformat(),
                'end': task.due_date.isoformat(),
                'allDay': True,
                'backgroundColor': get_task_color(task.priority),
                'borderColor': get_task_color(task.priority),
                'textColor': '#ffffff',
                'extendedProps': {
                    'type': 'task',
                    'id': task.id,
                    'status': task.status,
                    'priority': task.priority,
                    'assigned_to': task.assigned_to.get_full_name() if task.assigned_to else 'Unassigned',
                    'description': task.description[:100] + '...' if len(task.description) > 100 else task.description,
                    'url': f'/tasks/{task.id}/'
                }
            })
    
    # Get Calls
    if 'calls' in event_types:
        call_filters = user_filter & account_filter & (
            Q(scheduled_datetime__gte=start_datetime) & 
            Q(scheduled_datetime__lte=end_datetime)
        )
        
        calls = Call.objects.filter(call_filters).select_related('assigned_to', 'related_account')
        
        for call in calls:
            events.append({
                'id': f'call_{call.id}',
                'title': f'📞 {call.subject}',
                'start': call.scheduled_datetime.isoformat(),
                'end': (call.scheduled_datetime + timedelta(minutes=call.duration_minutes or 30)).isoformat(),
                'backgroundColor': get_call_color(call.status),
                'borderColor': get_call_color(call.status),
                'textColor': '#ffffff',
                'extendedProps': {
                    'type': 'call',
                    'id': call.id,
                    'status': call.status,
                    'call_type': call.call_type,
                    'phone_number': call.phone_number,
                    'assigned_to': call.assigned_to.get_full_name() if call.assigned_to else 'Unassigned',
                    'account': call.related_account.name if call.related_account else 'No account',
                    'description': call.description[:100] + '...' if len(call.description) > 100 else call.description,
                    'url': f'/tasks/calls/{call.id}/'
                }
            })
    
    # Get Meetings
    if 'meetings' in event_types:
        meeting_filters = user_filter & account_filter & (
            Q(start_datetime__gte=start_datetime) & 
            Q(start_datetime__lte=end_datetime)
        )
        
        meetings = Meeting.objects.filter(meeting_filters).select_related('assigned_to', 'related_account')
        
        for meeting in meetings:
            end_time = meeting.end_datetime or (meeting.start_datetime + timedelta(hours=1))
            
            events.append({
                'id': f'meeting_{meeting.id}',
                'title': f'🤝 {meeting.subject}',
                'start': meeting.start_datetime.isoformat(),
                'end': end_time.isoformat(),
                'backgroundColor': get_meeting_color(meeting.status),
                'borderColor': get_meeting_color(meeting.status),
                'textColor': '#ffffff',
                'extendedProps': {
                    'type': 'meeting',
                    'id': meeting.id,
                    'status': meeting.status,
                    'meeting_type': meeting.meeting_type,
                    'location': meeting.location,
                    'meeting_url': meeting.meeting_url,
                    'assigned_to': meeting.assigned_to.get_full_name() if meeting.assigned_to else 'Unassigned',
                    'account': meeting.related_account.name if meeting.related_account else 'No account',
                    'agenda': meeting.agenda[:100] + '...' if meeting.agenda and len(meeting.agenda) > 100 else meeting.agenda,
                    'url': f'/tasks/meetings/{meeting.id}/'
                }
            })
    
    logger.info(f"Returning {len(events)} events")
    return JsonResponse(events, safe=False)


def get_task_color(priority):
    """Get color based on task priority"""
    colors = {
        'high': '#dc3545',      # Red
        'medium': '#fd7e14',    # Orange
        'low': '#28a745',       # Green
    }
    return colors.get(priority, '#6c757d')  # Default gray


def get_call_color(status):
    """Get color based on call status"""
    colors = {
        'scheduled': '#0d6efd',     # Blue
        'in_progress': '#fd7e14',   # Orange
        'completed': '#28a745',     # Green
        'cancelled': '#6c757d',     # Gray
        'no_show': '#dc3545',       # Red
    }
    return colors.get(status, '#6c757d')


def get_meeting_color(status):
    """Get color based on meeting status"""
    colors = {
        'scheduled': '#0d6efd',     # Blue
        'in_progress': '#fd7e14',   # Orange
        'completed': '#28a745',     # Green
        'cancelled': '#6c757d',     # Gray
        'postponed': '#ffc107',     # Yellow
    }
    return colors.get(status, '#6c757d')


def calendar_event_counts_api(request):
    """API endpoint for event counts by date range"""
    from datetime import datetime, timedelta
    from django.db.models import Count
    import json
    
    # Default to current month if no dates provided
    today = datetime.now().date()
    start_date = request.GET.get('start', str(today.replace(day=1)))
    end_date = request.GET.get('end', str(today.replace(day=28) + timedelta(days=4)))
    
    try:
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Count events by type
    tasks_count = Task.objects.filter(
        due_date__range=[start_datetime.date(), end_datetime.date()]
    ).count()
    
    calls_count = Call.objects.filter(
        scheduled_datetime__date__range=[start_datetime.date(), end_datetime.date()]
    ).count()
    
    meetings_count = Meeting.objects.filter(
        start_datetime__date__range=[start_datetime.date(), end_datetime.date()]
    ).count()
    
    return JsonResponse({
        'tasks': tasks_count,
        'calls': calls_count,
        'meetings': meetings_count,
        'total': tasks_count + calls_count + meetings_count,
        'date_range': {
            'start': start_date,
            'end': end_date
        }
    })
