from django.contrib import admin
from encuesta.models import Dominio, Subdominio, Pregunta, Respuesta, Empresa, Usuario

class DominioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa')

class SubdominioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dominio')

class PreguntaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'subdominio', 'usuario')

class RespuestaAdmin(admin.ModelAdmin):
    list_display = ('pregunta',)

class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'empresa')

admin.site.register(Dominio, DominioAdmin)
admin.site.register(Subdominio, SubdominioAdmin)
admin.site.register(Pregunta, PreguntaAdmin)
admin.site.register(Respuesta, RespuestaAdmin)
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Usuario, UsuarioAdmin)
