from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from drugs.utils.custom_response import CustomResponse


class LoginUser(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return CustomResponse.response(
                status=400,
                message="Логин и пароль обязательны",
                http_status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if user is None:
            return CustomResponse.response(
                status=401,
                message="Неверные учетные данные",
                http_status=status.HTTP_401_UNAUTHORIZED
            )

        token, created = Token.objects.get_or_create(user=user)

        if user.is_superuser:
            role = "superuser"
 
        elif user.is_staff:
            role = "staff"
 
        else:
            role = "no_role"

        return CustomResponse.response(
            data={
                "token": token.key, 
                "username": username, 
                "role": role,
            },
            status=200,
            message="Авторизация прошла успешно",
            http_status=status.HTTP_200_OK
        )


class LogoutUser(APIView):
    permission_classes = [AllowAny]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        if user and user.is_authenticated:
            try:
                request.user.auth_token.delete()
            except Token.DoesNotExist:
                pass  

        return CustomResponse.response(
            message="Выход выполнен успешно",
            http_status=status.HTTP_200_OK
        )
