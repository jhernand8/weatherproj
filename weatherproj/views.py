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

# runs to update data that is stale from 2000 to present
# 94043 and save it to the db
def initData(request):
  minYear = 2000;
  today = date.today()
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
            if rain.update_date.month >= month:
              shouldUpdate = True
        if shouldUpdate:
          rain.delete()
      else:
        shouldUpdate = True
      if shouldUpdate:
        print "updating rain for: " + str(year) + " " + str(month) + "\n"
        rainAmt = getRainAmountForMonth("KNUQ", month, year, False);
        rainObj = MonthRainData(month = month, year = year, rain = rainAmt, update_date = today)
        rainObj.save() 

  return http.HttpResponse('Rain data saved.');
 
# Looks thru the list of MonthRainData objects for one with the
# given month and year and returns that or none if not present.
def findForMonthAndYear(month, year, allRain):
  for rain in allRain:
    if rain.month == month and rain.year == year:
      return rain
  return None;

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
