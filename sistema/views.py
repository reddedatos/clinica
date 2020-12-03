from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth

from django import forms
from django.forms import ModelForm,widgets

from .models import Paciente,TipoArticulo,Articulo,Turno ,Pedido,ItemPedido
from django.contrib.auth.models import User,Group

from datetime import datetime, date, time, timedelta

from django.shortcuts import get_object_or_404

def index(request):
    if not request.user.is_authenticated:
        return(render(request,"login.html")) #index
    else:
        return HttpResponseRedirect(reverse("inicio"))
    

def login_view(request):
    if request.method=="POST":
        nombreusuario=request.POST["nombreusuario"]
        password=request.POST["password"]

        usuario=auth.authenticate(username=nombreusuario.lower(),password=password.lower())

        request.session['usuario_valido'] = False

        if usuario:
            auth.login(request,usuario)

            request.session['usuarioSistema_secretaria']  = usuario.groups.filter(name = 'SECRETARIA').exists()
            request.session['usuarioSistema_gerencia']    = usuario.groups.filter(name = 'GERENCIA').exists()
            request.session['usuarioSistema_taller']      = usuario.groups.filter(name = 'TALLER').exists()
            request.session['usuarioSistema_profesional'] = usuario.groups.filter(name = 'PROFESIONAL').exists()
            request.session['usuarioSistema_ventas']      = usuario.groups.filter(name = 'VENTAS').exists()

            request.session['usuario_valido'] = True

            return HttpResponseRedirect(reverse("inicio"))
        else:
            return render(request,"login.html",{"mensaje":"Nombre o clave incorrecta"})

    return render(request,"login.html")

def inicio(request):
    xfecha = datetime.now()
    usuario=request.user
    turnos =Turno.objects.filter(fecha=xfecha).order_by('hora')
    pedidos=Pedido.objects.filter(itempedido__estado__in=['','*','Taller','Pedido','Pendiente']).distinct().order_by('-id')

    usuarioSistema=uSistema()
    if request.session.get('usuario_valido'):
        usuarioSistema.es_secretaria  = request.session['usuarioSistema_secretaria'] 
        usuarioSistema.es_gerencia    = request.session['usuarioSistema_gerencia'] 
        usuarioSistema.es_taller      = request.session['usuarioSistema_taller'] 
        usuarioSistema.es_profesional = request.session['usuarioSistema_profesional'] 
        usuarioSistema.es_ventas      = request.session['usuarioSistema_ventas'] 
    else:
        return render(request,"login.html",{"mensaje":"REINGRESE"})

    return render(request,"usuario.html",{"usuario":usuario,"pedidos":pedidos,"turnos":turnos,'usuarioSistema':usuarioSistema})


def logout_view(request):
    auth.logout(request)
    return render(request,"login.html",{"mensaje":"DESCONECTADO"})

