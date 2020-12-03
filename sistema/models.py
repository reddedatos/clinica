from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Paciente(models.Model):
    nombre = models.CharField(max_length=64)

    def __str__(self):
        return f"{ self.nombre }"

class Turno(models.Model):
    fecha        = models.DateField()
    hora         = models.TimeField()
    paciente     = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    profesional  = models.ForeignKey(User,on_delete=models.CASCADE)
    estado       = models.CharField(max_length=20,blank=True)
    detalle      = models.CharField(max_length=250,blank=True)

    def __str__(self):
        return f"{ self.fecha }:{ self.hora } {self.paciente} {self.estado}"

class TipoArticulo(models.Model):
    rubro    = models.CharField(max_length=30)

    def __str__(self):
        return f"{ self.rubro }"

class Articulo(models.Model):
    descripcion=models.CharField(max_length=64)
    tipo     = models.ForeignKey(TipoArticulo,on_delete=models.CASCADE,blank=True)
    precio   = models.DecimalField(max_digits=10,decimal_places=2,blank=True)

    def __str__(self):
        return f"{ self.descripcion }"

class Pedido(models.Model):
    paciente  = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha     = models.DateField(blank=True)
    estado    = models.CharField(max_length=20,blank=True)
    valor     = models.DecimalField(max_digits=10,decimal_places=2,blank=True)
    formapago = models.CharField(max_length=20,blank=True)
    vendedor  = models.ForeignKey(User, on_delete=models.CASCADE,blank=True)

    def __str__(self):
        return f"{ self.paciente } { self.fecha }"

class ItemPedido(models.Model):
    pedido  =models.ForeignKey(Pedido,on_delete=models.CASCADE)
    articulo=models.ForeignKey(Articulo,on_delete=models.CASCADE)
    cantidad=models.IntegerField(blank=True)
    precio  =models.DecimalField(max_digits=10,decimal_places=2,blank=True)
    opcion1 = models.CharField(max_length=20,blank=True)
    opcion2 = models.CharField(max_length=20,blank=True)
    opcion3 = models.CharField(max_length=20,blank=True)
    estado  =models.CharField(max_length=30)
    def __str__(self):
        return f"{ self.articulo }"





    