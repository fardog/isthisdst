from geonames.geonames import GeoNames
from geolocation.models import TimezoneCache
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from django.conf import settings


MAX_TZ_SEARCH_DAYS = getattr(settings, 'MAX_TZ_SEARCH_DAYS', 365)


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
    utc = timezone('UTC')
    dt = tz.localize(localtime.replace(tzinfo=utc))

    response = {
            'previous': dt,
            'previous_abbrev': dt.tzname(),
            'in_dst': True if dt.dst() else False,
            'offset': dt.dst()
        }
    originally_dst = dt.dst()

    for days in range(MAX_TZ_SEARCH_DAYS):
        d = tz.normalize(
            dt + timedelta(days = days)
        )
        if originally_dst and not d.dst():
            response.update({
                'next': d,
                'next_abbrev': d.tzname()
            })
            return response
        elif not originally_dst and d.dst():
            response.update({
                'next': d,
                'next_abbrev': d.tzname(),
                'offset': d.dst()  # We were not in DST originally, so offset was 0
            })
            return response
    return None