def turnos(request):

    usuario=request.user

    if not usuario.is_authenticated:
        return(render(request,"login.html")) 

    if not usuario.groups.filter(name__in = ['PROFESIONAL','SECRETARIA','GERENCIA']).exists():
        return(render(request,"login.html",{'mensaje':'SU NIVEL DE USUARIO NO PERMITE ESTA OPERACION'})) 

    profid =request.POST.get("idprof", 0)

    addTurno=False
    if profid!=0:
        addTurno=True

    idturno   = 0
    mipac     = 0
    miestado  = ""
    midetalle = ""
    editarlo  = False
    sinagregar=False

    if request.method=="POST" and profid==0:

        mform=request.POST
        if mform["accion"]=="ELIMINAR":
            idturno=mform["idturno"]
            miturno=Turno.objects.get(pk=int(idturno))
            miturno.delete()

        else:
            if mform["accion"]=="EDITAR":
                idturno=mform["idturno"]
                editarlo=True
            else:
                idturno=mform["idturno"]
                if int(idturno)!=0:
                    miturno = get_object_or_404(Turno, id=int(idturno))
                    if usuario.groups.filter(name = 'PROFESIONAL').exists():
                        form = nuevoTurnoProfesional(request.POST or None,instance=miturno)
                    else:
                        form = nuevoTurnoSecretaria(request.POST or None,instance=miturno)
                else:
                    if usuario.groups.filter(name = 'PROFESIONAL').exists():
                        form = nuevoTurnoProfesional(request.POST)
                    else:
                        form = nuevoTurnoSecretaria(request.POST)

                if form.is_valid():
                    form.save()
                else:
                    return render(request, "turnos.html?fecha=01/01/2020", {"form": form })

    lafecha=request.GET.get("fecha", False)

    if lafecha:
        xfecha = datetime.strptime(lafecha,"%d/%m/%Y")
    else:
        if request.method=="POST":
            lafecha=request.POST.get("fecha", False)
            if lafecha:
                xfecha = datetime.strptime(lafecha,"%d/%m/%Y")
            else:
                xfecha = datetime.now()
        else:
            xfecha = datetime.now()

    if editarlo:
        miturno   = Turno.objects.get(pk=int(idturno))
        profid    = miturno.profesional.id
        horaturno = miturno.hora
        idturno   = miturno.id
        mipac     = miturno.paciente.id
        miestado  = miturno.estado
        midetalle = miturno.detalle

    pedidos=None 

    turnosdados=[]

    nombreprofesional=""
    txtProfesional=[]
    if request.session['usuarioSistema_profesional'] and (not request.session['usuarioSistema_secretaria']) and (not request.session['usuarioSistema_gerencia']) :
        txtProf=User.objects.filter(id=request.user.id)
        sinagregar=True
    else:
        txtProf=User.objects.filter(groups__name='PROFESIONAL')

    for prof in txtProf:
        pname="( " + prof.username.strip(' ') + " )"
        if prof.last_name!="" or prof.first_name!="":
            pname=prof.last_name.strip(' ') + " " + prof.first_name.strip(' ')

        txtProfesional.append((prof.id,pname))
        pturnos =Turno.objects.filter(fecha=xfecha,profesional=prof.id).order_by('hora')
        turnosdados.append({'profesional':pname,'turnos':pturnos})
        if int(profid)==int(prof.id):
            nombreprofesional=pname 

    turnos =Turno.objects.filter(fecha=xfecha,profesional=profid).order_by('hora')

    txtHoras=[] #[('08:00','(....08:00....)')]
    itime=datetime(year=1900,month=1,day=1,hour=8,minute=0)
    for m in range(0,25):
        txtHoras.append((itime.strftime("%H:%M"),'(....'+itime.strftime("%H:%M")+'....)'))
        itime=itime+timedelta(hours=0,minutes=20)

    for m in turnos:
        if ( editarlo and m.id!=idturno ) or not editarlo:
            estaHora=(m.hora.strftime("%H:%M"),'(....'+m.hora.strftime("%H:%M")+'....)')
            while estaHora in txtHoras:
                txtHoras.remove(estaHora)  

    if request.session['usuarioSistema_profesional'] and (not request.session['usuarioSistema_secretaria']) and (not request.session['usuarioSistema_gerencia']) :
        turnos =Turno.objects.filter(fecha=xfecha,profesional=request.user).order_by('profesional__username','hora')
    else:
        turnos =Turno.objects.filter(fecha=xfecha).order_by('profesional__username','hora')

    aniodesde=xfecha.year
    mesdesde =xfecha.month
    diadesde =xfecha.day

    txtEstados=[('*',''),('ESPERA','En espera'),('ATENDIDO','Atendido')]


    if usuario.groups.filter(name = 'PROFESIONAL').exists():
        formnuevo=nuevoTurnoProfesional()
        formnuevo.fields['detalle'].widget = forms.Textarea(
                        attrs={'rows': 5,
                                'cols': 20})
        formnuevo.fields['detalle'].initial=midetalle

    else:
        formnuevo=nuevoTurnoSecretaria()

    seleccionarProfesional=FormProfesional()
    seleccionarProfesional.fields['idprof']=forms.ChoiceField(choices=txtProfesional,initial=profid,label='')

    formnuevo.fields['fecha'].initial  = str(diadesde)+"/"+str(mesdesde)+"/"+str(aniodesde)
    
    formnuevo.fields['hora']           = forms.ChoiceField(choices=txtHoras)
    formnuevo.fields['estado']         = forms.ChoiceField(choices=txtEstados)
    formnuevo.fields['estado'].initial = miestado
    formnuevo.fields['profesional'].initial = str(profid)
    formnuevo.fields['paciente'].initial    = str(mipac)

    formnuevo.order_fields(['fecha','profesional'])
    return render(request,"turnos.html",{"usuario":usuario,"pedidos":pedidos,"turnos":turnos,"aniodesde":aniodesde,
        "mesdesde":mesdesde,"diadesde":diadesde,"form":formnuevo,"formprofesional":seleccionarProfesional,"profesionales":txtProf,
        "agregarTurno":addTurno,
        "editar":editarlo,
        "idprof":profid,
        "fecha":xfecha.strftime("%d/%m/%Y"),
        "nombreprofesional":nombreprofesional,
        "turnosdados":turnosdados,
        "idturno":idturno,
        "sinagregar":sinagregar,
        })

