from django.urls import path
from . import views

app_name = 'opportunities'

urlpatterns = [
    path('', views.OpportunityListView.as_view(), name='list'),
    path('<int:pk>/', views.OpportunityDetailView.as_view(), name='detail'),
    path('create/', views.OpportunityCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.OpportunityUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.OpportunityDeleteView.as_view(), name='delete'),
]
