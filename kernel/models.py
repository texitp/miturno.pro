from django.db import models
from django.contrib.auth.models import User


class Servi(models.Model):
    # gestionar los distintos servicentros
    activo = models.BooleanField(default=True)
    nombre = models.CharField(max_length=40, default="")
    total_gasolina = models.FloatField(default=0)
    total_diesel = models.FloatField(default=0)
    distancia_turnos = models.IntegerField(default=200)

    def __str__(self):
        return '%s %s' % (self.pk, self.nombre)

    def get_responsables(self):
        return Responsable.objects.filter(fk_Servi=self).all()

    def get_primer_turno_gasolina(self):
        # donde se quedó la lista a serviciar
        primer_turno = 0
        i_cola = Cola.objects.filter(fk_Vehiculo__gasolina=True, fk_Servi=self).first()
        if i_cola:
            primer_turno = i_cola.turno
        return primer_turno

    def get_ultimo_turno_gasolina(self):
        # el último turno asignado
        ultimo_turno = 0
        i_cola = Cola.objects.filter(fk_Vehiculo__gasolina=True, fk_Servi=self).last()
        if i_cola:
            ultimo_turno = i_cola.turno
        return ultimo_turno

    def get_ultimo_turno_servido_gasolina(self):
        # el último turno asignado
        ultimo_turno = 0
        i_cola = Cola.objects.filter(fk_Vehiculo__gasolina=True, fk_Servi=self, estado__in=(2, 3)).last()
        if i_cola:
            ultimo_turno = i_cola.turno
        return ultimo_turno

    def get_primer_turno_diesel(self):
        # donde se quedó la lista a serviciar
        primer_turno = 0
        i_cola = Cola.objects.filter(fk_Vehiculo__gasolina=False, fk_Servi=self).first()
        if i_cola:
            primer_turno = i_cola.turno
        return primer_turno

    def get_ultimo_turno_diesel(self):
        # el último turno asignado
        ultimo_turno = 0
        i_cola = Cola.objects.filter(fk_Vehiculo__gasolina=False, fk_Servi=self).last()
        if i_cola:
            ultimo_turno = i_cola.turno
        return ultimo_turno

    def get_ultimo_turno_servido_diesel(self):
        # el último turno asignado
        ultimo_turno = 0
        i_cola = Cola.objects.filter(fk_Vehiculo__gasolina=False, fk_Servi=self, estado__in=(2, 3)).last()
        if i_cola:
            ultimo_turno = i_cola.turno
        return ultimo_turno

    def get_total_cola_gasolina(self):
        return Cola.objects.filter(fk_Vehiculo__gasolina=True, fk_Servi=self, estado=1).count()

    def get_total_cola_diesel(self):
        return Cola.objects.filter(fk_Vehiculo__gasolina=False, fk_Servi=self, estado=1).count()

    def get_ultimas_pipas_gasolina(self):
        return CombustibleServi.objects.filter(fk_Servi=self, gasolina=True)[0:5]

    def get_ultimas_pipas_diesel(self):
        return CombustibleServi.objects.filter(fk_Servi=self, gasolina=False)[0:5]

    def get_cola_gasolina_procesar(self):
        ielements = Cola.objects.filter(fk_Servi=self, estado=1,
                                        fk_Vehiculo__gasolina=True)[0:self.total_gasolina/40]
        return Cola.objects.filter(pk__in=ielements)

    def get_cola_gasolina_procesar_str(self):
        ielements = Cola.objects.filter(fk_Servi=self, estado=1, fk_Vehiculo__gasolina=True)
        lista = "\n\nPendientes Gasolina\n"
        lista += "TURNO----CHAPA----CARNET----CHOFER----TELEFONO----FECHA SOLICITUD\n"
        for element in ielements:
            lista += str(element.turno) + '----' + element.fk_Vehiculo.matricula + '----' + \
                     element.fk_Vehiculo.fk_Chofer.carnet + '----' + element.fk_Vehiculo.fk_Chofer.nombre + \
                     element.fk_Vehiculo.fk_Chofer.telefono + '----' + str(element.fecha) + '\n'
        if not ielements:
            lista += "\n\nSIN TURNOS PENDIENTES"
        return lista

    def get_cola_diesel_procesar(self):
        ielements = Cola.objects.filter(fk_Servi=self, estado=1,
                                        fk_Vehiculo__gasolina=False)[0:self.total_diesel/100]
        return Cola.objects.filter(pk__in=ielements)

    def get_cola_diesel_procesar_str(self):
        ielements = Cola.objects.filter(fk_Servi=self, estado=1, fk_Vehiculo__gasolina=False)
        lista = "\n\nPendientes Diesel\n"
        lista += "TURNO----CHAPA----CARNET----CHOFER----TELEFONO----FECHA SOLICITUD\n"
        for element in ielements:
            lista += str(element.turno) + '----' + element.fk_Vehiculo.matricula + '----' + \
                     element.fk_Vehiculo.fk_Chofer.carnet + '----' + element.fk_Vehiculo.fk_Chofer.nombre + \
                     element.fk_Vehiculo.fk_Chofer.telefono + '----' + str(element.fecha) + '\n'
        if not ielements:
            lista += "\n\nSIN TURNOS PENDIENTES\n\n"
        return lista


