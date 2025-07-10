from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from operator import attrgetter
from .models import Account
from tasks.models import Task, Call, Meeting


class AccountListView(LoginRequiredMixin, ListView):
    model = Account
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'
    paginate_by = 25
    
    def get_queryset(self):
        return Account.objects.select_related('assigned_to').order_by('-created_at')


class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account
    template_name = 'accounts/account_detail.html'
    context_object_name = 'account'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = self.get_object()
        
        # Initialize empty lists for activities
        activities = []
        
        try:
            # Get tasks directly related to this account using GenericForeignKey
            account_content_type = ContentType.objects.get_for_model(Account)
            tasks = Task.objects.filter(
                content_type=account_content_type,
                object_id=account.pk
            ).select_related('assigned_to', 'created_by')
            activities.extend(list(tasks))
        except Exception as e:
            print(f"Error getting tasks: {e}")
        
        try:
            # Get calls directly related to this account only
            calls = Call.objects.filter(
                related_account=account
            ).select_related('assigned_to', 'created_by')
            activities.extend(list(calls))
        except Exception as e:
            print(f"Error getting calls: {e}")
        
        try:
            # Get meetings directly related to this account only  
            meetings = Meeting.objects.filter(
                related_account=account
            ).select_related('assigned_to', 'created_by')
            activities.extend(list(meetings))
        except Exception as e:
            print(f"Error getting meetings: {e}")
        
        # Sort all activities by created_at and add activity type
        try:
            activities = sorted(
                activities,
                key=attrgetter('created_at'),
                reverse=True
            )[:15]  # Show only the latest 15 activities
            
            # Add activity type for template use
            for activity in activities:
                activity.activity_type = activity.__class__.__name__
                
        except Exception as e:
            print(f"Error sorting activities: {e}")
            activities = []
        
        context['activities'] = activities
        return context


class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    template_name = 'accounts/account_form.html'
    fields = ['name', 'account_type', 'industry', 'website', 'phone', 'email',
              'billing_street', 'billing_city', 'billing_state', 'billing_postal_code', 'billing_country',
              'annual_revenue', 'employees', 'description', 'assigned_to']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Account created successfully.')
        return super().form_valid(form)


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    template_name = 'accounts/account_form.html'
    fields = ['name', 'account_type', 'industry', 'website', 'phone', 'email',
              'billing_street', 'billing_city', 'billing_state', 'billing_postal_code', 'billing_country',
              'annual_revenue', 'employees', 'description', 'assigned_to']
    
    def form_valid(self, form):
        messages.success(self.request, 'Account updated successfully.')
        return super().form_valid(form)


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = Account
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('accounts:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Account deleted successfully.')
        return super().delete(request, *args, **kwargs)
