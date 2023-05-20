import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from kernel.models import *
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if not request.user.is_staff and not Vehiculo.objects.filter(fk_Chofer__fk_User=request.user):
        # enviando al cliente a adicionar su auto en caso de no tener
        return HttpResponseRedirect(reverse('autos'))

    pasar_por = {}
    # verificando si es cliente y tiene que pasar por algún Servi
    if not request.user.is_staff:
        iautos_cliente = Vehiculo.objects.filter(fk_Chofer__fk_User=request.user)
        for servi in Servi.objects.all():
            for auto in servi.get_cola_gasolina_procesar():
                if auto.fk_Vehiculo in iautos_cliente:
                    pasar_por['Gasolina en ' + servi.nombre + ' para ' +
                              auto.fk_Vehiculo.matricula] = ', turno # ' + str(auto.turno)

            for auto in servi.get_cola_diesel_procesar():
                if auto.fk_Vehiculo in iautos_cliente:
                    pasar_por['Diesel en ' + servi.nombre + ' para ' +
                              auto.fk_Vehiculo.matricula] = ', turno # ' + str(auto.turno)

    context = {
        'servicentros': Servi.objects.all(),
        'pasar_por': pasar_por,
        'header': "Inicio"
    }
    return render(request, 'index.html', context)


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    else:

        uname = ""
        if request.POST:
            uname = request.POST.get('uname').strip().lower()
            pwd = request.POST.get('pwd')
            iuser = User.objects.filter(username=uname).first()
            if iuser:
                auth_user = auth.authenticate(username=iuser.username, password=pwd)
                if auth_user:
                    auth.login(request, auth_user)
                    messages.success(request, "Bienvenido " + iuser.first_name + "!")
                    return HttpResponseRedirect(reverse('index'))
                else:
                    messages.error(request, 'Datos incorrectos.')
            else:
                messages.error(request, 'Datos incorrectos.')

        return render(request, "login.html", {'uname': uname})


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    else:

        form = {}
        if request.POST:
            licencia = request.POST.get('licencia').strip().lower()
            uname = request.POST.get('name').strip().lower()
            phone = request.POST.get('phone').strip().lower()
            pwd = request.POST.get('pwd')
            iuser = User.objects.filter(username=licencia).first()
            form['licencia'] = licencia
            form['name'] = uname
            form['phone'] = phone
            if iuser:
                messages.warning(request, 'Ya existe esta licencia.')
            else:
                # creando el usuario para que pueda autenticarse
                iuser = User(username=licencia)
                iuser.set_password(pwd)
                iuser.save()
                ichofer = Chofer(fk_User=iuser, nombre=uname, carnet=licencia, telefono=phone)
                ichofer.save()
                auth_user = auth.authenticate(username=iuser.username, password=pwd)
                if auth_user:
                    auth.login(request, auth_user)
                    messages.success(request, "Bienvenido!")
                    return HttpResponseRedirect(reverse('index'))

        return render(request, "register.html", {'form': form})


@login_required
def change_password(request):
    if request.POST:
        new_pwd = request.POST.get('new')
        iuser = User.objects.get(pk=request.user.pk)
        iuser.set_password(new_pwd)
        iuser.save()
        auth.logout(request)
        messages.success(request, 'Contraseña actualizada. Acceda nuevamente.')  # }
        return HttpResponseRedirect(reverse('index'))
    return render(request, "upd_pwd.html", {'header': "Cambiar contraseña"})


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def servicentros(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return HttpResponseRedirect(reverse('logout'))

    i_servis, i_historial = Servi.objects.all(), CombustibleServi.objects.filter(fk_User=request.user)
    if request.user.is_staff and not request.user.is_superuser:
        i_servis = i_servis.filter(pk__in=Responsable.objects.filter(fk_User=request.user).values('fk_Servi'))
    context = {
        'servicentros': i_servis, 'historial': i_historial, 'header': "Servicentros"
    }
    return render(request, 'servis.html', context)


@login_required
def add_servicentro(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('logout'))

    if request.POST:
        uname = request.POST.get('uname').strip().lower()
        distancia = int(request.POST.get('distancia'))
        Servi(nombre=uname, distancia_turnos=distancia).save()
        return HttpResponseRedirect(reverse('servicentros'))

    return render(request, 'addservi.html', {'header': "Nuevo Servicentro"})


@login_required
def add_responsable(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('logout'))

    form = {}
    if request.POST:
        pk_servi = int(request.POST.get('servi'))
        uname = request.POST.get('name').strip().lower()
        user = request.POST.get('user').strip().lower()
        mail = request.POST.get('correo').strip().lower()
        form['pk_servi'] = pk_servi
        form['uname'] = uname
        form['user'] = user
        form['correo'] = mail
        if User.objects.filter(username=user).first():
            messages.error(request, "Ya existe este usuario.")
        else:
            # creando el usuario para que pueda autenticarse
            iuser = User(username=user, first_name=uname)
            iuser.set_password(user)
            iuser.is_staff = True
            iuser.save()
            Responsable(fk_Servi=Servi.objects.get(pk=pk_servi), fk_User=iuser, correo=mail).save()
            messages.success(request, "Responsable adicionado.")
            return HttpResponseRedirect(reverse('responsables'))

    context = {
        'servicentros': Servi.objects.all(),
        'form': form, 'header': "Nuevo Responsable"
    }

    return render(request, 'addresponsable.html', context)


@login_required
def responsables(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse('logout'))

    context = {
        'responsables': Responsable.objects.all(), 'header': "Responsables"
    }
    return render(request, 'responsables.html', context)


@login_required
def add_combustible(request):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('logout'))

    if request.POST:
        pk_servi = request.POST.get('servi')
        gasolina = int(request.POST.get('combustible'))
        lts = float(request.POST.get('cantidad'))
        i_combservi = CombustibleServi(fk_User=request.user, fk_Servi=Servi.objects.get(pk=pk_servi),
                                       gasolina=gasolina, litros=lts, fecha=timezone.now())
        i_combservi.save()
        if i_combservi.gasolina:
            i_combservi.fk_Servi.total_gasolina += lts
            i_combservi.fk_Servi.save()
        else:
            i_combservi.fk_Servi.total_diesel += lts
            i_combservi.fk_Servi.save()
        messages.success(request, "Combustible adicionado.")
        return HttpResponseRedirect(reverse('servicentros'))

    i_servi = None
    if request.user.is_staff:
        i_resp = Responsable.objects.filter(fk_User=request.user).first()
        if i_resp:
            i_servi = i_resp.fk_Servi
    context = {
        'servi': i_servi, 'header': "Entrada de Combustible"
    }

    return render(request, 'addcombustible.html', context)


