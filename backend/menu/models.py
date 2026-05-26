from django.db import models


MAX_LENGTH = 255


class Menu(models.Model):
    GROUP_CHOICES = [
        ("main", "Основная"),
        ("manage", "Управление"),
    ]

    title = models.CharField(max_length=MAX_LENGTH, verbose_name='Название')
    slug = models.CharField(max_length=MAX_LENGTH, unique=True, verbose_name='URL')
    is_auth = models.BooleanField(default=False, verbose_name='Нужна ли авторизация?')
    is_active = models.BooleanField(default=True, verbose_name='Отображать?')
    group = models.CharField(max_length=150, choices=GROUP_CHOICES, blank=True, verbose_name='Группа')

    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'
        ordering = ['title']
    
    def __str__(self):
        return f'{self.title} ({self.slug})'
    