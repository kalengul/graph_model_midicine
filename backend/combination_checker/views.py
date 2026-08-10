"""
combination_checker/views.py
"""

from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView

from combination_checker.utils.custom_response import CustomResponse

from combination_checker.models import CombinationReport

from combination_checker.serializers import (
    CombinationReportCreateSerializer,
    CombinationReportListSerializer,
    CombinationReportSerializer,
)

from combination_checker.services.report_service import ReportService
from combination_checker.services.task_runner import TaskRunner


class ReportMixin:
    report_service = ReportService()

    def get_report(self, pk):
        return get_object_or_404(
            CombinationReport,
            pk=pk,
        )


class ReportListCreateView(APIView):
    """
    GET  /reports/
    POST /reports/
    """

    report_service = ReportService()

    def get(self, request):
        queryset = (
            CombinationReport.objects
            .order_by("-created_at")
        )

        serializer = (
            CombinationReportListSerializer(
                queryset,
                many=True,
            )
        )

        return CustomResponse(
            data=serializer.data,
            message="Reports retrieved successfully.",
        )

    @transaction.atomic
    def post(self, request):
        # ------------------------------------------------------
        # Проверяем единственный активный процесс
        # ------------------------------------------------------

        active_report = (
            CombinationReport.objects
            .filter(is_active=True)
            .first()
        )

        if active_report is not None:
            return CustomResponse(
                data={
                    "active_report_id": active_report.pk,
                },
                status=status.HTTP_409_CONFLICT,
                message="Another combination report is already running.",
            )

        # ------------------------------------------------------
        # Валидируем запрос
        # ------------------------------------------------------

        serializer = (
            CombinationReportCreateSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        # ------------------------------------------------------
        # Создаём отчёт
        # ------------------------------------------------------

        report = (
            self.report_service.create(
                **serializer.validated_data
            )
        )

        # ------------------------------------------------------
        # Атомарно занимаем единственный слот
        # ------------------------------------------------------

        if not CombinationReport.objects.claim_active(report.pk):
            return CustomResponse(
                data={
                    "active_report_id": active_report.pk,
                },
                status=status.HTTP_409_CONFLICT,
                message="Another combination report is already running.",
            )

        # ------------------------------------------------------
        # Запускаем обычный background thread/process
        # ------------------------------------------------------

        transaction.on_commit(
            lambda: TaskRunner.start(
                report.pk
            )
        )

        report.refresh_from_db()

        output_serializer = (
            CombinationReportSerializer(
                report,
                context={
                    "request": request
                },
            )
        )

        return CustomResponse(
            data=output_serializer.data,
            status=status.HTTP_201_CREATED,
            message="Report created successfully.",
            http_status=status.HTTP_201_CREATED,
            headers={
                "Location": f"/reports/{report.pk}/"
            },
        )


class ReportDetailView(
    APIView,
    ReportMixin,
):
    """
    GET /reports/<id>/
    DELETE /reports/<id>/
    """

    def get(
        self,
        request,
        pk,
    ):
        report = self.get_report(pk)

        serializer = (
            CombinationReportSerializer(
                report,
                context={
                    "request": request
                },
            )
        )

        return CustomResponse(
            data=serializer.data,
            message="Report retrieved successfully.",
        )

    def delete(
        self,
        request,
        pk,
    ):
        report = self.get_report(pk)

        if report.is_active:
            return CustomResponse(
                data={},
                status=status.HTTP_409_CONFLICT,
                message="Report is active. Cancel it first.",
            )

        self.report_service.delete(
            report,
            delete_file=True,
        )

        return CustomResponse(
            data={},
            status=status.HTTP_204_NO_CONTENT,
            message="Report deleted successfully.",
        )

class ReportCancelView(
    APIView,
    ReportMixin,
):
    """
    GET /reports/<id>/cancel/
    """

    def get(
        self,
        request,
        pk,
    ):
        report = self.get_report(pk)

        if not report.is_active:
            return CustomResponse(
                data={},
                status=status.HTTP_400_BAD_REQUEST,
                message="Report is not active.",
            )

        updated = (
            CombinationReport.objects
            .filter(
                pk=report.pk,
                is_active=True,
                status=CombinationReport.Status.RUNNING,
            )
            .update(
                status=CombinationReport.Status.CANCELED,
                is_active=False,
            )
        )

        if not updated:
            return CustomResponse(
                data={},
                status=status.HTTP_409_CONFLICT,
                message="Report is no longer running.",
            )

        return CustomResponse(
            data={
                "report_id": report.pk,
            },
            status=status.HTTP_202_ACCEPTED,
            message="Cancellation requested.",
        )


class ReportDownloadView(
    APIView,
    ReportMixin,
):
    """
    GET /reports/<id>/download/
    """

    def get(
        self,
        request,
        pk,
    ):
        report = self.get_report(pk)

        file_path = (
            self.report_service
            .get_download_path(report)
        )

        if (
            file_path is None
            or not file_path.is_file()
        ):
            raise Http404(
                "Result file not found."
            )

        return FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=file_path.name,
        )

class LatestCompletedReportView(APIView):
    report_service = ReportService()

    def get(self, request):
        report = (
            self.report_service
            .latest()
        )

        if report is None:
            return CustomResponse(
                data={},
                status=status.HTTP_404_NOT_FOUND,
                message="No completed reports found.",
            )

        serializer = (
            CombinationReportSerializer(
                report,
                context={
                    "request": request
                },
            )
        )

        return CustomResponse(
            data=serializer.data,
            message="Latest completed report retrieved successfully.",
        )


class LatestRunningReportView(APIView):
    report_service = ReportService()

    def get(self, request):
        report = (
            self.report_service
            .latest_running()
        )

        if report is None:
            return CustomResponse(
                data={},
                status=status.HTTP_404_NOT_FOUND,
                message="No running reports found.",
            )

        serializer = (
            CombinationReportSerializer(
                report,
                context={
                    "request": request
                },
            )
        )

        return CustomResponse(
            data=serializer.data,
            message="Running report retrieved successfully.",
        )
    
class LatestCompletedReportDownloadView(APIView):
    report_service = ReportService()

    def get(self, request):
        report = (
            self.report_service.latest()
        )

        if report is None:
            raise Http404(
                "No completed reports found."
            )

        file_path = (
            self.report_service.get_download_path(report)
        )

        if (
            file_path is None
            or not file_path.is_file()
        ):
            raise Http404(
                "Result file not found."
            )

        return FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=file_path.name,
        )
    

class RunningReportCancelView(APIView):
    report_service = ReportService()

    def get(self, request):
        report = (
            self.report_service
            .latest_running()
        )

        if report is None:
            return CustomResponse(
                data={},
                status=status.HTTP_404_NOT_FOUND,
                message="No running reports found.",
            )

        updated = (
            CombinationReport.objects
            .filter(
                pk=report.pk,
                is_active=True,
                status=CombinationReport.Status.RUNNING,
            )
            .update(
                status=CombinationReport.Status.CANCELED,
                is_active=False,
            )
        )

        if not updated:
            return CustomResponse(
                data={},
                status=status.HTTP_409_CONFLICT,
                message="Report is no longer running.",
            )

        return CustomResponse(
            data={
                "report_id": report.pk,
            },
            status=status.HTTP_202_ACCEPTED,
            message="Cancellation requested.",
        )