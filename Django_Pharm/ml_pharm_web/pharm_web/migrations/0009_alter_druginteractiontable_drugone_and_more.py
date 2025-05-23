# Generated by Django 5.2 on 2025-04-08 11:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drugs', '0001_initial'),
        ('pharm_web', '0008_medication_medicationsifeeffect_sifeeffect'),
    ]

    operations = [
        migrations.AlterField(
            model_name='druginteractiontable',
            name='DrugOne',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='druginteractions_one', to='drugs.drug', verbose_name='ЛС №1'),
        ),
        migrations.AlterField(
            model_name='druginteractiontable',
            name='DrugTwo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='druginteractions_two', to='drugs.drug', verbose_name='ЛС №2'),
        ),
        migrations.RemoveField(
            model_name='druggroup',
            name='user',
        ),
        migrations.DeleteModel(
            name='Drug',
        ),
        migrations.DeleteModel(
            name='DrugGroup',
        ),
    ]
