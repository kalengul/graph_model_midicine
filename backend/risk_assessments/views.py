"""
View: POST /api/v1.0/risk-assessments/drug-compatibility
"""
import logging

from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from risk_assessments.utils.parsers import XMLRiskAssessmentParser

from drugs.utils.custom_response import CustomResponse
from logging_system.services import CalculationLoggingService

from risk_assessments.serializers import (DrugRiskAssessmentRequestSerializer,
                                          RiskAssessmentResponseSerializer
                                          )
from risk_assessments.services import (
    ContraindicationNotFoundError,
    DrugNotFoundError,
    assess_drug_risks,
)

from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.types import OpenApiTypes

logger = logging.getLogger("risk_assessments.views")


@extend_schema_view(
    post=extend_schema(
        tags=["risk-assessments"],
        request=DrugRiskAssessmentRequestSerializer,
        responses={
            200: RiskAssessmentResponseSerializer,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT,
        },
    )
)
class DrugRiskAssessmentView(APIView):
    """
    POST /api/v1.0/risk-assessments/drug-compatibility

    Оценка рисков полифармакотерапии по названиям препаратов.
    """

    authentication_classes = [TokenAuthentication, SessionAuthentication]
    parser_classes = [JSONParser, XMLRiskAssessmentParser]

    def post(self, request):
        # 1. Валидация входных данных
        serializer = DrugRiskAssessmentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return _error_response(
                message="Некорректные входные данные",
                additional_data=serializer.errors,
            )

        drug_names: list[str] = serializer.validated_data["drugs"]
        patient_profile: dict | None = serializer.validated_data.get("patientProfile")

        # 2. Логирование запроса
        user = request.user if request.user.is_authenticated else None
        CalculationLoggingService.log_request(user, drug_names=drug_names)

        # 3. Оценка рисков
        try:
            result = assess_drug_risks(drug_names, patient_profile)

        except DrugNotFoundError as exc:
            missing_str = ", ".join(f"`{m}`" for m in exc.missing)
            return _error_response(
                message="В поле `drugs` указано некорректное значение",
                additional_data=f"Следующие препараты отсутствуют в системе: {missing_str}",
            )

        except ContraindicationNotFoundError as exc:
            missing_str = ", ".join(f"`{m}`" for m in exc.missing)
            return _error_response(
                message="В поле `contList` указано некорректное значение",
                additional_data=f"Следующие противопоказания отсутствуют в системе: {missing_str}",
            )

        except Exception:
            logger.exception("Критическая ошибка при оценке рисков")
            return CustomResponse(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Ошибка оценки рисков совместимости препаратов",
                http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return CustomResponse(
            status=status.HTTP_200_OK,
            message="Оценка рисков успешно выполнена",
            http_status=status.HTTP_200_OK,
            data=result,
        )


def _error_response(message: str, additional_data=None) -> CustomResponse:
    """Формирует стандартный 400-ответ согласно схеме ошибок проекта."""
    return CustomResponse(
        status=status.HTTP_400_BAD_REQUEST,
        message=message,
        http_status=status.HTTP_400_BAD_REQUEST,
        data={
            "title": "Некорректный запрос",
            "message": message,
            "errorCode": "BAD_REQUEST",
            "additionalData": additional_data,
        },
    )