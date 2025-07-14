from django.urls import path
from . import views
from . import api_views

app_name = 'leads'

urlpatterns = [
    # Regular views
    path('', views.LeadListView.as_view(), name='list'),
    path('<int:pk>/', views.LeadDetailView.as_view(), name='detail'),
    path('create/', views.LeadCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.LeadUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.LeadDeleteView.as_view(), name='delete'),
    path('<int:pk>/convert/', views.LeadConvertView.as_view(), name='convert'),
    
    # CVR Lead Scoring API endpoints
    path('api/<int:lead_id>/score/', api_views.LeadScoreAPIView.as_view(), name='api_score_lead'),
    path('api/bulk-score/', api_views.BulkLeadScoreAPIView.as_view(), name='api_bulk_score'),
    path('api/<int:lead_id>/cvr-data/', api_views.CVRDataAPIView.as_view(), name='api_cvr_data'),
    path('api/icp-config/', api_views.ICPConfigAPIView.as_view(), name='api_icp_config'),
    path('api/score-stats/', api_views.LeadScoreStatsAPIView.as_view(), name='api_score_stats'),
    path('api/score-all/', api_views.score_all_leads, name='api_score_all'),
    
    # New CVR Data Population API endpoints
    path('api/cvr-lookup/', api_views.CVRLookupAPIView.as_view(), name='api_cvr_lookup'),
    path('api/<int:lead_id>/populate-cvr/', api_views.PopulateLeadFromCVRAPIView.as_view(), name='api_populate_cvr'),
    path('api/create-from-cvr/', api_views.CreateLeadFromCVRAPIView.as_view(), name='api_create_from_cvr'),
]
