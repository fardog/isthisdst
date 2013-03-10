from django.shortcuts import render
from geolocation.utils import *
from utils import *
from datetime import timedelta
from pytz import timezone


def index(request):
    location = get_location_from_cookies(request)
    dst = offset_neg = offset_min = offset_hr = False
    observes = True
    latitude = longitude = failure_message = next_transition = offset = offset_fmt = tzname = None

    # Flush our cookies if our IP address has changed since last time
    if 'last_ip' in request.session and 'REMOTE_ADDR' in request.META:
        if request.session['last_ip'] != request.META['REMOTE_ADDR']:
            request.session.flush()

    # Now see if we have session data already.
    if 'latitude' in request.session and 'longitude' in request.session:
        latitude, longitude = request.session['latitude'], request.session['longitude']
    # If we don't, set it from the remote address
    elif 'REMOTE_ADDR' in request.META:
        try:
            request.session['last_ip'] = request.META['REMOTE_ADDR']
            location = ip_to_coordinate(request.META.get('REMOTE_ADDR'))
            set_cookies_from_location(request, location)
            latitude, longitude = location['latitude'], location['longitude']
        except Exception:
            failure_message = u"We failed to divine your location, even though there was some data on you. It just wasn't enough, sorry."
    # Complain if we couldn't find anything.
    else:
        failure_message = u"Failed to divine your location. Sorry."

    # If we did get something, get timezone data
    if latitude and longitude:
        dst = False
        tzdata = get_tzdata(latitude, longitude)
        tzname = tzdata['timezoneId']
        # calculated = calculate_dst_dates(timezone(tzdata['timezoneId']), datetime(2013, 01, 04, 00, 00))
        calculated = calculate_dst_dates(timezone(tzdata['timezoneId']), datetime.utcnow())

        if not calculated:
            observes = False
        elif calculated['in_dst']:
            dst = True

        if calculated:
            if dst:
                offset = timedelta(0) - calculated['offset']
                offset_neg = True
            else:
                offset = calculated['offset']

            offset_hr, remainder = divmod(calculated['offset'].seconds, 3600)
            offset_min, seconds = divmod(remainder, 60)

            next_transition = calculated['next'] - timedelta(seconds=1) - offset

    # Make it rain
    return render(request, 'isthisdst.html',
                  {'dst': dst, 'failure_message': failure_message,
                   'latitude': latitude, 'longitude': longitude,
                   'location': location, 'timezone': tzname, 'observes': observes,
                   'next_transition': next_transition,
                   'offset': offset, 'offset_fmt': offset_fmt, 'offset_neg': offset_neg, 'offset_min': offset_min, 'offset_hr': offset_hr, })
