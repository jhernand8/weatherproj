from django.contrib import admin
from django.urls import path
admin.autodiscover()
import weatherproj.views
urlpatterns = [
    # Examples:
    # url(r'^$', 'weatherproj.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    path('admin/', admin.site.urls),
    path('home/', weatherproj.views.home),
]
