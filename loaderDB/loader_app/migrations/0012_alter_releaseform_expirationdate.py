# Generated by Django 5.0.3 on 2024-03-28 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loader_app', '0011_alter_releaseform_dosageform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='releaseform',
            name='expirationDate',
            field=models.CharField(max_length=255, verbose_name='Срок годности'),
        ),
    ]
