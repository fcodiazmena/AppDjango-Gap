from django.urls import path
from authenticate.views import iniciarSesion, salirSesion

urlpatterns = [
    path('', iniciarSesion, name='login'),
    path('logout/', salirSesion, name='logout'),
]
