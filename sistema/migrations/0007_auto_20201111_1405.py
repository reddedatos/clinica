# Generated by Django 3.1.2 on 2020-11-11 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0006_auto_20201111_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='turno',
            name='fecha',
            field=models.DateField(default='2020-01-01'),
        ),
    ]
