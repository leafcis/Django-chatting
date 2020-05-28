from django.db import models

class Room(models.Model):

  title = models.CharField(max_length=100)
  member = models.IntegerField()

# Create your models here.
