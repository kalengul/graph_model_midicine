# Импорт модуля admin из библиотеки Django.contrib
from django.contrib import admin
# Импорт модели MyModel из текущего каталога (".")
from .models import *


class ml_modelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_model', 'slug', 'autor', 'time_create', 'user_group')
    list_display_links = ('id', 'name_model', 'slug')
    search_fields = ('name_model', 'autor', 'time_create', 'user_group')
    prepopulated_fields = {"slug": ("name_model",)}


class DrugAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'pg', 'time_create', 'user')
    list_display_links = ('id', 'name', 'slug')
    search_fields = ('name', 'time_create', 'user')
    prepopulated_fields = {"slug": ("name",)}


class DrugGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'time_create', 'user')
    list_display_links = ('id', 'title', 'slug')
    search_fields = ('title', 'time_create', 'user')
    prepopulated_fields = {"slug": ("title",)}


class DrugInteractionTableAdmin(admin.ModelAdmin):
    list_display = ('DrugOne', 'DrugTwo', 'Interaction', 'time_create', 'user')
    search_fields = ('DrugOne', 'DrugTwo', 'user')


class Drugs_information_MedScape_Admin(admin.ModelAdmin):
    list_display = ('id', 'Name_File', 'Comment_en', 'Comment_ru')


class Type_Drugs_MedScape_Admin(admin.ModelAdmin):
    list_display = ('id', 'Type_en', 'Type_ru')
    search_fields = ('Type_en', 'Type_ru')


class Name_Drugs_MedScape_Admin(admin.ModelAdmin):
    list_display = ('id', 'Name_en', 'Name_ru')
    search_fields = ('Name_en', 'Name_ru')


class Adverse_Effects_MedScape_Admin(admin.ModelAdmin):
    list_display = (
    'id', 'adverse_effects_name_en', 'adverse_effects_name_ru', 'adverse_effects_percent')


class ASource_Drugs_MedScape_Admin(admin.ModelAdmin):
    list_display = (
    'id', 'Source')


class Pregnancy_and_lactation_MedScape_Admin(admin.ModelAdmin):
    list_display = (
    'id', 'Pregnancy_common_ru', 'Pregnancy_specific_ru', 'Lactation_common_ru', 'Lactation_specific_ru', 'Pregnancy_common_en', 'Pregnancy_specific_en', 'Lactation_common_en', 'Lactation_specific_en')

class Warnings_MedScape_Admin(admin.ModelAdmin):
    list_display = (
    'id', 'warnings_type', 'warnings_name_en', 'warnings_name_ru')

class Interaction_MedScape_Admin(admin.ModelAdmin):
    list_display = (
    'id', 'interaction_with', 'classification_type_en', 'classification_type_ru', 'description_en', 'description_ru')


# Регистрация моделей для административного сайта
admin.site.register(ml_model, ml_modelAdmin)

admin.site.register(Drug, DrugAdmin)
admin.site.register(DrugGroup, DrugGroupAdmin)

admin.site.register(DrugInteractionTable, DrugInteractionTableAdmin)

admin.site.register(Drugs_information_MedScape, Drugs_information_MedScape_Admin)
admin.site.register(Type_Drugs_MedScape, Type_Drugs_MedScape_Admin)
admin.site.register(Name_Drugs_MedScape, Name_Drugs_MedScape_Admin)
admin.site.register(Adverse_Effects_MedScape, Adverse_Effects_MedScape_Admin)
admin.site.register(Source_Drugs_MedScape, ASource_Drugs_MedScape_Admin)
admin.site.register(Pregnancy_and_lactation_MedScape, Pregnancy_and_lactation_MedScape_Admin)
admin.site.register(Warnings_MedScape, Warnings_MedScape_Admin)
admin.site.register(Interaction_MedScape, Interaction_MedScape_Admin)
admin.site.register(drugs_chf)
admin.site.register(disease_chf)

admin.site.register(UserGroupAll)
admin.site.register(UserInGroup)