@login_required
def dar_baja_cola(request):
    if request.is_ajax:
        pst = request.GET
        i_cola = Cola.objects.get(pk=pst.get('pk_cola'))
        litros = float(pst.get('litros'))
        i_cola.estado = 2
        if litros == 0:
            i_cola.estado = 3
        elif litros < 0:
            # para cuando especifique cantidad
            litros = float(pst.get('otro'))
        i_cola.procesada = timezone.now()
        i_cola.litros = litros
        i_cola.save()
        # disminuir los litros globales del servicentro
        if i_cola.fk_Vehiculo.gasolina:
            i_cola.fk_Servi.total_gasolina -= litros
        else:
            i_cola.fk_Servi.total_diesel -= litros
        i_cola.fk_Servi.save()

    return JsonResponse({"status": 200})


@login_required
def procesar_gasolina(request):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('logout'))

    context = {
        'cola_gasolina': Responsable.objects.filter(fk_User=request.user).first().get_cola_gasolina_procesar(),
        'header': "Turnos para Gasolina"
    }

    return render(request, 'procesar_gasolina.html', context)


@login_required
def procesar_diesel(request):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('logout'))

    context = {
        'cola_diesel': Responsable.objects.filter(fk_User=request.user).first().get_cola_diesel_procesar(),
        'header': "Turnos para Diesel"
    }

    return render(request, 'procesar_diesel.html', context)


@login_required
def autos(request):
    i_autos = Vehiculo.objects.filter(fk_Chofer=Chofer.objects.get(fk_User=request.user))

    context = {
        'autos': i_autos, 'turnos': Cola.objects.filter(fk_Vehiculo__fk_Chofer__fk_User=request.user).first(),
        'header': "Mis Autos"
    }
    return render(request, 'autos.html', context)


@login_required
def profile(request):
    i_profile = Chofer.objects.filter(fk_User=request.user).first()

    if request.POST and i_profile:
        i_profile.nombre = request.POST.get('nombre')
        i_profile.telefono = request.POST.get('telefono')
        i_profile.save()
        messages.success(request, "Perfil actualizado.")
        return HttpResponseRedirect(reverse('profile'))

    context = {
        'profile': i_profile,
        'header': "Mi Perfil"
    }
    return render(request, 'profile.html', context)


@login_required
def add_auto(request):

    if request.POST:
        matricula = request.POST.get('chapa').strip().lower()
        gasolina = int(request.POST.get('combustible'))
        if Vehiculo.objects.filter(matricula=matricula, fk_Chofer__fk_User=request.user).first():
            messages.info(request, "Ya Usted tiene este vehículo.")
        else:
            Vehiculo(fk_Chofer=Chofer.objects.filter(fk_User=request.user).first(),
                     gasolina=gasolina,
                     matricula=matricula).save()
            messages.success(request, "Vehículo adicionado.")
        return HttpResponseRedirect(reverse('autos'))

    context = {
        'header': "Nuevo Auto"
    }

    return render(request, 'addauto.html', context)


