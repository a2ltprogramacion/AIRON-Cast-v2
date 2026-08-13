from django.db import models


class Product(models.Model):
    codigo = models.CharField(max_length=50, primary_key=True, unique=True)
    producto = models.TextField()
    tipo = models.CharField(max_length=200, blank=True, null=True)
    precio_usd = models.FloatField(default=0)
    precio_bcv = models.FloatField(default=0)
    actualizado_el = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.producto[:50]}"


class MessageTemplate(models.Model):
    titulo = models.CharField(max_length=300)
    categoria = models.CharField(max_length=200, blank=True, null=True)
    contenido = models.TextField()
    copy_count = models.PositiveIntegerField(default=0)
    creado_el = models.DateTimeField(auto_now_add=True)
    actualizado_el = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Plantilla de Mensaje"
        verbose_name_plural = "Plantillas de Mensajes"
        ordering = ["categoria", "titulo"]

    def __str__(self):
        return self.titulo