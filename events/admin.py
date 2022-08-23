from django.contrib import admin
from .models import Event,Invitee, Schedule,EventDate,EventPhoto,EventPhotoAlbum,Wish

class EventAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)

admin.site.register(Event,EventAdmin)
admin.site.register(Invitee)
admin.site.register(Schedule)
admin.site.register(EventDate)
admin.site.register(EventPhoto)
admin.site.register(EventPhotoAlbum)
admin.site.register(Wish)