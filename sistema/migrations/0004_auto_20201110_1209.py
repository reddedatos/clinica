# Generated by Django 3.1.2 on 2020-11-10 15:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sistema', '0003_auto_20201110_1151'),
    ]

    operations = [
        migrations.CreateModel(
            name='Articulo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=64)),
                ('opcion1', models.CharField(max_length=20)),
                ('opcion2', models.CharField(max_length=20)),
                ('opcion3', models.CharField(max_length=20)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='TipoArticulo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rubro', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='turno',
            name='detalle',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='turno',
            name='paciente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.paciente'),
        ),
        migrations.AlterField(
            model_name='turno',
            name='profesional',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(blank=True, max_length=20)),
                ('precio', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('cantidad', models.IntegerField(blank=True)),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.articulo')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.paciente')),
            ],
        ),
        migrations.AddField(
            model_name='articulo',
            name='tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.tipoarticulo'),
        ),
    ]