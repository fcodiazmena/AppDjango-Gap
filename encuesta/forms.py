from django import forms
from django.core.exceptions import ValidationError
from encuesta.models import Empresa, Usuario

class EmpresaForm(forms.ModelForm):
    empresa = forms.ModelChoiceField(queryset=Empresa.objects.all(),
                                     widget=forms.Select(attrs={
                                         'class': 'form-control'
                                     }))

    class Meta:
        model = Usuario
        fields = ['empresa']

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})

            if kwargs['instance'].Empresa.all():
                initial['empresa'] = kwargs['instance'].Empresa.all()[0]
            else:
                initial['empresa'] = None

        forms.ModelForm.__init__(self, *args, **kwargs)

class UsuarioForm(forms.ModelForm):
    usuario = forms.ModelChoiceField(queryset=Usuario.objects.all(),
                                     widget=forms.Select(attrs={
                                         'class': 'form-control'
                                     }))

    class Meta:
        model = Usuario
        fields = ['empresa']