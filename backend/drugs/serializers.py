import logging

from rest_framework import serializers
from drugs.models import DrugGroup, Drug, Nosology
from side_effects.models import SideEffect, DrugSideEffect


logger = logging.getLogger('drugs')


class DrugGroupSerializer(serializers.ModelSerializer):
    """Сериализатор группы ЛС."""

    class Meta:
        """Настройка сериализатора."""

        model = DrugGroup
        fields = ['id', 'dg_name']

    # Проверка на дубликат
    def validate_dg_name(self, value):
        qs = DrugGroup.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        for obj in qs:
            if obj.dg_name.lower() == value.lower():
                raise serializers.ValidationError(
                    "Группа с таким названием уже существует"
                )
        return value


class DrugSerializer(serializers.ModelSerializer):
    """
    Сериализатор ЛС.

    Выполняет добавление и получение ЛС
    (в том числе связь c группой и побочными эффектами).
    """

    dg_ids = serializers.PrimaryKeyRelatedField(
        source='drug_groups',
        queryset=DrugGroup.objects.all(),
        many=True,
        required=False,
        allow_empty=True,
        error_messages={'does_not_exist': 'Группа ЛС с таким ID не найдена'}
    )

    nosology_id = serializers.PrimaryKeyRelatedField(
        source='nosology',
        queryset=Nosology.objects.all(),
        required=False,
        allow_null=True,
        error_messages={'does_not_exist': 'Нозология с таким ID не найдена'}
    )

    side_effects = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    def validate_drug_name(self, value):
        """
        Валидация названия ЛС.

        Проверяет наличие ЛС в БД перед его добавлением.
        """
        qs = Drug.objects.all()
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        for obj in qs:
            if obj.drug_name.lower() == value.lower():
                raise serializers.ValidationError(
                    f"ЛС {value} уже существует"
                )
        return value

    def create(self, validated_data):
        """Добавление ЛС."""
        drug_groups = validated_data.pop('drug_groups', [])
        side_effects_data = validated_data.pop('side_effects', [])
        drug = Drug.objects.create(**validated_data)

        if drug_groups:
            drug.drug_groups.set(drug_groups)

        logger.debug(f'side_effects_data = {side_effects_data}')
        if side_effects_data:
            passed_ids = set()

            for se in side_effects_data:
                se_id = se.get('se_id')
                rank = se.get('rank')
                passed_ids.add(se_id)

                logger.debug(f'se_id = {se_id}')
                logger.debug(f'rank = {rank}')

                try:
                    DrugSideEffect.objects.create(
                        drug=drug,
                        side_effect=SideEffect.objects.get(id=se_id),
                        probability=rank
                    )
                except SideEffect.DoesNotExist:
                    raise serializers.ValidationError(
                        f"ПД с id={se_id} не существует")
            for effect in SideEffect.objects.order_by('id').exclude(
                id__in=passed_ids):
                DrugSideEffect.objects.create(
                    drug=drug,
                    side_effect=effect)
        else:
            for effect in SideEffect.objects.order_by('id').iterator():
                DrugSideEffect.objects.create(
                    drug=drug,
                    side_effect=effect)

        return drug

    class Meta:
        """Настройка сериализатора."""
        model = Drug
        fields = ['id', 'drug_name', 'dg_ids', 'nosology_id', 'side_effects']


class DrugListRetrieveSerializer(serializers.ModelSerializer):
    """
    Сериализатор для поиска ЛС с торговыми названиями.
    """
    dg_id = serializers.SerializerMethodField()
    nosology_id = serializers.IntegerField(source='nosology.id', read_only=True, allow_null=True)
    trade_ids = serializers.SerializerMethodField()
    
    class Meta:
        model = Drug
        fields = ['id', 'drug_name', 'dg_id', 'nosology_id', 'trade_ids']
    
    def get_dg_id(self, obj) -> list[int]:
        """Получение списка ID групп ЛС."""
        return [g.id for g in obj.drug_groups.all()]
    
    def get_trade_ids(self, obj) -> list[int]:
        """Получение списка ID торговых названий."""
        return [tn.id for tn in obj.trade_names.all()]


class FileSerializer(serializers.Serializer):
    """Сериализатор для файлов."""

    file = serializers.FileField()


class DrugDataLoadSerializer(serializers.Serializer):
    file = serializers.FileField(
        required=False,
        allow_null=True,
    )


class TradeNameResponseSerializer(serializers.Serializer):
    drug_id = serializers.IntegerField()
    drug_name = serializers.CharField()
    trade_names = serializers.ListField(
        child=serializers.CharField()
    )


class DrugTradeSearchTradeNameSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class DrugTradeSearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    drug_name = serializers.CharField()
    dg_id = serializers.ListField(
        child=serializers.IntegerField()
    )
    nosology_id = serializers.IntegerField(
        allow_null=True
    )
    trade_names = DrugTradeSearchTradeNameSerializer(
        many=True
    )


class DrugTradeSearchResponseSerializer(serializers.Serializer):
    query = serializers.CharField()
    count = serializers.IntegerField()
    results = DrugTradeSearchResultSerializer(
        many=True
    )

