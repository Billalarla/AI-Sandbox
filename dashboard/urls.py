from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='home'),
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('analytics/data/', views.analytics_data, name='analytics_data'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
