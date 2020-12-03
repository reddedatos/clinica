from django.contrib import admin
from .models import Paciente ,TipoArticulo,Articulo,Turno,Pedido,ItemPedido

# Register your models here.
admin.site.register(Paciente)
admin.site.register(Turno)
admin.site.register(TipoArticulo)
admin.site.register(Articulo)
admin.site.register(Pedido)
admin.site.register(ItemPedido)

