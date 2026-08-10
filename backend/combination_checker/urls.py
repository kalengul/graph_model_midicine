"""
combination_checker/urls.py
"""

from django.urls import path

from .views import (
    ReportListCreateView,
    ReportDetailView,
    ReportCancelView,
    ReportDownloadView,
    LatestCompletedReportView,
    LatestRunningReportView,
    RunningReportCancelView
)

app_name = "combination_checker"

urlpatterns = [
    # Основные маршруты
    path("reports/", ReportListCreateView.as_view(), name="report-list-create"),
    path("reports/<int:pk>/", ReportDetailView.as_view(), name="report-detail"),

    # Кастомные действия
    path("reports/<int:pk>/cancel/", ReportCancelView.as_view(), name="report-cancel"),
    path("reports/<int:pk>/download/", ReportDownloadView.as_view(), name="report-download"),

    # Служебные
    path("reports/latest-completed/", LatestCompletedReportView.as_view(), name="report-completed"),
    path("reports/running/", LatestRunningReportView.as_view(), name="report-running"),
    path("reports/running/cancel/", RunningReportCancelView.as_view(), name="report-running-cancel"),
]
