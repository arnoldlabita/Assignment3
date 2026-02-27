from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Department, User, Asset, MaintenanceLog

# Register Department normally
admin.site.register(Department)

# Register User with the built-in UserAdmin
admin.site.register(User, UserAdmin)

admin.site.register(MaintenanceLog)

# Register Asset with a custom ModelAdmin
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'asset_type', 'cost', 'repair_cost', 'assigned_to')
