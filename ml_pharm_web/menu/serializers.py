from rest_framework import serializers
from .models import Menu


class MenuSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)

        if not data['slug'].startswith('/'):
            data['slug'] = '/' + data['slug'].lstrip('/')  
            
        return data
    
    class Meta:
        model = Menu
        fields = ['title', 'slug']
