from django import http
from django.template import RequestContext, loader
import urllib2
import json
import sys
from weatherproj.models import AvgRainByMonth
from weatherproj.models import MonthRainData
from bs4 import BeautifulSoup
from datetime import date
import json
from json import JSONEncoder
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
from sets import Set

def home(request):
  allRain = MonthRainData.objects.order_by('year', 'month').all()
  allAvgs = AvgRainByMonth.objects.order_by('month')
  retStr = 'Weather home test test ';
  years = Set()
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

  avgs = getAvgByMonth()
  totals = getRunningTotalObj(allRain, allAvgs)
  template = loader.get_template('data.html')
  context = RequestContext(request, {
                           'month_data' : mark_safe(json.dumps(month_data, cls=DjangoJSONEncoder)),
                           'years' : mark_safe(json.dumps(yearsObj, cls=DjangoJSONEncoder)),
                           'averages' : mark_safe(json.dumps(avgs, cls=DjangoJSONEncoder)),
                           'totals' : mark_safe(json.dumps(totals, cls=DjangoJSONEncoder))
                           })
  return http.HttpResponse(template.render(context))

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
def getAvgByMonth():
  allAvgs = AvgRainByMonth.objects.order_by('month');
  avgsData = {}
  for avg in allAvgs:
    avgsData[avg.month] = avg.avg_rain;
  data = {}
  data["averages"] = avgsData;
  return data



