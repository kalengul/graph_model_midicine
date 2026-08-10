"""
combination_checker/serializers.py
"""

from rest_framework import serializers

from combination_checker.models import CombinationReport
from logging_system.models import SystemState


class CombinationReportCreateSerializer(
    serializers.Serializer
):
    """
    Запуск новой проверки комбинаций.
    """

    name = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )

    max_combination_size = serializers.IntegerField(
        min_value=2,
        max_value=10,
    )

    rank_name = serializers.ChoiceField(
        choices=[
            choice[0]
            for choice in CombinationReport.RANK_FIELDS
        ],
        default="rang_base",
        required=False,
    )

    def create(self, validated_data):
        state = SystemState.get_current_state()

        max_size = validated_data[
            "max_combination_size"
        ]

        name = validated_data.get("name")

        if not name:
            name = (
                f"Combinations up to {max_size}"
            )

        return CombinationReport.objects.create(
            name=name,
            max_combination_size=max_size,
            rank_name=validated_data["rank_name"],
            weight_version_name=(
                state.weights_file_name or ""
            ),
            weight_version_hash=(
                state.weights_file_hash or ""
            ),
            weight_version_uploaded_at=(
                state.weights_file_uploaded_at
            ),
            status=CombinationReport.Status.RUNNING,
            is_active=False,
        )


class CombinationReportSerializer(
    serializers.ModelSerializer
):
    progress = serializers.SerializerMethodField()

    class Meta:
        model = CombinationReport

        fields = (
            "id",
            "name",
            "status",
            "started_at",
            "finished_at",
            "duration",
            "max_combination_size",
            "weight_version_name",
            "total_iterations",
            "completed_iterations",
            "checked_combinations",
            "found_combinations",
            "pruned_combinations",
            "progress",
            "error_message",
        )

        read_only_fields = fields

    def get_progress(self, obj):
        return round(obj.progress, 2)


class CombinationReportListSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = CombinationReport

        fields = (
            "id",
            "name",
            "status",
            "created_at",
            "finished_at",
            "progress",
            "max_combination_size",
            "weight_version_name",
        )