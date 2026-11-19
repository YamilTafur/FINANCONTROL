
from django.db import models
from django.conf import settings


class MetaAhorro(models.Model):

    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='metas_ahorro'
    )

    nombre = models.CharField(max_length=150)

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    monto_objetivo = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    fecha_inicio = models.DateField()
    fecha_limite = models.DateField(null=True, blank=True)

    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default='ACTIVA'
    )

    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class AporteAhorro(models.Model):

    meta = models.ForeignKey(
        MetaAhorro,
        on_delete=models.CASCADE,
        related_name='aportes'
    )

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    fecha = models.DateField()

    descripcion = models.CharField(
        max_length=255,
        blank=True
    )

    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Aporte de S/ {self.monto}"


class ConfiguracionProteccion(models.Model):

    meta = models.OneToOneField(
        MetaAhorro,
        on_delete=models.CASCADE,
        related_name='proteccion'
    )

    proteccion_activa = models.BooleanField(default=True)

    permitir_retiros = models.BooleanField(default=False)

    requiere_confirmacion = models.BooleanField(default=True)

    monto_minimo_protegido = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"Protección de {self.meta.nombre}"


class RetiroAhorro(models.Model):

    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("CONFIRMADO", "Confirmado"),
        ("RECHAZADO", "Rechazado"),
    ]

    meta = models.ForeignKey(
        MetaAhorro,
        on_delete=models.CASCADE,
        related_name="retiros"
    )

    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    fecha = models.DateField()

    descripcion = models.CharField(
        max_length=255,
        blank=True
    )

    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default="PENDIENTE"
    )

    solicitado = models.DateTimeField(auto_now_add=True)

    resuelto = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Retiro de S/ {self.monto} - {self.estado}"
