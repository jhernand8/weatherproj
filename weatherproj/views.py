from django import http
from django.shortcuts import render
from django.template import RequestContext, loader
import json
import sys
from weatherproj.models import AvgRainByMonth
from weatherproj.models import MonthRainData
from weatherproj.models import ZipToUrl
from bs4 import BeautifulSoup
from datetime import date
import json
from json import JSONEncoder
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe

# Helper function to turn list of ZipToUrl into json array.
def makeZipUrlJson(allZipsToUrls):
  zipData = []
  for zipToUrl in allZipsToUrls:
    data = {}
    data["zip"] = zipToUrl.zip
    data["url"] = zipToUrl.url
    zipData.append(data)
  return zipData

def home(request):
  retStr = 'Weather home test test ';
  years = set()
  allZipsToUrls = ZipToUrl.objects.all();
  zipJson = makeZipUrlJson(allZipsToUrls);
  # if no zip code just show list of zip codes
  if "zip" not in request.GET:
    context = { 'zipsToUrls': mark_safe(json.dumps(zipJson, cls=DjangoJSONEncoder)), 'hasData': False};
    return render(request, 'data.html', context);
  
  zip = request.GET["zip"];
  currZip = request.GET["zip"];
  allRain = MonthRainData.objects.order_by('year', 'month').all().filter(zip=currZip)
  allAvgs = AvgRainByMonth.objects.order_by('month').filter(zip=currZip)
  month_data = []
  if allRain:
    for rain in allRain:
      years.add(rain.year)
      month_obj = {}
      month_obj["rain"] = rain.rain
      month_obj["month"] = rain.month
      month_obj["year"] = rain.year
      month_obj["avg"] = allAvgs[rain.month - 1].avg_rain
      month_data.append(month_obj)
  yearsObj = {}
  yearsObj["years"] = list(years)

  avgs = getAvgByMonth(zip)
  totals = getRunningTotalObj(allRain, allAvgs)
  context = {
                           'month_data' : mark_safe(json.dumps(month_data, cls=DjangoJSONEncoder)),
                           'years' : mark_safe(json.dumps(yearsObj, cls=DjangoJSONEncoder)),
                           'averages' : mark_safe(json.dumps(avgs, cls=DjangoJSONEncoder)),
                           'totals' : mark_safe(json.dumps(totals, cls=DjangoJSONEncoder)),
                           'zip': zip, 'hasData': True,
                           'zipsToUrls': mark_safe(json.dumps(zipJson, cls=DjangoJSONEncoder))}
  return render(request, 'data.html', context))

# Constructs object to pass to html for the running total and average
# running total for each month in each year of rainfall for that season -
# season being July 1 - June 30.
def getRunningTotalObj(allRain, allAvgs):
  runningTotalAvg = getRunningTotalAverages(allAvgs)
  totalObj = {}
  totals = []
  currSum = 0;
  for monthRain in allRain:
    # reset sum when we get to July as it starts a new "season"
    if monthRain.month == 7:
      currSum = 0
    currSum += monthRain.rain
    monthTotalObj = {}
    monthTotalObj["month"] = monthRain.month
    monthTotalObj["year"] = monthRain.year
    monthTotalObj["avg"] = runningTotalAvg[monthRain.month]
    monthTotalObj["rain"] = currSum
    totals.append(monthTotalObj)
  totalObj["runningTotals"] = runningTotalAvg
  totalObj["monthTotals"] = totals
  
  return totalObj;

# Returns object with the average running total rainfall during season thru month.
def getRunningTotalAverages(allAvgs):
  totals = {}
  sum = 0
  for month in range(7, 13):
    sum += allAvgs[month - 1].avg_rain
    totals[month] = sum
  for month in range(1, 7):
    sum += allAvgs[month - 1].avg_rain
    totals[month] = sum
  return totals
  
# Returns object of the average rain by month which can be converted to a json object
def getAvgByMonth(zip):
  allAvgs = AvgRainByMonth.objects.order_by('month');
  avgsData = {}
  for avg in allAvgs:
    if avg.zip != zip:
      continue;
    avgsData[avg.month] = avg.avg_rain;
  data = {}
  data["averages"] = avgsData;
  return data



