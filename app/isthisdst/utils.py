from geonames.geonames import GeoNames
from geolocation.models import TimezoneCache
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from django.conf import settings


def get_tzdata(lat, lng):
    tzdata = None
    try:
        cache_info = TimezoneCache.objects.get(latitude=round(float(lat), 1), longitude=round(float(lng), 1))
        if datetime.utcnow().replace(tzinfo=pytz.utc) > cache_info.expires:
            cache_info.delete()
            cache_info = None
        else:
            tzdata = {'timezoneId': cache_info.timezoneId, 'rawOffset': cache_info.rawOffset, }
    except TimezoneCache.DoesNotExist:
        tzdata = None
    except TimezoneCache.MultipleObjectsReturned:
        tzdata = None
        TimezoneCache.objects.filter(latitude=round(float(lat), 1), longitude=round(float(lng), 1)).delete()

    if not tzdata:
        tzdata = GeoNames(username=settings.GEONAMES_USER).timezone(lat, lng)
        t = TimezoneCache(latitude=round(float(lat), 1), longitude=round(float(lng), 1),
                          timezoneId=tzdata['timezoneId'], rawOffset=float(tzdata['rawOffset']),
                          expires=datetime.utcnow() + timedelta(weeks=2), )
        t.save()

    return tzdata


def calculate_dst_dates(tz, localtime=datetime.utcnow()):
    offset = 0
    offset_amt = None
    previousdt = None
    utc = timezone('UTC')

    for dt in tz._utc_transition_times:
        if dt.year < 2011:
            offset = offset + 1
            continue
        if dt > localtime:
            in_dst = False
            if tz._transition_info[offset - 1][1] > timedelta(microseconds=1):
                in_dst = True
                offset_amt = tz._transition_info[offset - 1][1]
            else:
                offset_amt = tz._transition_info[offset][1]
            return {'previous': tz.normalize(utc.localize(previousdt)), 'previous_abbrev': tz._transition_info[offset - 1][2],
                    'next': tz.normalize(utc.localize(dt)), 'next_abbrev': tz._transition_info[offset][2],
                    'in_dst': in_dst, 'offset': offset_amt, }
        previousdt = dt
        offset = offset + 1

    return None
