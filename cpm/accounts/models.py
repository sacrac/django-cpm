from django.contrib.auth.models import User
from django.db import models

from core.models import Slugged, DateStamp

# Create your models here.
#TODO: AD IPADDRESS FIELD TO USERS

class Visit(DateStamp):
    ip_address = models.ForeignKey('IPAddress', null=True, blank=True, related_name="visits")

class IPAddress(models.Model):
    ip_address = models.IPAddressField(blank=True, unique=True)

class Note(DateStamp):
    content = models.TextField(blank=True)
    user = models.ForeignKey(User)

    class Meta:
        permissions = (
            ("view_note", "Can view note"),
        )

class Company(Slugged):
    pass

class Client(models.Model):
    user = models.OneToOneField(User, related_name='client_profile')
    phone = models.IntegerField(null=True)
    c_phone = models.IntegerField(null=True)
    w_phone = models.IntegerField(null=True)
    company = models.ForeignKey(Company, blank=True, null=True, related_name='employees')
    title = models.CharField(max_length=255, blank=True)
    location = models.CommaSeparatedIntegerField(max_length=1000, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    ip_addresses = models.ManyToManyField(IPAddress, blank=True, null=True)



