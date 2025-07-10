from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Tasks
    path('', views.TaskListView.as_view(), name='list'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='detail'),
    path('create/', views.TaskCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.TaskUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='delete'),
    
    # Calls
    path('calls/', views.CallListView.as_view(), name='call_list'),
    path('calls/<int:pk>/', views.CallDetailView.as_view(), name='call_detail'),
    path('calls/create/', views.CallCreateView.as_view(), name='call_create'),
    path('calls/<int:pk>/edit/', views.CallUpdateView.as_view(), name='call_edit'),
    path('calls/<int:pk>/delete/', views.CallDeleteView.as_view(), name='call_delete'),
    
    # Meetings
    path('meetings/', views.MeetingListView.as_view(), name='meeting_list'),
    path('meetings/<int:pk>/', views.MeetingDetailView.as_view(), name='meeting_detail'),
    path('meetings/create/', views.MeetingCreateView.as_view(), name='meeting_create'),
    path('meetings/<int:pk>/edit/', views.MeetingUpdateView.as_view(), name='meeting_edit'),
    path('meetings/<int:pk>/delete/', views.MeetingDeleteView.as_view(), name='meeting_delete'),
]
