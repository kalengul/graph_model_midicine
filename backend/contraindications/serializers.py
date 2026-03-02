from rest_framework import serializers

from contraindications.models import Contraindication


class BaseContraindicationSerialize(serializers.ModelSerializer):
    """Класс прародитель для сериализаторов """

    cont_id = serializers.IntegerField(read_only=True, source='id')
    cont_name = serializers.CharField(source='name')
    cont_weigth = serializers.FloatField(source='weight', required=False)

    class Meta:
        """Настройка сериализатора для противопоказаний."""

        model = Contraindication
        fields = ('cont_id', 'cont_name', 'cont_weigth')


class ContraindicationListSerializer(BaseContraindicationSerialize):
    """
    Сериализатор противопоказаний.

    Используется для запросов POST и GET
    для получения всех противопоказаний.
    """

    def validate_cont_name(self, value):
        """
        Проверка наличия противопоказания в БД.

        Если добавляется противопоказание, которое уже есть в БД,
        вызывается исключение.
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
