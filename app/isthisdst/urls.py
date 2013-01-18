from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'isthisdst.views.home', name='home'),
    # url(r'^isthisdst/', include('isthisdst.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),

    url(r'^location/ip/(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/', 'geolocation.views.set_by_ip'),
    # url(r'^location/ip/', 'geolocation.views.set_by_ip'),
    url(r'^location/lat/(?P<lat>(?:\-)?\d+(?:\.\d+)?)/lng/(?P<lng>(?:\-)?\d+(?:\.\d+)?)/', 'geolocation.views.set_by_latlng'),
    url(r'^location/flush/', 'geolocation.views.flush'),
    url(r'^$', 'isthisdst.views.index'),
)