def pacientes(request):
    usuario=request.user

    if not usuario.is_authenticated:
        return(render(request,"login.html")) 

    if not usuario.groups.filter(name__in = ['PROFESIONAL','SECRETARIA','GERENCIA']).exists():
        return(render(request,"login.html",{'mensaje':'SU NIVEL DE USUARIO NO PERMITE ESTA OPERACION'})) 

    borrarlo=False
    editarlo=False

    esprof=False

    idpaciente=0

    if request.method=="POST" :
    
        form=request.POST

        idpaciente=form["id"]

        if form["accion"]=="MODIFICAR":
            editarlo=True
        else:
            if form["accion"]=="ELIMINAR":
                borrarlo=True
            else:
                if int(idpaciente)==0:
                    nuevo=Paciente(nombre=form['nombre'])
                    nuevo.save()
                    idpaciente=0

    if request.session['usuarioSistema_profesional'] and (not request.session['usuarioSistema_secretaria']) and (not request.session['usuarioSistema_gerencia'])  :
        mispacientes=Paciente.objects.filter(turno__profesional=request.user).order_by('nombre').distinct()
        esprof=True
    else:
        mispacientes=Paciente.objects.all().order_by('nombre')

    historial=None

    if Paciente.objects.filter(pk=int(idpaciente)):
        mipaciente=Paciente.objects.get(pk=int(idpaciente))
        historial =Turno.objects.filter(paciente=mipaciente,profesional=request.user).order_by('-fecha')
        if borrarlo:
            mipaciente.delete()
            idpaciente=0
        if editarlo:
            mipaciente.nombre=form["nombre"]
            mipaciente.save()
            idpaciente=0
    else:
        mipaciente=None


    editarlo=False
    if idpaciente!=0:
        editarlo=True

    return( render(request,"pacientes.html",{
        "mispacientes":mispacientes,
        "editarlo":editarlo,
        "mipaciente":mipaciente,
        "historial":historial,
        "esprof":esprof,
    }))


def articulos(request):
    usuario=request.user

    if not usuario.is_authenticated:
        return(render(request,"login.html")) 

    if not usuario.groups.filter(name__in = ['VENTAS','GERENCIA']).exists():
        return(render(request,"login.html",{'mensaje':'SU NIVEL DE USUARIO NO PERMITE ESTA OPERACION'})) 

    borrarlo=False
    editarlo=False

    idarticulo=0

    if request.method=="POST" :

        idarticulo = request.POST['idart']
        miaccion   = request.POST['accion']

        if miaccion=="MODIFICAR":
            editarlo=True
        else:
            if miaccion=="ELIMINAR":
                borrarlo=True
            else:
                if int(idarticulo)==0 and miaccion=="AGREGAR":
                        miform     = FormArticulo(data = request.POST or None)
                        miform.save()
                        idarticulo=0
                else:
                    pass
        
    tipos = TipoArticulo.objects.all()
    misarticulos = Articulo.objects.all().order_by('descripcion')
    
    if Articulo.objects.filter(pk=idarticulo):
        miarticulo=Articulo.objects.get(pk=idarticulo)
        if borrarlo:
            miarticulo.delete()
            idarticulo=0
            miarticulo=None
        if editarlo:
            object_to_edit = get_object_or_404(Articulo,id=idarticulo)
            miform     = FormArticulo(data = request.POST or None, instance=object_to_edit)

            miform.save()
            idarticulo=0

            miarticulo=None

        form=FormArticulo(instance=miarticulo)

    else:
        miarticulo=None
        form=FormArticulo()


    editarlo=False
    if idarticulo!=0:
        editarlo=True
        

    return( render(request,"articulos.html",{
        "misarticulos":misarticulos,
        "editarlo":editarlo,
        "miarticulo":miarticulo,
        "form":form,
        "tipos":tipos,
    }))

