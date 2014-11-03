from django import http
from django.template import RequestContext, loader
import urllib2
import json
from weatherproj.models import RainDataMonth

def home(request):
  allRain = RainDataMonth.objects.all()
  retStr = 'Weather home test';
  if allRain:
    for rain in allRain:
      retStr += "<br/>" + rain.year + " " + rain.month + " " + rain.rain
  return http.HttpResponse(retStr)

# runs once to fetch the past n years of data for 
# 94043 and save it to the db
def initData(request):
  rain = Rain(month = 11, year = 2013, rain = 0.12)
  rain.save()
  r2 = Rain(month = 1, year = 2012, rain = 1.02)
  r2.save()
  return http.HttpResponse('Rain data saved.')