@login_required
def reservas(request):

    if not request.user.is_staff and not Vehiculo.objects.filter(fk_Chofer__fk_User=request.user):
        # enviando al cliente a adicionar su auto en caso de no tener
        return HttpResponseRedirect(reverse('autos'))

    context = {
        'lista': Cola.objects.filter(fk_Vehiculo__fk_Chofer__fk_User=request.user).order_by('-fecha'),
        # para los autos que son compartidos por mas de un conductor
        'lista_extra': Cola.objects.filter(
            fk_Vehiculo__matricula__in=Vehiculo.objects.filter(
                fk_Chofer__fk_User=request.user).values('matricula')).filter(
            ~Q(fk_Vehiculo__fk_Chofer__fk_User=request.user)).order_by('-fecha'),
        'header': "Mis Turnos"
    }

    return render(request, 'reservas.html', context)


@login_required
def add_reserva(request):

    if request.POST:
        pk_auto = request.POST.get('vehiculo')
        iauto = Vehiculo.objects.get(pk=pk_auto)
        pk_servi = request.POST.get('servicentro')
        iservi = Servi.objects.get(pk=pk_servi)
        icola = Cola.objects.filter(fk_Vehiculo__matricula=iauto.matricula, estado=1)
        ultimo_turno = iservi.get_ultimo_turno_diesel()
        if iauto.gasolina:
            ultimo_turno = iservi.get_ultimo_turno_gasolina()
        continuar = True
        if icola.count() > 1:
            # verificar que esté en 2 servicentros solamente
            servis = []
            for cola in icola:
                if cola.fk_Servi.pk not in servis:
                    servis.append(cola.fk_Servi.pk)
            if len(servis) > 1:
                messages.info(request, "Ya este auto está en 2 servicentros: " +
                              Servi.objects.get(pk=servis[0]).nombre + " y " +
                              Servi.objects.get(pk=servis[1]).nombre)
                continuar = False
        if icola.filter(fk_Servi=iservi).count() > 1:
            # validando si ya está 2 veces en el mismo servi
            turnos = ""
            for cola in icola:
                turnos += str(cola.turno) + ", "
            messages.info(request, "Ya este auto está en cola, turnos: " + turnos)
            continuar = False
        elif icola.filter(fk_Servi=iservi).count() == 1:
            # verificando que tenga al menos 200 autos delante
            diferencia = ultimo_turno - icola.first().turno + 1
            if diferencia < iservi.distancia_turnos:
                messages.info(request, "Debe esperar " + str(200-diferencia) + " turnos para volver a marcar")
                continuar = False
        if continuar:
            ncola = Cola(fk_Vehiculo=iauto, fk_Servi=iservi, estado=1, fecha=timezone.now(),
                         turno=ultimo_turno + 1)
            messages.success(request, "Turno solicitado")
            ncola.save()
        return HttpResponseRedirect(reverse('reservas'))

    context = {
        'servicentros': Servi.objects.all(),
        'autos': Vehiculo.objects.filter(fk_Chofer__fk_User=request.user),
        'header': "Solicitud de Turno"
    }

    return render(request, 'addreserva.html', context)


@login_required
def del_reserva(request, pk_turno):

    ireserva = Cola.objects.filter(pk=pk_turno).first()
    if ireserva and ireserva.fk_Vehiculo.fk_Chofer.fk_User == request.user:
        ireserva.estado = 4
        ireserva.procesada = datetime.datetime.now()
        ireserva.save()
        messages.info(request, "Turno cancelado")

    return HttpResponseRedirect(reverse('reservas'))


@login_required
def del_profile(request, pk_chofer):

    ichofer = Chofer.objects.filter(pk=pk_chofer).first()
    if ichofer and ichofer.fk_User == request.user:
        ichofer.fk_User.delete()
        messages.info(request, "Perfil eliminado")

    return HttpResponseRedirect(reverse('index'))


@login_required
def tiempo_real_gasolina(request, pk_servi):
    i_servi = Servi.objects.get(pk=pk_servi)

    context = {
        'servi': i_servi,
        'header': "Despacho de Gasolina en " + i_servi.nombre
    }
    return render(request, 'tiempo_real_gasolina.html', context)


@login_required
def tiempo_real_diesel(request, pk_servi):
    i_servi = Servi.objects.get(pk=pk_servi)

    context = {
        'servi': i_servi,
        'header': "Despacho de Diesel en " + i_servi.nombre
    }
    return render(request, 'tiempo_real_diesel.html', context)


@login_required
def buscar(request):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('logout'))

    if request.POST:
        matricula = request.POST.get('matricula').strip().lower()

        context = {
            'lista': Cola.objects.filter(fk_Vehiculo__matricula=matricula).all().order_by('-fecha'),
            'matricula': matricula,
            'header': "Buscar"
        }
        return render(request, 'buscar.html', context)

    return render(request, 'buscar.html', {'header': "Buscar"})
