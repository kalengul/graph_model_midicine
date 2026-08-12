"""
combination_checker/views.py
"""

from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView

from accounts.auth import bearer_token_required

from combination_checker.utils.custom_response import CustomResponse
from combination_checker.models import CombinationReport
from combination_checker.serializers import (
    CombinationReportCreateSerializer,
    CombinationReportListSerializer,
    CombinationReportSerializer,
)
from combination_checker.services.report_service import ReportService
from combination_checker.services.task_runner import TaskRunner

from drf_spectacular.utils import (extend_schema,
                                   extend_schema_view,
                                   OpenApiResponse,
                                   OpenApiTypes
                                   )


class ReportMixin:
    report_service = ReportService()

    def get_report(self, pk):
        return get_object_or_404(
            CombinationReport,
            pk=pk,
        )

@extend_schema_view(
    get=extend_schema(
        operation_id='reports_list',
        responses={
            200: OpenApiResponse(
                response=CombinationReportListSerializer(many=True),
                description='Список отчётов успешно получен.',
            ),
        },
        tags=['combination-checker'],
    ),
    post=extend_schema(
        operation_id='reports_create',
        request=CombinationReportCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=CombinationReportSerializer,
                description='Отчёт успешно создан.',
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Некорректные данные.',
            ),
            409: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Другой отчёт уже выполняется.',
            ),
        },
        tags=['combination-checker'],
    ),
)
class ReportListCreateView(APIView):
    """
    GET  /reports/
    POST /reports/
    """

    report_service = ReportService()

    @bearer_token_required
    def get(self, request):
        queryset = (
            CombinationReport.objects
            .order_by("-started_at")
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

    @bearer_token_required
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
                    "id": active_report.pk,
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
                    "id": active_report.pk,
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

        output_serializer = CombinationReportListSerializer(report)

        return CustomResponse(
            data=output_serializer.data,
            status=status.HTTP_201_CREATED,
            message="Report created successfully.",
            http_status=status.HTTP_201_CREATED,
            headers={
                "Location": f"/reports/{report.pk}/"
            },
        )

@extend_schema_view(
    get=extend_schema(
        operation_id='report_detail',
        responses={
            200: OpenApiResponse(
                response=CombinationReportSerializer,
                description='Данные отчёта успешно получены.',
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Отчёт не найден.',
            ),
        },
        tags=['combination-checker'],
    ),
    delete=extend_schema(
        operation_id='report_delete',
        responses={
            204: OpenApiResponse(
                description='Отчёт успешно удалён.',
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Отчёт не найден.',
            ),
            409: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Нельзя удалить активный отчёт.',
            ),
        },
        tags=['combination-checker'],
    ),
)
class ReportDetailView(
    APIView,
    ReportMixin,
):
    """
    GET /reports/<id>/
    DELETE /reports/<id>/
    """

    @bearer_token_required
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
    
    @bearer_token_required
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

@extend_schema_view(
    get=extend_schema(
        operation_id='report_cancel',
        responses={
            202: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Запрос на отмену отчёта принят.',
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Отчёт не является активным.',
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Отчёт не найден.',
            ),
            409: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Отчёт больше не выполняется.',
            ),
        },
        tags=['combination-checker'],
    ),
)
class ReportCancelView(
    APIView,
    ReportMixin,
):
    """
    GET /reports/<id>/cancel/
    """

    @bearer_token_required
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
                "id": report.pk,
                "status": CombinationReport.Status.CANCELED
            },
            status=status.HTTP_202_ACCEPTED,
            message="Cancellation requested.",
        )

@extend_schema_view(
    get=extend_schema(
        operation_id='report_download',
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description='Отчёт успешно скачан.',
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Отчёт или файл результата не найден.',
            ),
        },
        tags=['combination-checker'],
    ),
)
class ReportDownloadView(
    APIView,
    ReportMixin,
):
    """
    GET /reports/<id>/download/
    """
    
    @bearer_token_required
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

@extend_schema_view(
    get=extend_schema(
        operation_id='latest_completed_report',
        responses={
            200: OpenApiResponse(
                response=CombinationReportSerializer,
                description='Последний завершённый отчёт успешно получен.',
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Завершённые отчёты не найдены.',
            ),
        },
        tags=['combination-checker'],
    ),
)
class LatestCompletedReportView(APIView):
    report_service = ReportService()

    @bearer_token_required
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

@extend_schema_view(
    get=extend_schema(
        operation_id='latest_running_report',
        responses={
            200: OpenApiResponse(
                response=CombinationReportSerializer,
                description='Последний выполняющийся отчёт успешно получен.',
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Выполняющиеся отчёты не найдены.',
            ),
        },
        tags=['combination-checker'],
    ),
)
class LatestRunningReportView(APIView):
    report_service = ReportService()

    @bearer_token_required
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

@extend_schema_view(
    get=extend_schema(
        operation_id='latest_completed_report_download',
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.BINARY,
                description='Последний завершённый отчёт успешно скачан.',
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Завершённый отчёт или файл результата не найден.',
            ),
        },
        tags=['combination-checker'],
    ),
)    
class LatestCompletedReportDownloadView(APIView):
    report_service = ReportService()

    @bearer_token_required
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
    
@extend_schema_view(
    get=extend_schema(
        operation_id='running_report_cancel',
        responses={
            202: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Запрос на отмену выполняющегося отчёта принят.',
            ),
            404: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Выполняющийся отчёт не найден.',
            ),
            409: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Отчёт больше не выполняется.',
            ),
        },
        tags=['combination-checker'],
    ),
)
class RunningReportCancelView(APIView):
    report_service = ReportService()
    
    @bearer_token_required
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
                "id": report.pk,
                "status": CombinationReport.Status.CANCELED
            },
            status=status.HTTP_202_ACCEPTED,
            message="Cancellation requested.",
        )