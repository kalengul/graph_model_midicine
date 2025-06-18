from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from drugs.utils.custom_response import CustomResponse
from accounts.auth import bearer_token_required


class LoginUser(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return CustomResponse(
                status=400,
                message="Логин и пароль обязательны",
                http_status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if user is None:
            return CustomResponse(
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

        return CustomResponse(
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
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        user = request.user

        if user and user.is_authenticated:
            try:
                user.auth_token.delete()
            except Token.DoesNotExist:
                pass

        return CustomResponse(
            message="Выход выполнен успешно",
            http_status=status.HTTP_200_OK
        )


class TokenCheck(APIView):
    @bearer_token_required
    def post(self, request):
        req_username = request.data.get('username')

        if not req_username:
            return CustomResponse(
                status=400,
                message="Поле 'username' обязательно",
                http_status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.username != req_username:
            return CustomResponse(
                status=403,
                message="Имя пользователя не соответствует токену",
                http_status=status.HTTP_403_FORBIDDEN
            )

        return CustomResponse(
            data={"username": request.user.username},
            status=200,
            message="Токен валиден и принадлежит пользователю",
            http_status=status.HTTP_200_OK
        )
    