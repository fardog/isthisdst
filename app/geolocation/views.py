from django.http import HttpResponseRedirect
from utils import ip_to_coordinate, set_cookies_from_location, set_cookies_from_latlng


def set_by_ip(request, ip=None):
    if ip:
        location = ip_to_coordinate(ip)
        if location:
            request.session.flush()
            request.session['ip'] = ip
            set_cookies_from_location(request, location)
    else:
        print ("Invalid IP Passed")
    return HttpResponseRedirect('/')


def set_by_latlng(request, lat=None, lng=None):
    latitude, longitude = float(lat), float(lng)
    if (-90 <= int(latitude) <= 90) and (-180 <= int(longitude) <= 180):
        request.session.flush()
        set_cookies_from_latlng(request, latitude, longitude)
    else:
        print ("Bad lat/lng passed")
    return HttpResponseRedirect('/')


def flush(request):
    request.session.flush()
    return HttpResponseRedirect('/')
