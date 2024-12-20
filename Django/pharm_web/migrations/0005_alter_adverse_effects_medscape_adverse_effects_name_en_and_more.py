# Generated by Django 4.2.1 on 2023-10-12 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pharm_web', '0004_alter_source_drugs_medscape_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adverse_effects_medscape',
            name='adverse_effects_name_en',
            field=models.CharField(max_length=10000, verbose_name='Adverse Effects'),
        ),
        migrations.AlterField(
            model_name='adverse_effects_medscape',
            name='adverse_effects_name_ru',
            field=models.CharField(max_length=10000, verbose_name='Побочное действие'),
        ),
        migrations.AlterField(
            model_name='adverse_effects_medscape',
            name='adverse_effects_percent',
            field=models.CharField(max_length=10000, verbose_name='Процент'),
        ),
        migrations.AlterField(
            model_name='source_drugs_medscape',
            name='Source',
            field=models.CharField(max_length=10000, verbose_name='Источник'),
        ),
        migrations.AlterField(
            model_name='warnings_medscape',
            name='warnings_name_en',
            field=models.CharField(max_length=10000, verbose_name='Warnings'),
        ),
        migrations.AlterField(
            model_name='warnings_medscape',
            name='warnings_name_ru',
            field=models.CharField(max_length=10000, verbose_name='Опасность'),
        ),
        migrations.AlterField(
            model_name='warnings_medscape',
            name='warnings_type',
            field=models.CharField(max_length=10000, verbose_name='Тип опасности'),
        ),
    ]
