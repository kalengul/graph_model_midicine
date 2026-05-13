from rest_framework import serializers
from logging_system.models import SystemState

class SystemStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemState
        fields = [
            'logging_enabled',
            'drugs_file_name',
            'drugs_file_hash',
            'drugs_file_uploaded_at',
            'weights_file_name',
            'weights_file_hash',
            'weights_file_uploaded_at',
            'updated_at',
            'commit_hash',
        ]