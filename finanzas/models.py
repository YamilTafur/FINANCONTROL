
from django.db import models
from django.conf import settings


class Categoria(models.Model):

    TIPOS = [
        ('INGRESO', 'Ingreso'),
        ('GASTO', 'Gasto'),
    ]


    GRUPOS_DISTRIBUCION = [
        ('NECESIDADES', 'Necesidades'),
        ('GUSTOS', 'Gustos'),
        ('DEUDAS', 'Deudas'),
    ]


    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categorias'
    )

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPOS)

    grupo_distribucion = models.CharField(
        max_length=20,
        choices=GRUPOS_DISTRIBUCION,
        null=True,
        blank=True
    )

    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Presupuesto(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='presupuestos'
    )

    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    monto_limite = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Ingreso(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ingresos'
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='ingresos'
    )

    presupuesto = models.ForeignKey(
        Presupuesto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ingresos'
    )

    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)

    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ingreso de S/ {self.monto}"


class ConfiguracionDistribucion(models.Model):

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='configuracion_distribucion'
    )

    porcentaje_necesidades = models.DecimalField(
        max_digits=5, decimal_places=2, default=55
    )

    porcentaje_gustos = models.DecimalField(
        max_digits=5, decimal_places=2, default=5
    )

    porcentaje_deudas = models.DecimalField(
        max_digits=5, decimal_places=2, default=10
    )

    porcentaje_ahorro = models.DecimalField(
        max_digits=5, decimal_places=2, default=15
    )

    porcentaje_inversion = models.DecimalField(
        max_digits=5, decimal_places=2, default=15
    )

    actualizada = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Distribución de {self.usuario}"


class DistribucionIngreso(models.Model):

    TIPOS = [
        ('MANUAL', 'Manual'),
        ('AUTOMATICA', 'Automática'),
    ]

    MODALIDADES = [
        ('NINGUNA', 'Sin porcentajes'),
        ('PREDETERMINADA', 'Predeterminada'),
        ('PERSONALIZADA', 'Personalizada'),
    ]

    ingreso = models.OneToOneField(
        Ingreso,
        on_delete=models.CASCADE,
        related_name='distribucion'
    )

    tipo = models.CharField(max_length=15, choices=TIPOS)

    modalidad = models.CharField(
        max_length=20,
        choices=MODALIDADES,
        default='NINGUNA'
    )

    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Distribución del ingreso {self.ingreso.id}"


class DetalleDistribucion(models.Model):

    DESTINOS = [
        ('NECESIDADES', 'Necesidades'),
        ('GUSTOS', 'Gustos'),
        ('DEUDAS', 'Deudas'),
        ('AHORRO', 'Ahorro'),
        ('INVERSION', 'Inversión'),
    ]

    distribucion = models.ForeignKey(
        DistribucionIngreso,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    destino = models.CharField(
        max_length=20,
        choices=DESTINOS,
        default='NECESIDADES'
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='distribuciones',
        null=True,
        blank=True
    )

    meta_ahorro = models.ForeignKey(
        'ahorros.MetaAhorro',
        on_delete=models.PROTECT,
        related_name='distribuciones',
        null=True,
        blank=True
    )

    monto = models.DecimalField(max_digits=12, decimal_places=2)

    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['distribucion', 'categoria'],
                name='categoria_unica_por_distribucion'
            ),
            models.UniqueConstraint(
                fields=['distribucion', 'meta_ahorro'],
                name='meta_unica_por_distribucion'
            )
        ]

    def __str__(self):
        return f"{self.destino}: S/ {self.monto}"


class Gasto(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gastos'
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='gastos'
    )

    presupuesto = models.ForeignKey(
        Presupuesto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gastos'
    )

    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)

    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gasto de S/ {self.monto}"


class ConfiguracionFinanciera(models.Model):

    POLITICAS = [
        ('AVISAR', 'Solo avisar'),
        ('CONFIRMAR', 'Solicitar confirmación'),
        ('RESTRINGIR', 'Restringir gasto'),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='configuracion_financiera'
    )

    politica_exceso = models.CharField(
        max_length=15,
        choices=POLITICAS,
        default='CONFIRMAR'
    )

    def __str__(self):
        return f"Configuración de {self.usuario.username}"
