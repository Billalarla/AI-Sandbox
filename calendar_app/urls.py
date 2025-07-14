from django.urls import path
from . import views

app_name = 'calendar_app'

urlpatterns = [
    # Main calendar view
    path('', views.CalendarView.as_view(), name='calendar'),
    
    # Debug calendar view
    path('debug/', views.CalendarDebugView.as_view(), name='calendar_debug'),
    
    # Public diagnostic view (no auth required)
    path('diagnostic/', views.CalendarDiagnosticPublicView.as_view(), name='calendar_diagnostic'),
    
    # Simple calendar view
    path('simple/', views.CalendarSimpleView.as_view(), name='calendar_simple'),
    
    # Public calendar view (no auth required for testing)
    path('public/', views.CalendarPublicView.as_view(), name='calendar_public'),
    
    # Quick create view
    path('create/', views.CalendarQuickCreateView.as_view(), name='quick_create'),
    
    # Account-specific calendar
    path('account/<int:account_id>/', views.AccountCalendarView.as_view(), name='account_calendar'),
    
    # User-specific calendar
    path('user/<int:user_id>/', views.UserCalendarView.as_view(), name='user_calendar'),
    
    # API endpoints
    path('api/events/', views.calendar_events_api, name='calendar_events_api'),
    path('api/counts/', views.calendar_event_counts_api, name='calendar_counts_api'),
]
