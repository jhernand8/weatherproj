from django.core.management.base import BaseCommand, CommandError
import urllib2
from weatherproj.models import AvgRainByMonth
from weatherproj.models import MonthRainData
from bs4 import BeautifulSoup
from datetime import date

# Cron job that updates the Rain data - fills in missing rain data
# since 2000 and updates recent rain data that might have changed since
# last being updated.
class Command(BaseCommand):
  
  # main method to update the rain data
  def handle(self, *args, **options):
    minYear = 2000;
    today = date.today()
    outStr = ""
    allRain = MonthRainData.objects.order_by('year', 'month').all();
    for year in range(minYear, today.year + 1):
      for month in range(1, 13):
        if year == today.year and month > today.month:
          break
        rain = findForMonthAndYear(month, year, allRain);
        shouldUpdate = False
        if rain: # only update if no update date or update date is before end of that month
          if rain.update_date:
            if rain.update_date.year < year:
              shouldUpdate = True
            elif rain.update_date.year == year:
              if rain.update_date.month <= month:
                shouldUpdate = True
          else:
            shouldUpdate = True;
          if shouldUpdate:
            rain.delete()
        else:
          shouldUpdate = True
        if shouldUpdate:
          outStr += "updating rain for: " + str(year) + " " + str(month) + "\n"
          rainAmt = getRainAmountForMonth("KNUQ", month, year, False);
          rainObj = MonthRainData(month = month, year = year, rain = rainAmt, update_date = today)
          rainObj.save() 
  
  

  # Looks thru the list of MonthRainData objects for one with the
  # given month and year and returns that or none if not present.
  @staticmethod
  def findForMonthAndYear(month, year, allRain):
    for rain in allRain:
      if rain.month == month and rain.year == year:
        return rain
    return None;
  

  # returns the url to use to fetch data from 
  # weather underground for the given month and year
  # and given station
  @staticmethod
  def getUrlForMonth(station, month, year):
    return 'http://www.wunderground.com/history/airport/' + station + '/' + str(year) + '/' + str(month) + '/1/MonthlyHistory.html';


  # Returns a decimal with the amount of rain as a decimal
  # for the given month and year and place.
  # if isAvg, returns the average for the month. Otherwise the
  # total for the month
  @staticmethod
  def getRainAmountForMonth(station, month, year, isAvg):
    urlForData = getUrlForMonth(station, month, year)
    response = urllib2.urlopen(urlForData)
    responseData = response.readlines()
    responsehtml = "".join(responseData)
    parsed = BeautifulSoup(responsehtml)
    divs = parsed.select('div[class="precip-to-date"] > strong')
    if divs:
      if isAvg:
        return float(divs[1].get_text())
      return float(divs[0].get_text())
    return float("0.00")
  # updates the average rain table 
  @staticmethod
  def initAvgRain(request):
    allAvgs = AvgRainByMonth.objects.all()
    for avg in allAvgs:
      avg.delete()
    for month in range(1, 13):
      rainAvg = getRainAmountForMonth("KNUQ", month, 2013, True)
      avg = AvgRainByMonth(month = month, avg_rain = rainAvg)
      avg.save()
    return http.HttpResponse('average data saved.')
