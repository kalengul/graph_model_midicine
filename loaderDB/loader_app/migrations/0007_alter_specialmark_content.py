# Generated by Django 5.0.3 on 2024-03-19 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loader_app', '0006_alter_druginformation_atcclassification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialmark',
            name='content',
            field=models.TextField(verbose_name='Содержание отметки'),
        ),
    ]
