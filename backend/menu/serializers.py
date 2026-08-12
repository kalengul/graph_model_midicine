from rest_framework import serializers
from menu.models import Menu


class MenuSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if not data['slug'].startswith('/'):
            data['slug'] = '/' + data['slug'].lstrip('/')  
            
        return data
    
    class Meta:
        model = Menu
        fields = ['title', 'slug', 'is_auth', 'group']


class MenuResultSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    message = serializers.CharField()


class MenuResponseSerializer(serializers.Serializer):
    result = MenuResultSerializer()
    data = MenuSerializer(many=True)
