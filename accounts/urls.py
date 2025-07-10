from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.AccountListView.as_view(), name='list'),
    path('<int:pk>/', views.AccountDetailView.as_view(), name='detail'),
    path('create/', views.AccountCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.AccountUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.AccountDeleteView.as_view(), name='delete'),
]
