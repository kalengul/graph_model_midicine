from rest_framework import serializers
from .models import SynonymGroup


class SynonymItemSerializer(serializers.Serializer):
    s_id = serializers.IntegerField()
    is_changed = serializers.BooleanField()

        
class SynonymUpdateSerializer(serializers.Serializer):
    sg_id = serializers.IntegerField()
    list_id = SynonymItemSerializer(many=True)

    # def validate_sg_id(self, value):
    #     if not SynonymGroup.objects.filter(id=value).exists():
    #         raise serializers.ValidationError("Группа с указанным ID не существует")
    #     return value

    # def validate_list_id(self, value):
    #     if not value:
    #         raise serializers.ValidationError("Список синонимов не может быть пустым")
    #     return value
    