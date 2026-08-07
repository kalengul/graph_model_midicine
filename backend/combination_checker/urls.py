"""
combination_checker/urls.py
"""

from django.urls import path

from .views import (
    ReportListCreateView,
    ReportDetailView,
    ReportStatusView,
    ReportCancelView,
    ReportDownloadView,
    LatestReportView,
    LatestReportForWeightView,
)

app_name = "combination_checker"

urlpatterns = [
    # Основные маршруты
    path("reports/", ReportListCreateView.as_view(), name="report-list-create"),
    path("reports/<int:pk>/", ReportDetailView.as_view(), name="report-detail"),

    # Кастомные действия
    path("reports/<int:pk>/status/", ReportStatusView.as_view(), name="report-status"),
    path("reports/<int:pk>/cancel/", ReportCancelView.as_view(), name="report-cancel"),
    path("reports/<int:pk>/download/", ReportDownloadView.as_view(), name="report-download"),

    # Служебные
    path("reports/latest/", LatestReportView.as_view(), name="report-latest"),
    path("reports/latest-for-weight/", LatestReportForWeightView.as_view(), name="report-latest-for-weight"),
]
