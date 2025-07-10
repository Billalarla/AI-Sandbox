from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Contact


class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    template_name = 'contacts/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 25
    
    def get_queryset(self):
        return Contact.objects.select_related('account', 'assigned_to').order_by('-created_at')


class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    template_name = 'contacts/contact_detail.html'
    context_object_name = 'contact'


class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    template_name = 'contacts/contact_form.html'
    fields = ['salutation', 'first_name', 'last_name', 'title', 'account', 'email', 'phone', 'mobile',
              'mailing_street', 'mailing_city', 'mailing_state', 'mailing_postal_code', 'mailing_country',
              'department', 'reports_to', 'lead_source', 'do_not_call', 'email_opt_out', 'description', 'assigned_to']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Contact created successfully.')
        return super().form_valid(form)


class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    template_name = 'contacts/contact_form.html'
    fields = ['salutation', 'first_name', 'last_name', 'title', 'account', 'email', 'phone', 'mobile',
              'mailing_street', 'mailing_city', 'mailing_state', 'mailing_postal_code', 'mailing_country',
              'department', 'reports_to', 'lead_source', 'do_not_call', 'email_opt_out', 'description', 'assigned_to']
    
    def form_valid(self, form):
        messages.success(self.request, 'Contact updated successfully.')
        return super().form_valid(form)


class ContactDeleteView(LoginRequiredMixin, DeleteView):
    model = Contact
    template_name = 'contacts/contact_confirm_delete.html'
    success_url = reverse_lazy('contacts:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Contact deleted successfully.')
        return super().delete(request, *args, **kwargs)
