from rest_framework import serializers
from .models import SynonymGroup, Synonym


class SynonymGroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SynonymGroup
        fields = ("name", "is_completed")

class SynonymGroupListSerializer(serializers.ModelSerializer):
    sg_id = serializers.IntegerField(source="id")
    sg_name = serializers.CharField(source="name")
    completed = serializers.BooleanField(source="is_completed")

    class Meta:
        model = SynonymGroup
        fields = ("sg_id", "sg_name", "completed")
 

class SynonymListSerializer(serializers.ModelSerializer):
    s_id = serializers.IntegerField(source="id")
    s_name = serializers.CharField(source="name")

    class Meta:
        model = Synonym
        fields = ("s_id", "s_name", "is_changed")


class SynonymItemSerializer(serializers.Serializer):
    s_id = serializers.IntegerField()
    status = serializers.BooleanField(help_text="Новый флаг изменения/удаления")

        
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
     