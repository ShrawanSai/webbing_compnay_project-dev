from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,UserChangeForm 
from events.models import Event,Invitee,Schedule,EventPhoto,EventPhotoAlbum
from .widgets import DatePickerInput, TimePickerInput, DateTimePickerInput
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model  
from accounts.models import Account
from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()  

class DateInput(forms.DateInput):
    input_type = 'date'

class CustomUserCreationForm(UserCreationForm):  
  
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)  
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)  
    #phonenumber = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': 'Phone'}))
  
    class Meta:  
        model = Account  
        fields = ('email', 'phone_number', 'username')  

    labels = {
        'phone_number' : "PHONE NUMBER (Include country code as well)"
    }
    
    

    def clean_email(self):  
        email = self.cleaned_data.get('email')  
        qs = User.objects.filter(email=email)  
        if qs.exists():  
            raise forms.ValidationError("Email is taken")  
        return email  
  
    def clean(self):  
        '''  
        Verify both passwords match.  
        '''  
        cleaned_data = super().clean()  
        password1 = cleaned_data.get("password1")  
        password2 = cleaned_data.get("password2")  
          
        if password1 is not None and password1 != password2:  
            self.add_error("password2", "Your passwords must match")  
        return cleaned_data  
  
    def save(self, commit=True):  
        # Save the provided password in hashed format  
        user = super().save(commit=False)  
        user.set_password(self.cleaned_data["password1"])  
        if commit:  
            user.save()  
        return user          
      
  
class CustomUserChangeForm(UserChangeForm):  
    class Meta:  
        model = Account  
        fields = ('email', 'phone_number','username', )  
  
    def clean_password(self):  
        # Regardless of what the user provides, return the initial value.  
        # This is done here, rather than on the field, because the  
        # field does not have access to the initial value  
        return self.initial["password"]  



class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['title','eventcode','description','eventtype','image','theme',
        'rsvp_option','scheduling_option','gallery_option','wishes_option',
        'eventstartdate','eventenddate','event_start_time',
        'information_on_schedule',
        'location','information_on_venue','event_venue_iframe','event_venue_photo',
        'contactperson','contactpersonphone',
        'invitation_image','invitation_email_subject','invitation_email_content','invitation_whatsapp_content',
        'mark_event_as_completed']

        labels = {
            "title": "Event Title",
            "eventcode": "Event Code (A unique alphanumeric code to recognize your event)",
            "description" : "Event Description",
            "eventtype" : "Event Type",
            "eventstartdate" : "Event Start date",
            "eventenddate" : "Event End date (Multi-day event)",
            "information_on_schedule" : "Short Description on items accross schedule for guests",
            "invitation_image" : "Image file for Invitation Card" ,
            "location" : "Venue Name",
            "information_on_venue" : "Venue Short Description for guests",
            "invitation_whatsapp_content" : "Message Content for WhatsApp invite",
            "contactperson" : "Event Owner/Contact person",
            "contactpersonphone" : "Event Owner/Contact person phone number",
            "theme" : "Select a website colour theme",
        }

        widgets = {
            'eventenddate': DatePickerInput(),
            'eventstartdate': DatePickerInput(),
            'event_start_time' : TimePickerInput(),
            'title' : forms.TextInput(attrs = {'class':'form-control'}),
            'eventcode' : forms.TextInput(attrs = {'class':'form-control'}),
            'description' : forms.Textarea(attrs = {'class':'form-control'}),
            'eventtype' : forms.TextInput(attrs = {'class':'form-control'}),
            'information_on_schedule' : forms.Textarea(attrs = {'class':'form-control','placeholder':'(Optional Field)'}),
            'location' : forms.TextInput(attrs = {'class':'form-control'}),
            'contactperson' : forms.TextInput(attrs = {'class':'form-control'}),
            'contactpersonphone' : forms.TextInput(attrs = {'class':'form-control'}),
            'invitation_email_subject' : forms.TextInput(attrs = {'class':'form-control'}),
            'invitation_email_content' : forms.Textarea(attrs = {'class':'form-control'}),
            'invitation_whatsapp_content' : forms.Textarea(attrs = {'class':'form-control'}),
            'invitation_image' : forms.ClearableFileInput(attrs = {'class':'form-control'}),
            'information_on_venue' : forms.Textarea(attrs = {'class':'form-control'}),
            'event_venue_iframe' : forms.Textarea(attrs = {'class':'form-control','placeholder':'Copy HTML iframe code directly onto here. You can choose to upload an image instead of the Google Map Iframe code'}),
            'theme' : forms.Select(attrs = {'class':'form-control'}),
            'image': forms.ClearableFileInput(attrs = {'class':'form-control'}),
            'event_venue_photo': forms.ClearableFileInput(attrs = {'class':'form-control'}),
        }
    def clean(self):
        cleaned_data = super(EventForm, self).clean() 
        event_venue_iframe = cleaned_data.get("event_venue_iframe")
        event_venue_photo = cleaned_data.get("event_venue_photo"),
        if event_venue_iframe is None and event_venue_photo is None:
            raise ValidationError('Please enter either Venue Iframe or a Venue Photograph')
        return cleaned_data


class ScheduleItemForm(ModelForm):
    class Meta:
        model = Schedule
        fields = ['item_name','item_start_time','item_end_time',
        'item_optional_detail','item_icon_image']

        widgets = {
            'item_start_time': TimePickerInput(),
            'item_end_time' : TimePickerInput()
        }

    def __init__(self, *args, **kwargs):
        super(ScheduleItemForm, self).__init__(*args, **kwargs)
        self.fields['item_end_time'].required = False
        self.fields['item_optional_detail'].required = False
        self.fields['item_icon_image'].required = False


class InviteeForm(ModelForm):
    class Meta:
        model = Invitee
        fields = ['invitee_name','invitee_email','invitee_phone','invitee_guest_count']

    def __init__(self, *args, **kwargs):
        super(InviteeForm, self).__init__(*args, **kwargs)
        self.fields['invitee_email'].required = False
        self.fields['invitee_phone'].required = False


class EventPhotoForm(ModelForm):
    class Meta:
        model = EventPhoto
        fields = ['photo_name','photo']

class EventPhotoFormforOwner(ModelForm):
    class Meta:
        model = EventPhoto
        fields = ['photo_name','photo_album','photo_approved','photo_name_display','photo_carousel_picture']
        def __init__(self, *args, **kwargs):
            super(EventPhotoFormforOwner, self).__init__(*args, **kwargs)
            self.fields['photo_name'].required = False
            self.fields['photo_album'].required = False
            self.fields['photo_approved'].required = False
            self.fields['photo_name_display'].required = False
            self.fields['photo_carousel_picture'].required = False
            #print(EventPhotoAlbum.objects.filter(album_eventcode=self.instance.photo_eventcode))
            self.fields['photo_album'].queryset = EventPhotoAlbum.objects.filter(album_eventcode=self.instance.photo_eventcode)




"""
class CreateUserForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs = {'class':'form-control'}))
    class Meta:
        model = User
        fields = ["username", "email","password1","password2"]
    
    def __init__(self, *args, **kwargs):
        super(CreateUserForm,self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
"""