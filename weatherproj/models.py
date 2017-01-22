from django.db import models

# rain amount in inches for a given month in a given location
class MonthRainData(models.Model):
  month = models.IntegerField()
  rain = models.FloatField()
  year = models.IntegerField()
  update_date = models.DateField()
  zip = models.TextField()

# stores the average amount of rain for a given month
class AvgRainByMonth(models.Model):
  month = models.IntegerField()
  avg_rain = models.FloatField()
  zip = models.TextField()
  avg_id = models.AutoField(primary_key = True)

# Stores the zip codes to load data for as well as the url to use
# to load/get the data.
class ZipToUrl(models.Model):
  zip = models.TextField(unique=True, primary_key = True)
  url = models.TextField()
