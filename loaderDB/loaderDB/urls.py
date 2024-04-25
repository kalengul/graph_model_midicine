"""
URL configuration for loaderDB project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from loader_app import views
import medicalNLP.views


urlpatterns = [
    # маршрутизация основных функции веб-сервиса 
    path('', views.index),
    path('admin/', admin.site.urls),
    path('back_loader/', views.back_loader),
    path('front_loader/', views.front_loader),
    path('show_instruction/<int:drug_id>/', views.show_instruction, name='instruction'),
    path('show_list_of_essential_medicines_text/', views.show_list_of_essential_medicines_text, name='essential_medicines_text'),
    path('show_list_of_essential_medicines_link/', views.show_list_of_essential_medicines_link, name='essential_medicines_link'),
    path('load_to_excel/', views.load_to_excel, name='load_to_excel'),
    path('frequency_dictionary_for_each_drug_to_excel/', views.frequency_dictionary_for_each_drug_to_excel, name='frequency_dictionary_for_each_drug_to_excel'),
    path('frequency_dictionary_for_all_drugs_to_excel/', views.frequency_dictionary_for_all_drugs_to_excel, name='frequency_dictionary_for_all_drugs_to_excel'),
    path('filtering_medical_terms/', views.filtering_medical_terms, name='filtering_medical_terms'),
    # маршрутизация функций медицинского NLP
    path('medical_index/', medicalNLP.views.medical_index, name='medical_index'),
    path('train_vectorization_models/', medicalNLP.views.train_vectorization_models, name='train_vectorization_models'),
    path('creating_semantic_network/', medicalNLP.views.creating_semantic_network, name='creating_semantic_network'),
]
