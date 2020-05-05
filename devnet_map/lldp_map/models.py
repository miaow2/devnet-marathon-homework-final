from django.db import models

# Create your models here.
class Device(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True
    )
    ip_address = models.CharField(
        max_length=20,
        verbose_name='IP Address'
    )

    def __str__(self):
        return self.name