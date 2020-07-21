from django.urls import path
from encuesta.views import index, pregunta_list, subdominio_list, resultado, usuario_list, usuario_add, usuario_delete, empresa_add, admin_pregunta_add

urlpatterns = [
    path('', index, name='index'),
    path('<int:id_dominio>/', pregunta_list, name="pregunta_list"),
    path('<int:id_dominio>/<int:id_subdominio>/', subdominio_list, name="subdominio_list"),
    path('resultado/grafico/<int:id_empresa>', resultado, name="resultado"),
    path('usuario/', usuario_list, name="usuario_list"),
    path('usuario/agregar/', usuario_add, name="usuario_add"),
    path('usuario/eliminar/', usuario_delete, name="usuario_delete"),
    path('empresa/agregar/', empresa_add, name="empresa_add"),
    path('pregunta/agregar/', admin_pregunta_add, name="admin_pregunta_add"),
]