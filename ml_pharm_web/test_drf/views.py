from rest_framework.views import APIView
from rest_framework.response import Response


class HelloWorld(APIView):
    def get(self, request):
        return Response({"message": "Hello, Polina!"})


class Menu(APIView):
    def get(self, _):
        res = {
            "result": {
                "status": 200,
                "message": "меню получено успешно"
            },
            "data": [
                {
                    "title": "Взаимодействие MedScape",
                    "slug": "/medScape"
                },
                {
                    "title": "Взаимодействие Fortran",
                    "slug": "/fortran"
                },
                {
                    "title": "Добавить ЛС",
                    "slug": "/addDrug"
                }
            ]
        }

        return Response(res)
    