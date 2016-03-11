from django.conf.urls import include, url
from django.contrib import admin
from django.http.response import HttpResponse

urlpatterns = [
    url(r'^', include('smart_heating.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /")),
]
