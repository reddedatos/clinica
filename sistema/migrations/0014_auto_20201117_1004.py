# Generated by Django 3.1.2 on 2020-11-17 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0013_auto_20201117_0900'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articulo',
            name='tipo',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='sistema.tipoarticulo'),
        ),
    ]
