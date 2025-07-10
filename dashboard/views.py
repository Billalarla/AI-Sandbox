from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from accounts.models import Account
from contacts.models import Contact
from leads.models import Lead
from opportunities.models import Opportunity
from tasks.models import Task
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


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/profile.html'
