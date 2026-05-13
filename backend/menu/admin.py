from django.contrib import admin

from menu.models import Menu


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_auth', 'is_active']
    prepopulated_fields = {'slug': ('title',),}
