from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Sum, Q, Avg, F
from django.utils import timezone
from datetime import timedelta, datetime
from django.http import JsonResponse
import json

from accounts.models import Account
from contacts.models import Contact
from leads.models import Lead
from opportunities.models import Opportunity
from tasks.models import Task, Call, Meeting
from campaigns.models import Campaign


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get basic counts
        context['total_accounts'] = Account.objects.count()
        context['total_contacts'] = Contact.objects.count()
        context['total_leads'] = Lead.objects.count()
        context['total_opportunities'] = Opportunity.objects.exclude(sales_stage__in=['closed_won', 'closed_lost']).count()
        
        # Get user's tasks
        context['my_tasks'] = Task.objects.filter(
            assigned_to=self.request.user,
            status__in=['not_started', 'in_progress']
        ).order_by('due_date')[:5]
        
        # Get recent activities (leads, opportunities)
        context['recent_leads'] = Lead.objects.order_by('-created_at')[:5]
        context['recent_opportunities'] = Opportunity.objects.order_by('-created_at')[:5]
        
        # Sales pipeline data
        pipeline_data = Opportunity.objects.exclude(sales_stage__in=['closed_won', 'closed_lost']).values('sales_stage').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        context['pipeline_data'] = pipeline_data
        
        # Lead conversion data
        total_leads = Lead.objects.count()
        converted_leads = Lead.objects.filter(status='converted').count()
        context['conversion_rate'] = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Monthly sales data (for chart)
        now = timezone.now()
        monthly_sales = []
        for i in range(6):
            month_start = now.replace(day=1) - timedelta(days=30*i)
            month_end = month_start.replace(day=28) + timedelta(days=4)
            month_end = month_end.replace(day=1) - timedelta(days=1)
            
            sales = Opportunity.objects.filter(
                sales_stage='closed_won',
                updated_at__range=[month_start, month_end]
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_sales.append({
                'month': month_start.strftime('%B'),
                'sales': float(sales)
            })
        
        context['monthly_sales'] = list(reversed(monthly_sales))
        
        return context


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Sales by stage
        context['sales_by_stage'] = Opportunity.objects.values('sales_stage').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        )
        
        # Leads by source
        context['leads_by_source'] = Lead.objects.values('lead_source').annotate(
            count=Count('id')
        )
        
        # Top performing accounts
        context['top_accounts'] = Account.objects.annotate(
            opportunity_count=Count('opportunities'),
            total_revenue=Sum('opportunities__amount', filter=Q(opportunities__sales_stage='closed_won'))
        ).order_by('-total_revenue')[:10]
        
        return context


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/analytics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Time period calculations
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_quarter = now.replace(month=((now.month-1)//3)*3+1, day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        thirty_days_ago = now - timedelta(days=30)
        
        # Activity Metrics
        context['calls_this_month'] = Call.objects.filter(created_at__gte=start_of_month).count()
        context['meetings_this_month'] = Meeting.objects.filter(created_at__gte=start_of_month).count()
        context['tasks_this_month'] = Task.objects.filter(created_at__gte=start_of_month).count()
        
        # Sales Metrics
        context['deals_closed_this_month'] = Opportunity.objects.filter(
            sales_stage='closed_won',
            updated_at__gte=start_of_month
        ).count()
        
        context['pipeline_value'] = Opportunity.objects.exclude(
            sales_stage__in=['closed_won', 'closed_lost']
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        context['revenue_this_month'] = Opportunity.objects.filter(
            sales_stage='closed_won',
            updated_at__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        context['revenue_this_quarter'] = Opportunity.objects.filter(
            sales_stage='closed_won',
            updated_at__gte=start_of_quarter
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        context['revenue_this_year'] = Opportunity.objects.filter(
            sales_stage='closed_won',
            updated_at__gte=start_of_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Conversion Metrics
        total_leads = Lead.objects.count()
        converted_leads = Lead.objects.filter(status='converted').count()
        context['lead_conversion_rate'] = (converted_leads / total_leads * 100) if total_leads > 0 else 0
        
        # Average deal size
        context['average_deal_size'] = Opportunity.objects.filter(
            sales_stage='closed_won'
        ).aggregate(avg=Avg('amount'))['avg'] or 0
        
        return context


def analytics_data(request):
    """API endpoint for chart data"""
    chart_type = request.GET.get('type', 'sales_pipeline')
    
    if chart_type == 'sales_pipeline':
        data = list(Opportunity.objects.exclude(
            sales_stage__in=['closed_won', 'closed_lost']
        ).values('sales_stage').annotate(
            count=Count('id'),
            total_amount=Sum('amount')
        ))
        
    elif chart_type == 'monthly_revenue':
        now = timezone.now()
        data = []
        for i in range(12):
            month_start = (now.replace(day=1) - timedelta(days=30*i)).replace(day=1)
            month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            
            revenue = Opportunity.objects.filter(
                sales_stage='closed_won',
                updated_at__range=[month_start, month_end]
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            data.append({
                'month': month_start.strftime('%b %Y'),
                'revenue': float(revenue)
            })
        data.reverse()
        
    elif chart_type == 'activity_breakdown':
        now = timezone.now()
        start_of_month = now.replace(day=1)
        
        data = {
            'calls': Call.objects.filter(created_at__gte=start_of_month).count(),
            'meetings': Meeting.objects.filter(created_at__gte=start_of_month).count(),
            'tasks': Task.objects.filter(created_at__gte=start_of_month).count(),
        }
        
    elif chart_type == 'lead_sources':
        data = list(Lead.objects.values('lead_source').annotate(
            count=Count('id')
        ).order_by('-count'))
        
    elif chart_type == 'deals_by_stage':
        data = list(Opportunity.objects.values('sales_stage').annotate(
            count=Count('id')
        ))
        
    elif chart_type == 'call_outcomes':
        data = list(Call.objects.exclude(call_result='').values('call_result').annotate(
            count=Count('id')
        ).order_by('-count'))
        
    elif chart_type == 'meeting_types':
        data = list(Meeting.objects.values('meeting_type').annotate(
            count=Count('id')
        ))
        
    elif chart_type == 'weekly_activities':
        data = []
        for i in range(7):
            day = timezone.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            calls = Call.objects.filter(created_at__range=[day_start, day_end]).count()
            meetings = Meeting.objects.filter(created_at__range=[day_start, day_end]).count()
            tasks = Task.objects.filter(created_at__range=[day_start, day_end]).count()
            
            data.append({
                'day': day.strftime('%a'),
                'calls': calls,
                'meetings': meetings,
                'tasks': tasks
            })
        data.reverse()
    
    else:
        data = []
    
    return JsonResponse(data, safe=False)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/profile.html'
