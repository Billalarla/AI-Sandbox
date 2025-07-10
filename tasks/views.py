from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Task, Call, Meeting


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 25
    
    def get_queryset(self):
        return Task.objects.select_related('assigned_to').order_by('due_date')


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['subject', 'status', 'priority', 'task_type', 'due_date', 'start_date', 'description', 'assigned_to']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Task created successfully.')
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    template_name = 'tasks/task_form.html'
    fields = ['subject', 'status', 'priority', 'task_type', 'due_date', 'start_date', 'description', 'assigned_to']
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully.')
        return super().form_valid(form)


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks:list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Task deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Call Views
class CallListView(LoginRequiredMixin, ListView):
    model = Call
    template_name = 'tasks/call_list.html'
    context_object_name = 'calls'
    paginate_by = 25
    
    def get_queryset(self):
        return Call.objects.select_related('assigned_to', 'related_contact', 'related_account').order_by('-scheduled_datetime')


class CallDetailView(LoginRequiredMixin, DetailView):
    model = Call
    template_name = 'tasks/call_detail.html'
    context_object_name = 'call'


class CallCreateView(LoginRequiredMixin, CreateView):
    model = Call
    template_name = 'tasks/call_form.html'
    fields = ['subject', 'call_type', 'status', 'phone_number', 'scheduled_datetime', 'description', 
              'related_account', 'related_contact', 'related_lead', 'related_opportunity', 'assigned_to']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Call created successfully.')
        return super().form_valid(form)


class CallUpdateView(LoginRequiredMixin, UpdateView):
    model = Call
    template_name = 'tasks/call_form.html'
    fields = ['subject', 'call_type', 'status', 'call_result', 'phone_number', 'scheduled_datetime', 
              'actual_start_time', 'actual_end_time', 'duration_minutes', 'description', 'call_notes',
              'related_account', 'related_contact', 'related_lead', 'related_opportunity', 'assigned_to']
    
    def form_valid(self, form):
        messages.success(self.request, 'Call updated successfully.')
        return super().form_valid(form)


class CallDeleteView(LoginRequiredMixin, DeleteView):
    model = Call
    template_name = 'tasks/call_confirm_delete.html'
    success_url = reverse_lazy('tasks:call_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Call deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Meeting Views
class MeetingListView(LoginRequiredMixin, ListView):
    model = Meeting
    template_name = 'tasks/meeting_list.html'
    context_object_name = 'meetings'
    paginate_by = 25
    
    def get_queryset(self):
        return Meeting.objects.select_related('assigned_to', 'primary_contact', 'related_account').order_by('-start_datetime')


class MeetingDetailView(LoginRequiredMixin, DetailView):
    model = Meeting
    template_name = 'tasks/meeting_detail.html'
    context_object_name = 'meeting'


class MeetingCreateView(LoginRequiredMixin, CreateView):
    model = Meeting
    template_name = 'tasks/meeting_form.html'
    fields = ['subject', 'meeting_type', 'status', 'location', 'meeting_url', 'start_datetime', 'end_datetime',
              'agenda', 'primary_contact', 'attendees_notes', 'related_account', 'related_contact', 
              'related_lead', 'related_opportunity', 'assigned_to']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Meeting created successfully.')
        return super().form_valid(form)


class MeetingUpdateView(LoginRequiredMixin, UpdateView):
    model = Meeting
    template_name = 'tasks/meeting_form.html'
    fields = ['subject', 'meeting_type', 'status', 'location', 'meeting_url', 'start_datetime', 'end_datetime',
              'duration_minutes', 'agenda', 'meeting_notes', 'outcome', 'primary_contact', 'attendees_notes',
              'related_account', 'related_contact', 'related_lead', 'related_opportunity', 'assigned_to']
    
    def form_valid(self, form):
        messages.success(self.request, 'Meeting updated successfully.')
        return super().form_valid(form)


class MeetingDeleteView(LoginRequiredMixin, DeleteView):
    model = Meeting
    template_name = 'tasks/meeting_confirm_delete.html'
    success_url = reverse_lazy('tasks:meeting_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Meeting deleted successfully.')
        return super().delete(request, *args, **kwargs)
