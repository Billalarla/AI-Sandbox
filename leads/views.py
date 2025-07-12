from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Lead
from .forms import LeadForm


class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    template_name = 'leads/lead_list.html'
    context_object_name = 'leads'
    paginate_by = 25
    
    def get_queryset(self):
        return Lead.objects.select_related('assigned_to').order_by('-created_at')


class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    template_name = 'leads/lead_detail.html'
    context_object_name = 'lead'


class LeadCreateView(LoginRequiredMixin, CreateView):
    model = Lead
    form_class = LeadForm
    template_name = 'leads/lead_form.html'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Lead created successfully.')
        return super().form_valid(form)


class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    form_class = LeadForm
    template_name = 'leads/lead_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Lead updated successfully.')
        return super().form_valid(form)


class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    template_name = 'leads/lead_confirm_delete.html'
    success_url = reverse_lazy('leads:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Lead deleted successfully.')
        return super().delete(request, *args, **kwargs)


class LeadConvertView(LoginRequiredMixin, View):
    def post(self, request, pk):
        lead = Lead.objects.get(pk=pk)
        # Convert lead to account and contact
        # This is a simplified version - you can expand this
        lead.status = 'converted'
        lead.save()
        messages.success(request, f'Lead {lead.full_name} converted successfully.')
        return redirect('leads:detail', pk=pk)
