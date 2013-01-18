from django.contrib.gis.geoip import GeoIP


def ip_to_coordinate(ip_address):
    g = GeoIP()
    return g.city(ip_address)


def set_cookies_from_location(request, location):
    request.session['latitude'], request.session['longitude'] = location['latitude'], location['longitude']
    request.session['city'], request.session['region'], request.session['country_name'] = location['city'], location['region'], location['country_name']


def set_cookies_from_latlng(request, lat, lng):
    request.session['latitude'], request.session['longitude'] = lat, lng


def get_location_from_cookies(request):
    if 'latitude' in request.session and 'country_name' in request.session:
        return {'latitude': request.session['latitude'],
                'longitude': request.session['longitude'],
                'city': request.session['city'],
                'region': request.session['region'],
                'country_name': request.session['country_name'], }
    elif 'latitude' in request.session and 'longitude' in request.session:
        return {'latitude': request.session['latitude'],
                'longitude': request.session['longitude'],
                'city': None,
                'region': None,
                'country_name': None, }
    else:
        return False