def pedidos(request):
    usuario=request.user

    if not usuario.is_authenticated:
        return(render(request,"login.html")) 

    if not usuario.groups.filter(name__in = ['VENTAS','GERENCIA','TALLER']).exists():
        return(render(request,"login.html",{'mensaje':'SU NIVEL DE USUARIO NO PERMITE ESTA OPERACION'})) 

    articulos=Articulo.objects.all().order_by('descripcion')
    pacientes=Paciente.objects.all().order_by('nombre')
    pedidos=Pedido.objects.exclude(estado__in=['FINALIZADO','ENTREGADO']).order_by('-id')
    fecha=datetime.now()

    borrarlo=False
    editarlo=False

    estaller=False
    if request.session['usuarioSistema_taller'] and (not request.session['usuarioSistema_ventas'] ) and (not request.session['usuarioSistema_gerencia'] ):
        estaller=True

    ideditar     = 0
    pedidoeditar = None
    itemseditar  = None

    if request.method=="POST" :
    
        form=request.POST

        ideditar=form["id"]

    itemseditar=[]

    xpeds=[]
    for ped in pedidos:
        if int(ped.id)==int(ideditar):
            pedidoeditar=ped
            fecha=ped.fecha
        pitems=ItemPedido.objects.filter(pedido=ped.id)
        xitems=[]
        for pit in pitems:
            eslente=False
            armazon=False
            if pit.articulo.tipo.rubro=="LENTE":
                eslente=True
            if pit.opcion3=="X":
                armazon=True
            xitems.append({"datos":pit,"eslente":eslente,"armazon":armazon})
            if int(ped.id)==int(ideditar):
                itemseditar.append({"datos":pit,"eslente":eslente,"armazon":armazon})
        xpeds.append({"pedido":ped,"items":xitems})

    

    return render(request,"pedidos.html",{
        "articulos":articulos,
        "pacientes":pacientes,
        "pedidos":pedidos,
        "fecha":fecha.strftime("%d/%m/%Y"),
        "xpeds":xpeds,
        "pedidoeditar":pedidoeditar,
        "itemseditar":itemseditar,
        "estaller":estaller,
    })
    
