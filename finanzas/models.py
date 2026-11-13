
from django.db import models
from django.conf import settings


class Categoria(models.Model):

    TIPOS = [
        ('INGRESO', 'Ingreso'),
        ('GASTO', 'Gasto'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categorias'
    )

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPOS)
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


class DistribucionIngreso(models.Model):

    TIPOS = [
        ('MANUAL', 'Manual'),
        ('AUTOMATICA', 'Automática'),
    ]

    ingreso = models.OneToOneField(
        Ingreso,
        on_delete=models.CASCADE,
        related_name='distribucion'
    )

    tipo = models.CharField(max_length=15, choices=TIPOS)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Distribución del ingreso {self.ingreso.id}"


class DetalleDistribucion(models.Model):

    distribucion = models.ForeignKey(
        DistribucionIngreso,
        on_delete=models.CASCADE,
        related_name='detalles'
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='distribuciones'
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
            )
        ]

    def __str__(self):
        return f"{self.categoria.nombre}: S/ {self.monto}"


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
