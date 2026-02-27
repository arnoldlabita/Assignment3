from django.urls import path
from .views import DashboardView, AssetListView, AssetCreateView, SignUpView, MaintenanceCreateView
from . import views

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('list/', AssetListView.as_view(), name='asset-list'),
    path('create/', AssetCreateView.as_view(), name='asset-create'),
    path('register/', SignUpView.as_view(), name='register'),
    path('asset/<int:pk>/maintain/', MaintenanceCreateView.as_view(), name='maintenance-add'),
    path('export/csv/', views.export_assets_csv, name='export-assets-csv'),
]