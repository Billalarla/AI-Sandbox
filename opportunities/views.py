from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Opportunity
from .forms import OpportunityForm


class OpportunityListView(LoginRequiredMixin, ListView):
    model = Opportunity
    template_name = 'opportunities/opportunity_list.html'
    context_object_name = 'opportunities'
    paginate_by = 25
    
    def get_queryset(self):
        return Opportunity.objects.select_related('account', 'contact', 'assigned_to').order_by('-expected_close_date')


class OpportunityDetailView(LoginRequiredMixin, DetailView):
    model = Opportunity
    template_name = 'opportunities/opportunity_detail.html'
    context_object_name = 'opportunity'


class OpportunityCreateView(LoginRequiredMixin, CreateView):
    model = Opportunity
    form_class = OpportunityForm
    template_name = 'opportunities/opportunity_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Opportunity created successfully.')
        return super().form_valid(form)


class OpportunityUpdateView(LoginRequiredMixin, UpdateView):
    model = Opportunity
    form_class = OpportunityForm
    template_name = 'opportunities/opportunity_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Opportunity updated successfully.')
        return super().form_valid(form)


class OpportunityDeleteView(LoginRequiredMixin, DeleteView):
    model = Opportunity
    template_name = 'opportunities/opportunity_confirm_delete.html'
    success_url = reverse_lazy('opportunities:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Opportunity deleted successfully.')
        return super().delete(request, *args, **kwargs)
