# Generated by Django 3.1.2 on 2020-11-11 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0005_auto_20201111_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='turno',
            name='fecha',
            field=models.DateField(default='0000-00-00'),
        ),
        migrations.AlterField(
            model_name='turno',
            name='hora',
            field=models.TimeField(default='00:00'),
        ),
    ]