def pedidosAgregar(request):
    usuario=request.user

    if not usuario.is_authenticated:
        return(render(request,"login.html")) 

    if not usuario.groups.filter(name__in = ['VENTAS','GERENCIA','TALLER']).exists():
        return(render(request,"login.html",{'mensaje':'SU NIVEL DE USUARIO NO PERMITE ESTA OPERACION'})) 

    borrarlo=False
    editarlo=False

    form=request.POST

    idpaciente=form["paciente"]
    ideditar  =form["id"]
    miaccion  =form["accion"]
    mipac     =Paciente.objects.get(pk=idpaciente)

    fec=datetime.strptime(form["fecha"], '%d/%m/%Y').date()

    if miaccion=="MODIFICAR":
        editarlo=True
    else:
        if miaccion=="ELIMINAR":
            borrarlo=True
        else:
            if int(ideditar)==0:

                mipedido=Pedido.objects.create(
                    fecha    = fec.strftime("%Y-%m-%d"),
                    estado   = 'PENDIENTE',
                    paciente = mipac,
                    valor    = float(form["valortotal"].replace(',','.')),
                    formapago= form["formapago"],
                    vendedor = usuario,
                )

                for k in range(1,int(form["canti"])+1):
                    print(form["articulo_" + str(k)])

                    idarticulo=form["articulo_" + str(k)]
                    activo    =form["activo_" + str(k)]

                    if activo=="X":
                        miart=Articulo.objects.get(pk=idarticulo)

                        ItemPedido.objects.create(
                            articulo = miart,
                            pedido   = mipedido,
                            cantidad = form["cantidad_" + str(k)],
                            opcion1  = form["opc1_"     + str(k)],
                            opcion2  = form["opc2_"     + str(k)],
                            opcion3  = form["opc3_"     + str(k)],
                            estado   = form["estado_"   + str(k)],
                            precio   = float(form["precio_"   + str(k)].replace(',','.')),
                        )


    if Pedido.objects.filter(pk=ideditar):
        mipedido=Pedido.objects.get(pk=ideditar)
        if borrarlo:
            mipedido.delete()
            ideditar=0
            mipedido=None
        if editarlo:
            print("MODIFICAR")
            mipedido.fecha    =fec.strftime("%Y-%m-%d")
            mipedido.paciente =mipac
            mipedido.valor    =float(form["valortotal"].replace(',','.'))
            mipedido.formapago=form["formapago"]
            mipedido.save()

            for k in range(1,int(form["canti"])+1):

                idarticulo=form["articulo_" + str(k)]
                activo    =form["activo_"   + str(k)]
                idip      =form["idip_"     + str(k)]

                if activo=="X":
                    miart=Articulo.objects.get(pk=idarticulo)
                    if int(idip)<0:
                        ItemPedido.objects.create(
                            articulo = miart,
                            pedido   = mipedido,
                            cantidad = form["cantidad_" + str(k)],
                            opcion1  = form["opc1_"     + str(k)],
                            opcion2  = form["opc2_"     + str(k)],
                            opcion3  = form["opc3_"     + str(k)],
                            estado   = form["estado_"   + str(k)],
                            precio   = float(form["precio_"   + str(k)].replace(',','.')),
                        )
                    else:
                        myitem=ItemPedido.objects.get(pk=idip)
                        myitem.estado=form["estado_"   + str(k)];
                        myitem.save();
                else:
                    if int(idip)>0:
                        myitem=ItemPedido.objects.get(pk=idip)
                        myitem.delete()
                        



    formdatos={
        "paciente":form["paciente"],
        "fecha"   :form["fecha"],
        "canti"   :form["canti"],
    }



    return HttpResponseRedirect(reverse("pedidos"))

