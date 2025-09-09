from rest_framework import serializers

from contraindications.models import Contraindication


class BaseContraindicationSerialize(serializers.ModelSerializer):
    """Класс прорадитель для сериализаторов """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        """Настройка сериализатора для противопоказаний."""

        model = Contraindication
        fields = ('id', 'name', 'weight', 'node_target')


class ContraindicationListSerializer(BaseContraindicationSerialize):
    """
    Сериализатор противопоказаний.

    Используется для запросов POST и GET
    для получения всех противопоказаний.
    """

    def validate_name(self, value):
        """
        Проверка наличия противопоказания в БД.

        Если добавляется противопоказание, которое уже есть в БД,
        вызывается иключение.
        """
        if Contraindication.objects.filter(name=value):
            raise ValueError(
                f"Противопоказание с названием '{value}' уже существует."
            )
        return value


class ContraindicationDetailSerializer(BaseContraindicationSerialize):
    """
    Сериализатор противопоказаний.

    Используется для запросов PUT, PATCH и GET
    для получения одного противопоказания по ID.
    """