class Chofer(models.Model):
    # los choferes que serían los clientes
    fk_User = models.ForeignKey(User, related_name="usuario_chofer",
                                on_delete=models.CASCADE, default=None)
    nombre = models.CharField(max_length=100)
    carnet = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)


class Vehiculo(models.Model):
    # los autos que serviciarían en los servicentros
    fk_Chofer = models.ForeignKey(Chofer, related_name="vehiculo_chofer", on_delete=models.CASCADE)
    matricula = models.CharField(max_length=10)
    gasolina = models.BooleanField(default=True)

    def __str__(self):
        return '%s %s' % (self.fk_Chofer.nombre, self.matricula)


class CombustibleServi(models.Model):
    fk_User = models.ForeignKey(User, related_name="user_combustibleservi",
                                on_delete=models.CASCADE, default=None)
    fk_Servi = models.ForeignKey(Servi, related_name="combustible_servi", on_delete=models.CASCADE)
    gasolina = models.BooleanField(default=True)
    litros = models.FloatField()
    fecha = models.DateTimeField()


class Cola(models.Model):
    # para las colas en los servicentros x vehículo y tipo de combustible
    STATUS_CHOICES = [
        (1, 'En cola'),
        (2, 'Procesado'),
        (3, 'Perdido'),
        (4, 'Cancelado'),
    ]
    fk_Servi = models.ForeignKey(Servi, related_name="servi_cola", on_delete=models.CASCADE)
    fk_Vehiculo = models.ForeignKey(Vehiculo, related_name="servi_vehiculo", on_delete=models.CASCADE)
    estado = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=1,
    )
    fecha = models.DateTimeField()
    procesada = models.DateTimeField(default=None, null=True, blank=True)
    litros = models.FloatField(default=0)
    turno = models.IntegerField()

    def __str__(self):
        return '%s %s %s' % (self.fk_Servi.nombre, self.fk_Vehiculo.fk_Chofer.carnet, self.turno)

    class Meta:
        ordering = ('fecha',)
        verbose_name = "Cola"


class Responsable(models.Model):
    fk_User = models.ForeignKey(User, related_name="usuario_responsable",
                                on_delete=models.CASCADE, default=None)
    fk_Servi = models.ForeignKey(Servi, related_name="responsable_servi", on_delete=models.CASCADE)
    correo = models.CharField(max_length=100, default="", blank=True)

    def get_cola_gasolina_procesar(self):
        ielements = Cola.objects.filter(
            fk_Servi=self.fk_Servi, estado=1,
            fk_Vehiculo__gasolina=True)[0:self.fk_Servi.total_gasolina/40]
        return Cola.objects.filter(pk__in=ielements)

    def get_cola_diesel_procesar(self):
        ielements = Cola.objects.filter(
            fk_Servi=self.fk_Servi, estado=1,
            fk_Vehiculo__gasolina=False)[0:self.fk_Servi.total_diesel/100]
        return Cola.objects.filter(pk__in=ielements)
