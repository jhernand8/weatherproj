from django.db import models

# rain amount in inches for a given month in a given location
class MonthRainData(models.Model):
  month = models.IntegerField()
  rain = models.FloatField()
  year = models.IntegerField()

# stores the average amount of rain for a given month
class AvgRainByMonth(models.Model):
  month = models.IntegerField(primary_key = True)
  avg_rain = models.FloatField()

