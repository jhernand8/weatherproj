from django import http
from django.template import RequestContext, loader
import urllib2
import json
from weatherproj.models import AvgRainByMonth
from weatherproj.models import MonthRainData
from bs4 import BeautifulSoup
from datetime import date

def home(request):
  allRain = MonthRainData.objects.all()
  retStr = 'Weather home test';
  if allRain:
    for rain in allRain:
      retStr += "<br/>" + str(rain.year) + " " + str(rain.month) + " " + str(rain.rain)
  retStr += "parsed:  " + str(getRainAmountForMonth("KNUQ", 1, 2014, False))
  return http.HttpResponse(retStr)

# runs once to fetch the past n years of data for 
# 94043 and save it to the db
def initData(request):
  allRain = MonthRainData.objects.all();
  if allRain:
    for rain in allRain:
      rain.delete();
  avgs = AvgRainByMonth.objects.all()
  for a in avgs:
    a.delete()

  today = date.today()
  for year in range(2004, today.year + 1) :
    for month in range(1, 13):
      if year == today.year and month > today.month:
        break
      rainAmt = getRainAmountForMonth("KNUQ", month, year, False)
      rainObj = Rain(month = month, year = year, rain = rainAmt)
      rainObj.save()
  for month in range(1, 13):
    rainAvg = getRainAmountForMonth("KNUQ", month, 2013, True)
    avg = AvgRainByMonth(month = month, avg_rain = rainAvg)
    avg.save()
  return http.HttpResponse('Rain data saved.')

# returns the url to use to fetch data from 
# weather underground for the given month and year
# and given station
def getUrlForMonth(station, month, year):
  return 'http://www.wunderground.com/history/airport/' + station + '/' + str(year) + '/' + str(month) + '/1/MonthlyHistory.html';

# Returns a decimal with the amount of rain as a decimal
# for the given month and year and place.
# if isAvg, returns the average for the month. Otherwise the
# total for the month
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
