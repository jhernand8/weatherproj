from django.db import models

# rain amount in inches for a given month in a given location
class MonthRainData(models.Model):
  month = models.IntegerField()
  rain = models.FloatField()
  year = models.IntegerField()