def reportes(request):
    usuario=request.user

    if not usuario.is_authenticated:
        return(render(request,"login.html")) 

    if not usuario.groups.filter(name__in = ['GERENCIA']).exists():
        return(render(request,"login.html",{'mensaje':'SU NIVEL DE USUARIO NO PERMITE ESTA OPERACION'})) 

    hoy=date.today()

    reporte1=False
    reporte2=False
    reporte3=False
    reporte4=False
    reporte5=False
    accion=""
    tipo  =""
    datos =None
    pacientes={}
    articulos={}
    vendedores={}
    fec1=hoy.strftime("%d/%m/%Y")
    fec2=hoy.strftime("%d/%m/%Y")
    cantidad=0
    total=0

    if request.method=="POST":
        form   = request.POST
        accion = form["accion"]
        tipo   = form["tipo"]
        fec1   = form["fec1"]
        fec2   = form["fec2"]

    fec1a=int(datetime.strptime(fec1,"%d/%m/%Y").year)
    fec1m=int(datetime.strptime(fec1,"%d/%m/%Y").month)
    fec1d=int(datetime.strptime(fec1,"%d/%m/%Y").day)

    fec2a=int(datetime.strptime(fec2,"%d/%m/%Y").year)
    fec2m=int(datetime.strptime(fec2,"%d/%m/%Y").month)
    fec2d=int(datetime.strptime(fec2,"%d/%m/%Y").day)

    if accion=="REPORTE1":
        reporte1=True
        turnos=Turno.objects.filter(
            fecha__gte=date(fec1a, fec1m, fec1d)
            ).filter(
                fecha__lte=date(fec2a, fec2m, fec2d)
            ).filter(
                estado='ATENDIDO'
            )
        for turno in turnos:
            if turno.paciente.nombre not in pacientes:
                pacientes[turno.paciente.nombre]=1
            else:
                pacientes[turno.paciente.nombre]=pacientes[turno.paciente.nombre]+1
        
        datos=sorted(pacientes.items(),key=lambda x:(-x[1],x[0]))
        cantidad = len(pacientes)

    if accion=="REPORTE2":
        reporte2=True
        turnos=Turno.objects.filter(
            fecha__gte=date(fec1a, fec1m, fec1d)
            ).filter(
                fecha__lte=date(fec2a, fec2m, fec2d)
            ).exclude(
                estado='ATENDIDO'
            )
        for turno in turnos:
            if turno.paciente.nombre not in pacientes:
                pacientes[turno.paciente.nombre]=1
            else:
                pacientes[turno.paciente.nombre]=pacientes[turno.paciente.nombre]+1
        
        datos=sorted(pacientes.items(),key=lambda x:(-x[1],x[0]))
        cantidad = len(pacientes)

    if accion=="REPORTE3":
        reporte3=True
        pedidos=Pedido.objects.filter(
            fecha__gte=date(fec1a, fec1m, fec1d)
            ).filter(
                fecha__lte=date(fec2a, fec2m, fec2d)
            )
        for pedido in pedidos:
            if pedido.paciente.nombre not in pacientes:
                pacientes[pedido.paciente.nombre]=1
            else:
                pacientes[pedido.paciente.nombre]=pacientes[pedido.paciente.nombre]+1
        
        datos=sorted(pacientes.items(),key=lambda x:(-x[1],x[0]))
        cantidad = len(pacientes)

    if accion=="REPORTE4":
        reporte4=True
        pedidos=ItemPedido.objects.filter(
            pedido__fecha__gte=date(fec1a, fec1m, fec1d)
            ).filter(
                pedido__fecha__lte=date(fec2a, fec2m, fec2d)
            )
        for pedido in pedidos:
            if pedido.articulo.descripcion not in articulos:
                articulos[pedido.articulo.descripcion]=pedido.cantidad
            else:
                articulos[pedido.articulo.descripcion]=articulos[pedido.articulo.descripcion]+pedido.cantidad
        
        datos=sorted(articulos.items(), key=lambda tup:(-tup[1], tup[0]))
        cantidad = len(articulos)

    if accion=="REPORTE5":
        reporte5=True
        pedidos=ItemPedido.objects.filter(
            pedido__fecha__gte=date(fec1a, fec1m, fec1d)
            ).filter(
                pedido__fecha__lte=date(fec2a, fec2m, fec2d)
            )
        for pedido in pedidos:
            vname="( " + pedido.pedido.vendedor.username.strip(' ') + " )"
            if pedido.pedido.vendedor.last_name!="" or pedido.pedido.vendedor.first_name!="":
                vname=pedido.pedido.vendedor.last_name.strip(' ') + " " + pedido.pedido.vendedor.first_name.strip(' ')
            if vname not in vendedores:
                vendedores[vname]=pedido.precio*pedido.cantidad
            else:
                vendedores[vname]=vendedores[vname]+pedido.precio*pedido.cantidad
            total=total+pedido.precio*pedido.cantidad
        datos=sorted(vendedores.items(), key=lambda tup:(-tup[1], tup[0]))
        cantidad = len(vendedores)

    contexto={
        'accion':accion,
        'tipo':tipo,
        'datos':datos,
        'cantidad':cantidad,
        'reporte1':reporte1,
        'reporte2':reporte2,
        'reporte3':reporte3,
        'reporte4':reporte4,
        'reporte5':reporte5,
        'fec1':fec1,
        'fec2':fec2,
        'total':total,
    }

    return render(request,"reportes.html",contexto)

class FormProfesional(forms.Form):
    idprof=forms.ChoiceField()
    labels={'idprof':''}

class nuevoTurnoProfesional(ModelForm):
    class Meta:
        model=Turno
        fields='__all__'
        
        field_order=['fecha','profesional']
        widgets={'fecha':forms.HiddenInput(),'profesional':forms.HiddenInput()}

class nuevoTurnoSecretaria(ModelForm):
    class Meta:
        model=Turno
        fields='__all__'
        exclude=('detalle',)
        field_order=['fecha','profesional']
        widgets={'fecha':forms.HiddenInput(),'profesional':forms.HiddenInput()}

class uSistema:
    es_secretaria  = False
    es_gerencia    = False
    es_taller      = False
    es_profesional = False
    es_ventas      = False 

class FormArticulo(ModelForm):
    class Meta:
        model=Articulo
        fields="__all__"
    
