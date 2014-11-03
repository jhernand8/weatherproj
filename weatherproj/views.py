from django import http
from django.template import RequestContext, loader
import urllib2
import json
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
  allRain = MonthRainData.objects.order_by('year', 'month')
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
  template = loader.get_template('data.html')
  # from django.utils.safestring import mark_safe
  context = RequestContext(request, {
                           'month_data' : mark_safe(json.dumps(month_data, cls=DjangoJSONEncoder)),
                           'years' : mark_safe(json.dumps(yearsObj, cls=DjangoJSONEncoder)) })
  return http.HttpResponse(template.render(context))

# runs once to fetch data for the given year
# 94043 and save it to the db
def initData(request):
  year = int(request.GET.get('year', '2013'));
  allRain = MonthRainData.objects.all();
  if allRain:
    for rain in allRain:
      if rain.year == year:
        rain.delete();

  today = date.today()
  monthsProc = "";
  for month in range(1, 13):
    if year == today.year and month > today.month:
      break
    monthsProc += str(month) + ", ";
    rainAmt = getRainAmountForMonth("KNUQ", month, year, False)
    rainObj = MonthRainData(month = month, year = year, rain = rainAmt)
    rainObj.save()
  return http.HttpResponse('Rain data saved. Months: ' + monthsProc)
 
# updates the average rain table 
def initAvgRain(request):
  allAvgs = AvgRainByMonth.objects.all()
  for avg in allAvgs:
    avg.delete()
  for month in range(1, 13):
    rainAvg = getRainAmountForMonth("KNUQ", month, 2013, True)
    avg = AvgRainByMonth(month = month, avg_rain = rainAvg)
    avg.save()
  return http.HttpResponse('average data saved.')

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
