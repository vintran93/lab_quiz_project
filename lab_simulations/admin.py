# ===== lab_simulations/admin.py =====
from django.contrib import admin
from .models import LabSimulation

@admin.register(LabSimulation)
class LabSimulationAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'task']
    readonly_fields = ['created_at', 'updated_at']

# ===== requirements.txt =====
# Django==4.2.7
# Pillow==10.1.0