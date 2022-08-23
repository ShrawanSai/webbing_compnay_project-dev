from django.db import models
import datetime
from accounts.models import Account
from ckeditor.fields import RichTextField
from phonenumber_field.modelfields import PhoneNumberField

THEME_CHOICES = (
    ('bridge-theme.css','Bridge Theme'),
    ('dark-red-theme.css','Dark red Theme'),
    ('default-theme.css','Default Theme'),
    ('green-theme.css','Green Theme'),
    ('jelly-bean-theme.css','Jelly Bean Theme'),
    ('lite-blue-theme.css','Light Blue Theme'),
    ('orange-theme.css','Orange Theme'),
    ('pink-theme.css','Pink Theme'),
    ('purple-theme.css','Purple Theme'),
    ('red-theme.css','Red Theme')
)

class Event(models.Model):
    title = models.CharField(max_length=200)
    eventcode = models.CharField(max_length=50,primary_key=True)
    #description = models.TextField(blank=True)
    description = RichTextField(blank=True)
    eventtype = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=200)
    contactperson = models.CharField(max_length=200)
    contactpersonphone = PhoneNumberField()
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    mark_event_as_completed = models.BooleanField(default=False)
    image = models.ImageField(upload_to='events/images/',blank=True)

    invitation_email_subject = models.CharField(max_length=200, blank=True)
    invitation_email_content = RichTextField(blank=True)

    invitation_whatsapp_content = models.TextField(blank=True,null=True)
    invitation_image = models.ImageField(upload_to='events/images/',blank=True,null = True)

    #event date range, event dates,event start time, event end time (optional), 
    eventstartdate = models.DateField()
    eventenddate = models.DateField()
    event_start_time = models.TimeField(default=datetime.time(00, 00))
    event_end_time = models.TimeField(blank = True,null=True)
    information_on_schedule = models.TextField(blank=True,null = True)

    event_venue_iframe = models.TextField(blank = True,null=True)
    event_venue_photo = models.ImageField(upload_to='events/images/',blank=True,null=True)
    eventrange = models.PositiveSmallIntegerField(default = 1)
    information_on_venue = models.TextField(blank=True,null = True)

    rsvp_option = models.BooleanField(default=True)
    scheduling_option = models.BooleanField(default=True)
    gallery_option = models.BooleanField(default=True)
    wishes_option = models.BooleanField(default=True)
    rsvp_code = models.CharField(max_length=7,blank=True)
    theme = models.CharField(max_length=50, choices=THEME_CHOICES, default='default-theme.css')

    def __str__(self):
        return self.eventcode

    def save(self, *args, **kwargs):
        date_diff = self.eventenddate - self.eventstartdate
        self.eventrange = date_diff.days + 1
        super(Event, self).save(*args, **kwargs)
    
class Invitee(models.Model):
    eventcode = models.ForeignKey(Event,on_delete=models.CASCADE)
    invitee = models.ForeignKey(Account,on_delete=models.CASCADE,related_name="invitation_for_user")
    invitee_name = models.CharField(max_length=70)
    invitee_email = models.EmailField(max_length=70,null = True, blank = True)
    invitee_phone = PhoneNumberField(null = True, blank = True)
    invitee_email_sent = models.BooleanField(default=False)
    invitee_whatsapp_sent = models.BooleanField(default=False)
    invitee_rsvp = models.BooleanField(default=False)
    invitee_guest_count = models.DecimalField(max_digits=1, decimal_places=0)
    def __str__(self):
        return self.invitee_name

class EventDate(models.Model):
    day_eventcode = models.ForeignKey(Event,on_delete=models.CASCADE)
    day_date = models.DateField(default=datetime.date.today)
    day_dayname = models.CharField(max_length=70,default="Day")
    def __str__(self):
        return str(self.day_eventcode)+'_'+str(self.day_dayname)

class Schedule(models.Model):
    item_eventcode = models.ForeignKey(Event,on_delete=models.CASCADE)
    item_date = models.ForeignKey(EventDate,on_delete=models.CASCADE)
    item_name = models.CharField(max_length=70,default="Item")
    item_start_time = models.TimeField(default=datetime.time(00, 00))
    item_end_time = models.TimeField(null=True)
    item_optional_detail = models.TextField(null=True)
    item_icon_image = models.ImageField(upload_to='events/images/',blank=True)
    def __str__(self):
        return str(self.item_eventcode)+'_'+str(self.item_name)


class EventPhotoAlbum(models.Model):
    album_name = models.CharField(max_length=70,default="Album")
    album_eventcode = models.ForeignKey(Event,on_delete=models.CASCADE)
    album_owner = models.ForeignKey(Account,on_delete=models.CASCADE)
    album_approved = models.BooleanField(default=False)
    album_created_date = models.DateTimeField(auto_now_add=True)
    album_thumbnail = models.FileField(upload_to='events/images/',null = True, blank = True)

    def __str__(self):

        return str(self.album_eventcode)+'_'+str(self.album_name)+'_'+str(self.id)

class EventPhoto(models.Model):
    photo_name = models.CharField(max_length=70,blank=True)
    photo_poster = models.ForeignKey(Account,on_delete=models.CASCADE)
    photo_album = models.ForeignKey(EventPhotoAlbum,on_delete=models.CASCADE, null = True, blank = True)
    photo_eventcode = models.ForeignKey(Event,on_delete=models.CASCADE)
    photo = models.FileField(upload_to='events/images/')
    photo_approved = models.BooleanField(default=False)
    photo_created_date = models.DateTimeField(auto_now_add=True)
    photo_name_display = models.BooleanField(default=False)
    photo_carousel_picture = models.BooleanField(default=False)

    def __str__(self):
        return str(self.photo_poster)+'_'+str(self.photo_eventcode)+'_'+str(self.id)


class Wish(models.Model):
    wish_poster = models.ForeignKey(Account,on_delete=models.CASCADE)
    wish_eventcode = models.ForeignKey(Event,on_delete=models.CASCADE)
    wish_message = models.TextField(blank=True)
    wish_photo = models.FileField(upload_to='events/images/',blank=True,null = True)
    wish_byline = models.CharField(max_length=70,blank=True,null = True)
    wish_created_date = models.DateTimeField(auto_now_add=True)
    wish_approved = models.BooleanField(default=False)
    def __str__(self):
        return str(self.wish_poster)+'_'+str(self.wish_eventcode)+'_'+str(self.id)


