# Generated by Django 3.1.2 on 2020-11-10 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='turno',
            name='estado',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
