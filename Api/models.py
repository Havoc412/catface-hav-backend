from django.db import models

# Create your models here.
class catInfor(models.Model):
    name = models.CharField(verbose_name="主名", max_length=10)
    sex = models.CharField(verbose_name="性别", max_length=10)
    kind = models.CharField(verbose_name="花色", max_length=10)
