from django.db import models
from django.contrib.auth.models import User


class Empresa(models.Model):
    nombre = models.CharField(max_length=45, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Dominio(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)
    empresa = models.ForeignKey(
        Empresa, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre + ' / ' + self.empresa.nombre


class Subdominio(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)
    dominio = models.ForeignKey(
        Dominio, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre + ' / ' + self.dominio.empresa.nombre

class Usuario(models.Model):
    user = models.OneToOneField(
        User, blank=True, null=True, on_delete=models.CASCADE)
    empresa = models.ForeignKey(
        Empresa, blank=True, null=True, on_delete=models.CASCADE)
    administrador = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + ' / ' + self.empresa.nombre

class Pregunta(models.Model):
    titulo = models.CharField(max_length=255, blank=True, null=True)
    subdominio = models.ForeignKey(
        Subdominio, blank=True, null=True, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo + ' / ' + self.usuario.user.username + ' / ' + self.subdominio.dominio.empresa.nombre


class Respuesta(models.Model):
	pregunta = models.OneToOneField(Pregunta, null=True, blank=True, related_name="respuesta", on_delete=models.CASCADE)
	voto = models.CharField(max_length=10, default='Falso')

	def __str__(self):
		return '%s : ¿ %s ? : %s' % (self.pregunta.subdominio.nombre, self.pregunta.titulo, self.voto)
