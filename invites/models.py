from django.db import models
from accounts.models import Account
from events.models import Event

class Invitation(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,related_name="invitee")
    eventcode = models.ForeignKey(Event,on_delete=models.CASCADE)
    invitation_from = models.ForeignKey(Account,on_delete=models.CASCADE,related_name="invitation_from")
    rsvp_done = models.BooleanField(default=False)
    rsvp_reject = models.BooleanField(default=False)
    remarks = models.CharField(max_length=300,blank=True)
    guest_count = models.DecimalField(max_digits=1, decimal_places=0,default = 1)
    name_for_invitation_without_registering = models.CharField(max_length=100,null=True,blank=True)
    email_for_invitation_without_registering = models.EmailField(null=True,blank=True)
    phone_for_invitation_without_registering = models.CharField(max_length=11,null=True,blank=True)
    
    def __str__(self):
        return str(self.user)+'_'+str(self.eventcode)+'_'+str(self.invitation_from)+'_'+str(self.id)
