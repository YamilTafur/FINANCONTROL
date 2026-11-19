
from django import forms
from .models import Categoria, Ingreso, Gasto, Presupuesto


class CategoriaForm(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = [
            "nombre",
            "tipo",
            "grupo_distribucion",
            "descripcion",
            "activa"
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        grupo = cleaned_data.get("grupo_distribucion")

        if tipo == "INGRESO" and grupo:
            self.add_error(
                "grupo_distribucion",
                "Las categorías de ingreso no necesitan grupo de distribución."
            )

        if tipo == "GASTO" and not grupo:
            self.add_error(
                "grupo_distribucion",
                "Selecciona Necesidades, Gustos o Deudas."
            )

        return cleaned_data


class IngresoForm(forms.ModelForm):

    class Meta:
        model = Ingreso
        fields = ["categoria", "presupuesto", "monto", "fecha", "descripcion"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["categoria"].queryset = Categoria.objects.filter(
            usuario=usuario,
            tipo="INGRESO",
            activa=True
        )

        self.fields["presupuesto"].queryset = Presupuesto.objects.filter(
            usuario=usuario
        )

        self.fields["presupuesto"].required = False

    def clean_monto(self):
        monto = self.cleaned_data["monto"]
        if monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor que cero.")
        return monto


class GastoForm(forms.ModelForm):

    class Meta:
        model = Gasto
        fields = ["categoria", "presupuesto", "monto", "fecha", "descripcion"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["categoria"].queryset = Categoria.objects.filter(
            usuario=usuario,
            tipo="GASTO",
            activa=True
        )

        self.fields["presupuesto"].queryset = Presupuesto.objects.filter(
            usuario=usuario
        )

        self.fields["presupuesto"].required = False

    def clean_monto(self):
        monto = self.cleaned_data["monto"]
        if monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor que cero.")
        return monto
