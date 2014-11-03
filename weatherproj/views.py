from django import http
from django.template import RequestContext, loader
import urllib2
import json
from weatherproj.models import MonthRainData
from bs4 import BeautifulSoup

def home(request):
  #allRain = MonthRainData.objects.all()
  retStr = 'Weather home test';
  #if allRain:
    #for rain in allRain:
      #retStr += "<br/>" + rain.year + " " + rain.month + " " + rain.rain
  retStr += "parsed:  " + getRainAmountForMonth("KNUQ", 1, 2014)
  return http.HttpResponse(retStr)

# runs once to fetch the past n years of data for 
# 94043 and save it to the db
def initData(request):
  rain = MonthRainData(month = 11, year = 2013, rain = 0.12)
  rain.save()
  r2 = MonthRainData(month = 1, year = 2012, rain = 1.02)
  r2.save()
  return http.HttpResponse('Rain data saved.')

# returns the url to use to fetch data from 
# weather underground for the given month and year
# and given station
def getUrlForMonth(station, month, year):
  return 'http://www.wunderground.com/history/airport/' + station + '/' + year + '/' + month + '/1/MontlyHistory.html';

# Returns a decimal with the amount of rain as a decimal
# for the given month and year and place.
def getRainAmountForMonth(station, month, year):
  urlForData = getUrlForMonth(station, month, year)
  response = urllib2.urlopen(urlForData)
  responseData = response.readLines()
  parsed = BeautifulSoup(responseData)
  divs = parsed.find("div", "precip-to-date", True)
  datastr = ""
  for d in divs:
    datastr += str(d) + ":::"
  return datastr
