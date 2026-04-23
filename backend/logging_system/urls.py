from django.urls import path
from .views import SystemStateView, LoggingToggleView, LogsExportView, LogsDeleteView

urlpatterns = [
    path('logs/state/', SystemStateView.as_view(), name='system-state'),
    path('logs/toggle/', LoggingToggleView.as_view(), name='logging-toggle'),
    path('logs/export/', LogsExportView.as_view(), name='logs-export'),
    path('logs/delete/', LogsDeleteView.as_view(), name='logs-delete'),
]