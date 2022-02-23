from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import *

admin.site.register(organisation,LeafletGeoAdmin)
admin.site.register(employee, LeafletGeoAdmin)
admin.site.register(attendence)
admin.site.register(announcement)
admin.site.register(personalMsg)
admin.site.register(attendenceReq)