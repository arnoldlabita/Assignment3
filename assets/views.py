import csv

from django.views.generic import ListView, TemplateView, CreateView
from django.urls import reverse_lazy
from django.db.models import Sum, Count, Value, DecimalField
from django.db.models.functions import Coalesce
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Asset, Department, MaintenanceLog
from .forms import CustomCreationForm
from .mixins import ManagerRequiredMixin


# =====================================================
# DASHBOARD VIEW
# =====================================================
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "assets/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Total Asset Value
        context['total_asset_value'] = (
            Asset.objects.aggregate(total=Sum('cost'))['total'] or 0
        )

        # Assets Per Type
        context['assets_by_type'] = (
            Asset.objects
            .values('asset_type')
            .annotate(count=Count('id'))
        )

        # Total Repair Cost (from Maintenance Logs)
        context['total_repair_cost'] = (
            MaintenanceLog.objects.aggregate(total=Sum('cost'))['total'] or 0
        )

        # Cost by Department
        context['department_costs'] = Department.objects.annotate(
            total_cost=Coalesce(
                Sum('users__assets__cost'),
                Value(0),
                output_field=DecimalField()
            )
        )

        return context


# =====================================================
# ASSET LIST VIEW (WITH PAGINATION)
# =====================================================
class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    paginate_by = 5   # ✅ Required by activity

    def get_queryset(self):
        return (
            Asset.objects
            .select_related('assigned_to')
            .annotate(
                repair_total=Coalesce(
                    Sum('maintenance_logs__cost'),
                    Value(0),
                    output_field=DecimalField()
                )
            )
            .order_by('-created_at')
        )


# =====================================================
# ASSET CREATE VIEW
# =====================================================
class AssetCreateView(ManagerRequiredMixin, CreateView):
    model = Asset
    template_name = "assets/asset_form.html"
    fields = ['name', 'asset_type', 'cost', 'repair_cost', 'assigned_to']
    success_url = reverse_lazy('asset-list')


# =====================================================
# MAINTENANCE CREATE VIEW
# =====================================================
class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceLog
    template_name = "assets/maintenance_form.html"
    fields = ['description', 'cost', 'date_repaired']

    def form_valid(self, form):
        asset = get_object_or_404(Asset, pk=self.kwargs['pk'])
        form.instance.asset = asset
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('asset-list')


# =====================================================
# CSV EXPORT VIEW
# =====================================================
def export_assets_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="asset_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Asset Name', 'Type', 'Cost', 'Assigned User'])

    assets = Asset.objects.select_related('assigned_to').all()

    for asset in assets:
        writer.writerow([
            asset.name,
            asset.get_asset_type_display(),
            asset.cost,
            asset.assigned_to.username if asset.assigned_to else "Unassigned"
        ])

    return response


# =====================================================
# USER REGISTRATION VIEW
# =====================================================
class SignUpView(CreateView):
    form_class = CustomCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')