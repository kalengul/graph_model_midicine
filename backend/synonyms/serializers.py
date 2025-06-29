import os

from rest_framework import serializers
from .models import SynonymGroup, Synonym, SynonymStatus


class SynonymGroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SynonymGroup
        fields = ("name", "is_completed")

class SynonymGroupListSerializer(serializers.ModelSerializer):
    sg_id = serializers.IntegerField(source="id")
    sg_name = serializers.CharField(source="name")
    is_completed = serializers.BooleanField()

    class Meta:
        model = SynonymGroup
        fields = ("sg_id", "sg_name", "is_completed")
 

class SynonymListSerializer(serializers.ModelSerializer):
    s_id = serializers.IntegerField(source="id")
    s_name = serializers.CharField(source="name")
    st_id = serializers.SerializerMethodField()

    class Meta:
        model = Synonym
        fields = ("s_id", "s_name", "st_id")

    def get_st_id(self, obj):
        """Обработка идентификатора статуса синонимов."""
        return obj.st_id if obj.st_id else None


class SynonymItemSerializer(serializers.Serializer):
    s_id = serializers.IntegerField()
    st_id = serializers.IntegerField(help_text="Новый флаг изменения/удаления")

        
class SynonymUpdateSerializer(serializers.Serializer):
    sg_id = serializers.IntegerField()
    list_id = SynonymItemSerializer(many=True)

    def validate_sg_id(self, value):
        if not SynonymGroup.objects.filter(id=value).exists():
            raise serializers.ValidationError("Группа с указанным ID не существует")
        
        return value

    def validate(self, attrs):
        if not attrs.get("list_id"):
            raise serializers.ValidationError({"list_id": "Список не может быть пустым"})
        
        return attrs


class SynonymCreateSerializer(serializers.Serializer):
     sg_id = serializers.IntegerField()
     names = serializers.ListField(
         child=serializers.CharField(max_length=255),
         allow_empty=False,
         help_text="Список текстов новых синонимов"
     )


class FileUploadSerializer(serializers.Serializer):
    """Сериализатор для входных файлов с синоннимами."""

    file = serializers.FileField()

    def validate_file(self, file):
        """Проверка файла."""
        valid_extensions = ['.json']
        ext = os.path.splitext(file.name)[1].lower()

        if ext not in valid_extensions:
            raise serializers.ValidationError(
                f'Неверное расширение файла: {ext}. '
                f'Разрешены только: {valid_extensions}'
            )
        return file


class SynonymStatusSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и чтения статуса синонима."""

    st_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        """Настройка"""

        model = SynonymStatus
        fields = ['st_id', 'st_name', 'st_code']


class ChangeSynonymStatusSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения статуса синонима."""

    st_id = serializers.IntegerField(source='id')
    st_name = serializers.CharField(read_only=True)

    class Meta:
        """Настройка."""

        model = SynonymStatus
        fields = ['st_id', 'st_name', 'st_code']
        extra_kwargs = {
            'st_code': {'required': True},
        }

    def update(self, instance, validated_data):
        instance.st_code = validated_data.get('st_code', instance.st_code)
        instance.save()
        return instance
