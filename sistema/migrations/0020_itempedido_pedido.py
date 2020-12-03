# Generated by Django 3.1.2 on 2020-11-18 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sistema', '0019_auto_20201118_1149'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(blank=True)),
                ('estado', models.CharField(blank=True, max_length=20)),
                ('precio', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.paciente')),
            ],
        ),
        migrations.CreateModel(
            name='ItemPedido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField(blank=True)),
                ('precio', models.DecimalField(blank=True, decimal_places=2, max_digits=10)),
                ('opcion1', models.CharField(blank=True, max_length=20)),
                ('opcion2', models.CharField(blank=True, max_length=20)),
                ('opcion3', models.CharField(blank=True, max_length=20)),
                ('estado', models.CharField(max_length=30)),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.articulo')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sistema.pedido')),
            ],
        ),
    ]