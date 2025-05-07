from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotAuthenticated

from functools import wraps


class BearerTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'


def bearer_token_required(view_func):
    """Декоратор для проверки Bearer токена и аутентификации пользователя."""

    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        for authenticator in [BearerTokenAuthentication()]:
            user_auth_tuple = authenticator.authenticate(request)
            if user_auth_tuple is not None:
                request.user, request.auth = user_auth_tuple
                break
        else:
            raise NotAuthenticated("Учетные данные не были предоставлены.")

        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Учетные данные не были предоставлены.")

        return view_func(self, request, *args, **kwargs)

    return _wrapped_view
