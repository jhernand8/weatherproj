from django import http
from django.template import RequestContext, loader
import urllib2
import json


def home(request):
  return http.HttpResponse('Weather home test.')
