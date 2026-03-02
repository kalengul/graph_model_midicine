from rest_framework import serializers

from .models import Graph


class GraphSerializer(serializers.ModelSerializer):
    """Сериализатор графа."""

    NAME = 'name'
    NODES = 'nodes'
    LINKS = 'links'

    class Meta:
        """Настройка сериализатора."""

        model = Graph
        fields = ('name', 'graph_json', 'graph_xml')

    def validate_graph_json(self, value):
        """Проверка наличия ключей json-словаре графа."""
        required_keys = [self.NODES, self.LINKS]
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(
                    f'В графе не хватает ключа {key}'
                )

        if not isinstance(value[self.NODES], list):
            raise serializers.ValidationError('Вершины должны быть список')
        if not isinstance(value[self.LINKS], list):
            raise serializers.ValidationError('Рёбра должны быть список')

        return value

    def validate_name(self, value):
        """
        Проверка названия графа.

        Наличие графа в БД с названием "name".
        """
        if Graph.objects.filter(name=value).exists():
            raise serializers.ValidationError('Такой граф уже есть!')

        return value


class UpdateGraphSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления графа."""

    NODES = 'nodes'
    LINKS = 'links'

    class Meta:
        """Настройка сериализатора."""

        model = Graph
        fields = ('graph_json', 'graph_xml')

    def validate_graph_json(self, value):
        """Проверка наличия ключей json-словаре графа."""
        required_keys = [self.NODES, self.LINKS]
        for key in required_keys:
            if key not in value:
                raise serializers.ValidationError(
                    f'В графе не хватает ключа {key}'
                )

        if not isinstance(value[self.NODES], list):
            raise serializers.ValidationError('Вершины должны быть список')
        if not isinstance(value[self.LINKS], list):
            raise serializers.ValidationError('Рёбра должны быть список')

        return value


class GraphListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для списка графов.

    Предназначен для GET-запрос на список графов.
    Каждый элемент списка это название и id graph.
    """

    class Meta:
        """Настройка сериализатора."""

        model = Graph
        fields = ('id', 'name')


class BayesSerializer(serializers.Serializer):
    """Сериализатор для Байеса."""

    class HumanDataSerializer(serializers.Serializer):
        """Сериализатор данных о пациенте."""

        age = serializers.CharField(required=False, allow_null=True,
                                    allow_blank=True)
        gender = serializers.CharField(required=False, allow_null=True,
                                       allow_blank=True)
        cont_list = serializers.ListField(
            child=serializers.IntegerField(required=False, allow_null=True),
            required=False, allow_empty=True, allow_null=True, default=list)

    drugs = serializers.ListField(
        child=serializers.IntegerField(), required=True
    )
    humanData = HumanDataSerializer(required=False)
