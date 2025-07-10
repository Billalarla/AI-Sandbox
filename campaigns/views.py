from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Campaign


class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = 'campaigns/campaign_list.html'
    context_object_name = 'campaigns'
    paginate_by = 25
    
    def get_queryset(self):
        return Campaign.objects.select_related('assigned_to').order_by('-start_date')


class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = 'campaigns/campaign_detail.html'
    context_object_name = 'campaign'


class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    template_name = 'campaigns/campaign_form.html'
    fields = ['name', 'status', 'campaign_type', 'start_date', 'end_date', 'budgeted_cost', 'actual_cost',
              'expected_revenue', 'expected_response', 'num_sent', 'description', 'objective', 'assigned_to']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Campaign created successfully.')
        return super().form_valid(form)


class CampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = Campaign
    template_name = 'campaigns/campaign_form.html'
    fields = ['name', 'status', 'campaign_type', 'start_date', 'end_date', 'budgeted_cost', 'actual_cost',
              'expected_revenue', 'expected_response', 'num_sent', 'description', 'objective', 'assigned_to']
    
    def form_valid(self, form):
        messages.success(self.request, 'Campaign updated successfully.')
        return super().form_valid(form)


class CampaignDeleteView(LoginRequiredMixin, DeleteView):
    model = Campaign
    template_name = 'campaigns/campaign_confirm_delete.html'
    success_url = reverse_lazy('campaigns:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Campaign deleted successfully.')
        return super().delete(request, *args, **kwargs)
