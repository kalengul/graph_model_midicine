from rest_framework import serializers


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField()
    role = serializers.CharField()

class MessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField(required=False)

class TokenCheckRequestSerializer(serializers.Serializer):
    username = serializers.CharField()

class TokenCheckResponseSerializer(serializers.Serializer):
    username = serializers.CharField()