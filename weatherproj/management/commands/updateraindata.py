from django.core.management.base import BaseCommand, CommandError
import urllib2
from weatherproj.models import AvgRainByMonth
from weatherproj.models import MonthRainData
from weatherproj.models import ZipToUrl
from bs4 import BeautifulSoup
from datetime import date
from datetime import timedelta

# Cron job that updates the Rain data - fills in missing rain data
# since 2000 and updates recent rain data that might have changed since
# last being updated.
class Command(BaseCommand):
  
  # main method to update the rain data
  def handle(self, *args, **options):
    minYear = 2000;
    today = date.today()
    allZips = ZipToUrl.objects.all();
    allRain = MonthRainData.objects.order_by('year', 'month').all();
    # for each zip code
    for currZip in allZips:
      # go thru all months since minYear and see if there's data that needs
      # to be created or updated.
      for year in range(minYear, today.year + 1):
        for month in range(1, 13):
          if year == today.year and month > today.month:
            break
          rain = self.findForMonthAndYear(month, year, currZip.zip, allRain);
          shouldUpdate = False
          if rain:
            shouldUpdate = self.should_update(rain)
            if shouldUpdate:
              rain.delete()
          else:
            shouldUpdate = True
          if shouldUpdate:
            rainAmt = self.getRainAmountForMonth(currZip, month, year, False);
            rainObj = MonthRainData(month = month, year = year, rain = rainAmt, update_date = today, zip = currZip.zip)
            rainObj.save() 
    # upate any averages if missing for any zip code
    allAvgs = AvgRainByMonth.objects.all()
    self.initAvgRain(allAvgs, allZips);


  # Helper to decide if we should update this rain object.
  # Update if no update date or if update date is before the end
  # of rain's month (with some buffer).
  def should_update(self, rain):
    if not rain.update_date:
      return True
    # approx end of month - using 28 since know all months have at least 28 days
    rain_month_end = date(rain.year, rain.month, 28)
    # add two weeks - buffer - so during two weeks after end of prev month
    # will still update that month - in case there are changes/updates
    two_weeks = timedelta(days=14)
    rain_month_end = rain_month_end + two_weeks
    if rain.update_date < rain_month_end:
      return True
    return False

  # Looks thru the list of MonthRainData objects for one with the
  # given month and year and returns that or none if not present.
  def findForMonthAndYear(self, month, year, zip, allRain):
    for rain in allRain:
      if rain.month == month and rain.year == year and rain.zip == zip:
        return rain
    return None;
  

  # returns the url to use to fetch data from 
  # weather underground for the given month and year
  # and given station
  def getUrlForMonth(self, station, month, year):
    return 'http://www.wunderground.com/history/airport/' + station + '/' + str(year) + '/' + str(month) + '/1/MonthlyCalendar.html';


  # Returns a decimal with the amount of rain as a decimal
  # for the given month and year and place.
  # if isAvg, returns the average for the month. Otherwise the
  # total for the month
  def getRainAmountForMonth(self, zipToUrl, month, year, isAvg):
    urlForData = self.getUrlForMonth(zipToUrl.url, month, year)
    response = urllib2.urlopen(urlForData)
    responseData = response.readlines()
    responsehtml = "".join(responseData)
    parsed = BeautifulSoup(responsehtml)
    divs = parsed.select('div[class="precip-to-date"] > strong')
    if divs:
      divText = ""
      if isAvg:
        divText = divs[2].get_text()
      else:
        divText = divs[1].get_text()
      if divText.find(" in") > -1:
        ind = divText.find(" in")
        divText = divText[:ind]
      return float(divText)
    return float("0.00")

  # updates the average rain table 
  def initAvgRain(self, allAvgs, allZips):
    for currZipToUrl in allZips:
      for month in range(1, 13):
        if self.needsAvgData(currZipToUrl, month, allAvgs):
          rainAvg = self.getRainAmountForMonth(currZipToUrl, month, 2013, True)
          avg = AvgRainByMonth(month = month, avg_rain = rainAvg, zip = currZipToUrl.zip)
          avg.save()
          

  # Returns true if there is no data in all the averages for the given
  # month and zip code.
  def needsAvgData(self, zipToUrl, month, allAvgData):
    for avg in allAvgData:
      if avg.zip == zipToUrl.zip and avg.month == month:
        return False
    return True


