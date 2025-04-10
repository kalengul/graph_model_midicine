def menu_context(request):
    menu = [{'title': "Главная", 'url_name': 'home'}]

    if request.user.is_authenticated and request.user.is_staff:
        menu.append({'title': "Добавить данные", 'url_name': 'add_page'})

    return {'menu': menu}