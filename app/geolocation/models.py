from django.conf import settings
from django.db import models
from django.utils import timezone

class TimezoneCache (models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    timezoneId = models.CharField(max_length=128)
    rawOffset = models.FloatField()
    expires = models.DateTimeField()

    def __unicode__(self):
        return u"%s,%s" % (self.latitude, self.longitude)

    class Meta:
        ordering = ['-id']
