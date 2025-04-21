from django.db import models


MAX_LENGTH = 255


class Menu(models.Model):
    title = models.CharField(max_length=MAX_LENGTH, verbose_name='Название')
    slug = models.CharField(max_length=MAX_LENGTH, unique=True, verbose_name='URL')

    class Meta:
        verbose_name = 'Меню'
        verbose_name_plural = 'Меню'
        ordering = ['title']
    
    def __str__(self):
        return f'{self.title} ({self.slug})'
    