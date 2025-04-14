import os

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.conf import settings

from .models import *


class AddDrugGroupForm(forms.ModelForm):
    class Meta:
        model = DrugGroup
        fields = '__all__'


class AddDrugForm(forms.ModelForm):
    class Meta:
        model = Drug
        fields = '__all__'


class DisplaySideEffectsForm(forms.Form):

    DISPLAY_CHOICES = []
    DISPLAY_CHOICES.append(('all', 'Показать всё'))

    filename = 'drugs_xcn.txt'
    path = os.path.join(settings.TXT_DB_PATH, filename)

    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            drug_name = line.split('\t')[1].replace(';', '')
            drug_id = line.split('\t')[0]
            DISPLAY_CHOICES.append(
                (drug_id,
                 drug_name))



    # DISPLAY_CHOICES = [ # Нужно получить список ЛС
    #     ('all', 'Показать все'),
    #     ('amiodaron', 'Амиодарон'),
    # ]

    display_method = forms.ChoiceField(
        choices=DISPLAY_CHOICES,
        label="Выберете способ отображения побочек",
        widget=forms.Select
    )


class AddSideEffect(forms.Form):
    name = forms.CharField(label='Название побочного эффекта', widget=forms.TextInput(attrs={'class': 'form-input'}))


class updateSeideEffectRande(forms.Form):
    # DISPLAY_CHOICES = [ # Нужно получить список побочек
    #     ('1', 'Гипатит'),
    #     ('2', 'Почечная недостаточность'),
    # ]
    DISPLAY_CHOICES = []
    filename = 'side_effects.txt'
    path = os.path.join(settings.TXT_DB_PATH, filename)

    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            if line == '\n':
                continue
            line = line.strip()
            DISPLAY_CHOICES.append(
                (line.split('\t')[0],
                 line.split('\t')[1].replace(';', ''))
            )

    display_method = forms.ChoiceField(
        choices=DISPLAY_CHOICES,
        label="Выберете побочный эффект",
        widget=forms.Select
    )

    name = forms.CharField(label='Коэффициент появления', widget=forms.TextInput(attrs={'class': 'form-input'}))


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
