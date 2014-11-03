import uuid
from django.db import models

# rain amount in inches for a given month in a given location
class RainDataMonth(models.Model):
  month = models.IntegerField()
  rain = models.FloatField()
  year = models.IntegerField()
  id = models.UUIDField(primary_key = True, default=uuid.uuid4, editable=False)
