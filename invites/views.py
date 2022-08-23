from email import message
from turtle import update
from django.db import IntegrityError
from django.dispatch import receiver
from django.shortcuts import render,redirect, get_object_or_404, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.db import IntegrityError 
from django.contrib.auth import login,logout,authenticate
from django.utils import timezone
from pandas import date_range
from .forms import EventForm, InviteeForm,ScheduleItemForm,EventPhotoForm,EventPhotoFormforOwner,CustomUserCreationForm
from events.models import Event, Invitee, Schedule, EventDate,EventPhoto, EventPhotoAlbum,Wish
from accounts.models import Account, Friend
from .models import Invitation
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail,send_mass_mail
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.db.models import Count,Q
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
import random
import string
import datetime
import json
import base64
import requests
from webbing_compnay.settings import ALLOWED_HOSTS
#import cStringIO


account_sid = "AC94e3f73951443d046eea5ff492c410fe"
auth_token = "98502679f395253fcaab98186531be2b"
client = Client(account_sid, auth_token)
User = settings.AUTH_USER_MODEL


def friendship_calculator(invitation_from,friend):

    friends = Friend.objects.filter(user = invitation_from, friend = friend)
    if len(friends) == 0:
        Friend.objects.create(user = invitation_from, friend = friend, friendship_strength = 1)
    else:
        friend_relation = friends[0]
        friend_relation.friendship_strength = friend_relation.friendship_strength + 1
        friend_relation.save()


def rsvp_code_generator(length = 7):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(length))


# Function to update Invitations Database from Invitee Database
def check_existing_invites(request):
    #print(request.user.email)
    invitations = Invitee.objects.filter(invitee_email = request.user.email)
    for invite in invitations:
        if invite.invitee.email != request.user.email:
            invite.invitee = request.user
            invite.save()
        eventcode = invite.eventcode
        invitation_from = Event.objects.filter(eventcode = eventcode)[0].user
        if len( Invitation.objects.filter(user = request.user,eventcode = invite.eventcode, invitation_from = invitation_from )) == 0:
            Invitation.objects.create(user = request.user,eventcode = invite.eventcode, invitation_from = invitation_from, guest_count = invite.invitee_guest_count )
            friendship_calculator(invitation_from,request.user)

    
    
    invitations = Invitee.objects.filter(invitee_phone = request.user.phone_number)
    for invite in invitations:
        if invite.invitee.phone_number != request.user.phone_number:
            invite.invitee = request.user
            invite.save()
        eventcode = invite.eventcode
        invitation_from = Event.objects.filter(eventcode = eventcode)[0].user
        if len( Invitation.objects.filter(user = request.user,eventcode = invite.eventcode, invitation_from = invitation_from )) == 0:
            Invitation.objects.create(user = request.user,eventcode = invite.eventcode, invitation_from = invitation_from, guest_count = invite.invitee_guest_count )
            friendship_calculator(invitation_from,request.user)
# can remove this
def check_existing_invites2(request):
    invitations = Invitation.objects.filter(email_for_invitation_without_registering = request.user.email)
    for invite in invitations:
        invite.user = request.user
        invite.email_for_invitation_without_registering = None
        invite.name_for_invitation_without_registering = None
        invite.phone_for_invitation_without_registering = None
        invite.save()
    
def signupuser(request):
    if request.method == 'GET':
        return render(request,'invites/signupuser.html',{'form':CustomUserCreationForm()})
    else:
        form = CustomUserCreationForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
                login(request,user)
                return redirect('allactions')
            else:
                return render(request,'invites/signupuser.html',{'form':CustomUserCreationForm(),'error': form})
        except IntegrityError:
            return render(request,'invites/signupuser.html',{'form':CustomUserCreationForm(),'error':'That username is taken'})

        except Exception as e:
            return render(request,'invites/signupuser.html',{'form':CustomUserCreationForm(),'error':e})

def loginuser(request):
    if request.method == 'GET':
        return render(request,'invites/loginuser.html',{'form':AuthenticationForm()})
    else:
        user = authenticate(request,username = request.POST['username'],password = request.POST['password'])
        if user is None:
            return render(request,'invites/loginuser.html',{'form':AuthenticationForm(),'error':'Username and Password do not match'})
        else:
            login(request,user)
            return redirect('allactions')
        
@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')


@login_required
def home(request):
    return render(request,'invites/home.html')
@login_required
def allactions(request):
    check_existing_invites(request)
    #check_existing_invites2(request)
    events = Event.objects.filter(user = request.user, mark_event_as_completed=False)
    completed_events = Event.objects.filter(user = request.user, mark_event_as_completed=True).order_by('-eventstartdate')
    invitations = Invitation.objects.filter(user = request.user)
    
    
    return render(request,'invites/allactions.html',{'events':events,'completed_events':completed_events,'my_invitations':invitations})
@login_required
def createevent(request):
    if request.method == 'GET':
        return render(request,'invites/createevent.html',{'form':EventForm()})
    else:
        try:
            form = EventForm(request.POST,request.FILES)
            new_event = form.save(commit=False)
            new_event.user = request.user
            new_event.rsvp_code = rsvp_code_generator()
            new_event.save()
            if new_event.scheduling_option:
                return redirect('eventscheduler',eventcode_key = new_event.eventcode)
            else:
                return redirect('allactions')
        except ValueError:
            return render(request,'invites/createevent.html',{'form':EventForm(),'error':'Invalid Data'})

@login_required
def viewevent(request,eventcode_key):
    event = Event.objects.filter(user = request.user, eventcode = eventcode_key)[0]
    if request.method == 'GET':
        form = EventForm(instance = event)
        return render(request,'invites/viewevent.html',{'event':event,'form':form})
    else:
        try:
            form = EventForm(request.POST,request.FILES,instance = event)
            form.save()
            eventdates = EventDate.objects.filter(day_eventcode = event)
            if len(eventdates) == 0 and event.scheduling_option:
                print(eventdates)
                return redirect('eventscheduler',eventcode_key = eventcode_key)
           
            return redirect('viewevent',eventcode_key = eventcode_key)
        except Exception as e:
            return render(request,'invites/createevent.html',{'form':EventForm(),'error':e})
@login_required
def completeevent(request,eventcode_key):
    event = Event.objects.filter(user = request.user, eventcode = eventcode_key)[0]
    if request.method == 'POST':
        event.mark_event_as_completed = True
        event.save()
        return redirect('allactions')
@login_required
def deleteevent(request,eventcode_key):
    event = Event.objects.filter(user = request.user, eventcode = eventcode_key)[0]
    if request.method == 'POST':
        event.delete()
        return redirect('allactions')


######################## Invites ##########################

def addfriendinvites(request,eventcode_key):

    if 'Add_Friend' in request.POST:

        event = Event.objects.get(user = request.user, eventcode = eventcode_key)
        friend_user_id = request.POST["friend"]
        friend = Account.objects.get(id = friend_user_id)
        friend_guest_count = request.POST["friend_guest_count"]
        Invitee.objects.create(eventcode = event, invitee = friend, invitee_name = friend.username, invitee_email = friend.email, invitee_phone = friend.phone_number,invitee_guest_count = friend_guest_count)

    return redirect('sendinvites',eventcode_key = eventcode_key)

@login_required
def sendinvites(request,eventcode_key):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)

    current_invitees = Invitee.objects.filter(eventcode = event)
    invited_guests = current_invitees.filter(Q(invitee_email_sent = True) | Q(invitee_whatsapp_sent = True))
    invites_pending = current_invitees.filter(invitee_email_sent = False,invitee_whatsapp_sent = False)
    

    friends = Friend.objects.filter(user = request.user).order_by('-friendship_strength')
    uninvited_friends = []

    invited_friends = list(Invitation.objects.filter(eventcode = event ,invitation_from = event.user))
    invited_friends = [f.user for f in invited_friends]
    for f in friends:
        if f.friend in invited_friends:
            f.invite_sent = True
        else:
            uninvited_friends.append(f.friend)
            f.invite_sent = False
    #print(uninvited_friends)


    if request.method == 'GET':
        return render(request,'invites/sendinvites.html',{'form':InviteeForm(),'event':event,'invited_guests':invited_guests,'invites_pending':invites_pending,'uninvited_friends':uninvited_friends,'invited_friends':invited_friends})
    else:
        try:
            form = InviteeForm(request.POST)
            new_invitee = form.save(commit=False)
            new_invitee.eventcode = event
            print(new_invitee)
            receiver_e = form.cleaned_data.get('invitee_email')
            receiver_e = Account.objects.filter(email = receiver_e)

            receiver_p = form.cleaned_data.get('invitee_phone')
            receiver_p = Account.objects.filter(phone_number = receiver_p)
            
            if len(receiver_p) == 0 and len(receiver_e) == 0:
                reciever = request.user   
            else:
                if len(receiver_p) == 1:
                    reciever = receiver_p[0]
                else:
                    reciever = receiver_e[0]
                Invitation.objects.create(user = reciever ,eventcode = event ,invitation_from = event.user ,rsvp_done = False, )
                friendship_calculator(event.user,reciever)
            new_invitee.invitee = reciever
            new_invitee.save()
            return redirect('sendinvites',eventcode_key = eventcode_key)
        except ValueError as e:
            return render(request,'invites/sendinvites.html',{'form':InviteeForm(),'error':e,'event':event, 'invited_guests':invited_guests,'invites_pending':invites_pending,'uninvited_friends':uninvited_friends,'invited_friends':invited_friends})
   
def send_whatsapp_messages(phonenumber,message,name, image,website_url):
  
        print(phonenumber)

        firstStr = "data:image/jpeg;base64,"
        formatImg = image.decode('utf-8')
        fullDataImg = firstStr+formatImg

        url = "https://api.maytapi.com/api/eed76cd2-bef0-4f09-87c1-1657cbb35b68/23205/sendMessage"
        start = f"Hey {name}! \n" + message
        #payload = "{\r\n    \"to_number\": \"917550148020\",\r\n    \"type\": \"text\",\r\n    \"message\": \"Hello World!\"\r\n    \r\n\}"
        payload = {
            "to_number": f"{phonenumber}",
            "type": "media",
            "message": fullDataImg,
            "text": start
        } 
        headers = {
        'x-maytapi-key': '92bde335-a4dd-4724-9729-187e49391276',
        'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
        print(response.text.encode('utf8'))

        payload = {
            "to_number": f"{phonenumber}",
            "type": "link",
            "message": website_url,
            "text": "Here is the link to the website. Please signup and take a minute to explore the website for the Birthday. Also do share any photos you have in the Event Gallery "
        }
        response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
        print(response.text.encode('utf8'))

        payload = {
            "to_number": f"{phonenumber}",
            "type": "buttons",
            "title": "RSVP",
            "message": "Please RSVP for this invite",
            "buttons": [
                {
                "id": "!response 1",
                "text": "I will be attending"
                },
                {
                "id": "!response 2",
                "text": "Sorry, I cannot make it!"
                }
            ],
            "footer": "You may choose to RSVP on the website as well! We recommend you do so you can explore the the birthday event website",
        }
        response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
        print(response.text.encode('utf8'))

@login_required
def finalizeinvitees(request,eventcode_key):

        if 'Delete_Selected' in request.POST:
            delete_records = request.POST.getlist('finalize_invitees',[])
            delete_records = Invitee.objects.filter(id__in = delete_records,invitee_email_sent = False)
            delete_records.delete()
        else:
            event = Event.objects.get(user = request.user, eventcode = eventcode_key)
            subject = event.invitation_email_subject
            message = event.invitation_email_content
            email_from = settings.EMAIL_HOST_USER

            email_list = request.POST.getlist('finalize_invitees',[])
            email_list = Invitee.objects.filter(id__in = email_list)
    

            invited_guests = email_list.filter(invitee_email_sent = True)
            invites_pending = email_list.filter(invitee_email_sent = False,invitee_whatsapp_sent = False)
            invites_pending_email = email_list.filter(invitee_email_sent = False)
            invites_pending_phone = email_list.filter(invitee_whatsapp_sent = False)
            recipient_list = list(invites_pending_email.values_list('invitee_email', flat=True))
            whatsapp_message = event.invitation_whatsapp_content
            whatsapp_list = list(invites_pending_phone.values_list('invitee_phone', flat=True))
            whatsapp_list_names = list(invites_pending_phone.values_list('invitee_name', flat=True))
            b64_img = base64.b64encode(event.image.read())
            website_url = ALLOWED_HOSTS[0] + '/visit/' + event.eventcode
            for phonenumber in range(len(whatsapp_list)):
                send_whatsapp_messages(whatsapp_list[phonenumber],whatsapp_message,whatsapp_list_names[phonenumber],b64_img,website_url)

            whatsapp_messages_sent = True

            if whatsapp_messages_sent:
                invites_pending_phone.update(invitee_whatsapp_sent=True)
            messages = [(subject, message, email_from, [recipient]) for recipient in recipient_list]


            send_mass_mail(messages)
            invites_pending_email.update(invitee_email_sent=True)
            
        return redirect('sendinvites',eventcode_key = eventcode_key)

@login_required
def viewrsvps(request,eventcode_key):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)
    accepted_rsvpd_invitations = Invitation.objects.filter(eventcode = event, invitation_from = request.user, rsvp_done = True, rsvp_reject = False).exclude(user = request.user)
    rejected_rsvpd_invitations = Invitation.objects.filter(eventcode = event, invitation_from = request.user, rsvp_done = True, rsvp_reject = True).exclude(user = request.user)
    pending_invitations = Invitation.objects.filter(eventcode = event, invitation_from = request.user, rsvp_done = False)
    non_registered_invites = Invitee.objects.filter(invitee = event.user, eventcode = event, invitee_email_sent = True)
    print(non_registered_invites)
    if request.method == 'GET':
        return render(
            request,
            'invites/viewrsvps.html',
            {
                'event':event,
                'accepted_rsvpd_invitations':accepted_rsvpd_invitations,
                'rejected_rsvpd_invitations':rejected_rsvpd_invitations,
                'pending_invitations':pending_invitations,
                'non_registered_invites':non_registered_invites
                }
            )



#### INVITES ##########
@login_required
def joinevent(request):
    if request.method == 'POST':
        rsvp_code = request.POST['rsvp_code']
        event =  Event.objects.filter(rsvp_code = rsvp_code)
        if len(event) == 1:
            event = event[0]
            #print(type(event.eventcode))
            #print(type(event.user))
            if len(Invitation.objects.filter(user = request.user,eventcode = event, invitation_from = event.user )) == 0:
                Invitation.objects.create(user = request.user,eventcode = event, invitation_from = event.user )
                friendship_calculator(event.user,request.user)
            return redirect('allactions')
        else:
            print('there')
            messages.info(request, 'Sorry, could not find an event with that event code.')
            return redirect('allactions')

#### Event Scheduler ##########
@login_required
def get_event_date_range(event):
    date_range = False
    selected_dates = [event.eventenddate.strftime("%Y-%m-%d")]

    if event.eventstartdate != event.eventenddate:
        date_range = [event.eventstartdate+datetime.timedelta(days=x) for x in range((event.eventenddate-event.eventstartdate).days)]  
        date_range.append(event.eventenddate)
        date_range = [t.strftime("%Y-%m-%d") for t in date_range]
    print(selected_dates)
    return selected_dates, date_range

@login_required
def changeeventdates(request,eventcode_key):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)
    eventdates = EventDate.objects.filter(day_eventcode = event)
    if request.method == 'POST':
        eventdates.delete()
    return redirect('eventscheduler',eventcode_key = event)

@login_required
def changescheduleitems(request,eventcode_key):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)
    if request.method == 'POST':
        if 'Delete_Selected' in request.POST:
            delete_records = request.POST.getlist('delete_schedule_items',[])
            delete_records = Schedule.objects.filter(id__in = delete_records)
            delete_records.delete()
    return redirect('eventscheduler',eventcode_key = event)

@login_required
def eventscheduler(request,eventcode_key):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)
    eventdates = EventDate.objects.filter(day_eventcode = event)
    if len(eventdates) == 0:
        if event.eventstartdate == event.eventenddate:
            selected_dates = [event.eventstartdate.strftime("%Y-%m-%d")]
            date_range = [event.eventstartdate.strftime("%Y-%m-%d")]
        else:
            selected_dates, date_range = get_event_date_range(event)
            print(selected_dates)
        if request.method == 'GET' and len(date_range) > 1:
            return render(request,'invites/eventscheduler.html',{'event':event,'date_range':date_range})
        elif request.method == 'GET' and len(date_range) == 1:
            return render(request,'invites/eventscheduler.html',{'event':event,'selected_dates':selected_dates})
        else: 
            if 'selected_date' in request.POST:
                selected_dates = list(request.POST.getlist('selected_date',[]))
                print(f'dates selected {selected_dates}')
                request.session['selected_dates'] = selected_dates
                return render(request,'invites/eventscheduler.html',{'event':event,'selected_dates':selected_dates})

            elif 'selected_dates' in request.session and set(request.session['selected_dates']).issubset(set(list(request.POST.keys()))):
                #print(request.POST)
                for date in request.POST:
                    if date == 'csrfmiddlewaretoken':
                        continue
                    #print(date)
                    EventDate.objects.create(day_eventcode = event,day_date = date,day_dayname = request.POST[date])
                return redirect('eventscheduler',eventcode_key = eventcode_key)
            else:
                print('failed')
                print(set(selected_dates))
                print(set(list(request.POST.keys())))
                print(dict(request.POST))
                temp_dict = dict(request.POST)
                del temp_dict['csrfmiddlewaretoken']
                date = list(temp_dict.keys())[0]
                name = list(temp_dict.values())[0][0]
                EventDate.objects.create(day_eventcode = event,day_date = date,day_dayname = name)
                return redirect('eventscheduler',eventcode_key = eventcode_key)
    else:
        existing_schedlues = Schedule.objects.filter(item_eventcode = event)
        if request.method == 'GET':
            form_map = {}
            for eventdate in eventdates:
                schedule_for_the_day = existing_schedlues.filter(item_date = eventdate)
                form_map.update({eventdate.day_date:[eventdate.day_dayname,ScheduleItemForm(),schedule_for_the_day]})
            return render(request,'invites/eventscheduler.html',{'event':event,'form_map':form_map})
        else:
            try:
                form = ScheduleItemForm(request.POST,request.FILES)
                new_item = form.save(commit=False)
                new_item.item_eventcode = event
                new_item.item_date = EventDate.objects.filter(day_eventcode = event,day_date = request.POST["date"])[0]
                new_item.save()
                return redirect('eventscheduler',eventcode_key = event)
            except ValueError as e:
                print('fail')
                print(e)
                return render(request,'invites/eventscheduler.html',{'event':event})

 #### Gallery ##########
@login_required
def alter_approval_status(request,eventcode_key):
    if request.method == 'GET':
        return render(request,'invites/temp.html')
    id = request.POST['id'].split('_')
    if id[0] == 'album':
        w = EventPhotoAlbum.objects.get(id=int(id[1]))
        
        w.album_approved = request.POST['isapproved'] == 'true'
        w.save()
    elif id[0] == 'wish':
        w = Wish.objects.get(id=int(id[1]))
        
        w.wish_approved = request.POST['isapproved'] == 'true'
        w.save()
    else:
        w = EventPhoto.objects.get(id=int(id[1]))
        w.photo_approved = request.POST['isapproved'] == 'true'
        w.save()
    return redirect('gallery',eventcode_key = eventcode_key)

@login_required
def gallery(request,eventcode_key):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)
    all_albums = EventPhotoAlbum.objects.filter(album_eventcode = event).annotate(number_of_photos=Count('eventphoto'))
    all_albums_by_me = all_albums.filter(album_owner = request.user)
    all_albums_other = all_albums.filter(~Q(album_owner = request.user))
    photos_by_me = EventPhoto.objects.filter(photo_eventcode = event, photo_poster = request.user,photo_album__isnull=True)
    photos_by_others = EventPhoto.objects.filter(~Q(photo_poster = request.user),photo_eventcode = event, photo_album__isnull=True)
    if request.method == 'GET':
        return render(request,'invites/gallery.html',{'event':event,'all_albums_by_me':all_albums_by_me,'all_albums_other':all_albums_other,'photos_by_me':photos_by_me,'photos_by_others':photos_by_others})
@login_required
def upload_pictures(request,eventcode_key):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)
    if request.method == 'GET':
        form = EventPhotoForm()
        return render(request,'invites/upload_pictures.html',{'event':event,'form':form})
    else:
        if 'Multiphotoupload' in request.POST:
            print('here')
            single_photos = request.FILES.getlist('images')
            length = EventPhoto.objects.filter().count()
            for img in single_photos:
                length += 1
                EventPhoto.objects.create(
                    photo_name = f"{event.eventcode}_{length}",
                    photo_poster = request.user,
                    photo_eventcode = event,
                    photo = img,
                    photo_approved = True
                    )
            return redirect('upload_pictures',eventcode_key = eventcode_key)
        else:
                
            try:
                form = EventPhotoForm(request.POST,request.FILES)
                new_photo = form.save(commit=False)
                new_photo.photo_poster = request.user
                #new_photo.photo_album = None
                new_photo.photo_eventcode = event
                new_photo.photo_approved = True
                new_photo.photo_name_display = True
                new_photo.save()
                return redirect('upload_pictures',eventcode_key = eventcode_key)
            except ValueError as e:
                print(e)
                return render(request,'invites/upload_pictures.html',{'event':event,'form':EventPhotoForm(),'error':'Invalid Data'})
@login_required
def upload_album(request,eventcode_key):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)
    all_albums = EventPhotoAlbum.objects.filter(album_eventcode = event).annotate(number_of_photos=Count('eventphoto'))
    all_albums = all_albums.filter(album_owner = request.user)

    if request.method == 'GET':
        return render(request,'invites/upload_album.html',{'event':event,'all_albums':all_albums})
    else:
        try:
            images = request.FILES.getlist('images')
            album_thumbnail = request.FILES.getlist('album_thumbnail')[0]
            album_name = request.POST['album_name']
            new_album = EventPhotoAlbum.objects.create(album_name = album_name, album_eventcode = event, album_owner = request.user, album_approved = True, album_thumbnail = album_thumbnail)
            length = EventPhoto.objects.filter().count()
            for img in images:
                length += 1
                EventPhoto.objects.create(
                    photo_name = f"album_name_{length}",
                    photo_poster = request.user,
                    photo_album = new_album,
                    photo_eventcode = event,
                    photo = img,
                    photo_approved = True
                    )

            return redirect('gallery',eventcode_key = eventcode_key)
        except ValueError as e:
            print(e)
            return render(request,'invites/upload_album.html',{'event':event,'error':'Invalid Data','all_albums':all_albums})
@login_required
def view_album(request,eventcode_key, album_id):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)
    album = EventPhotoAlbum.objects.get(id = album_id)
    if request.method == 'GET':
        album_pictures = EventPhoto.objects.filter(photo_album = album).order_by('-photo_approved') 
        if album.album_owner == request.user:
            edit_permission = True
        else:
            edit_permission = False
        return render(request,'invites/view_album.html',{'event':event,'album':album,'album_pictures':album_pictures,'edit_permission':edit_permission})
    else:
        if "change_album_name" in request.POST:
            album.album_name = request.POST['album_name']
            print(album.album_name)
            album.save()
            return redirect('view_album',eventcode_key = eventcode_key,album_id = album_id)

        elif "change_album_thumbnail" in request.POST:
            print('2323')
            album_thumbnail = request.FILES.getlist('album_thumbnail')[0]
            album.album_thumbnail = album_thumbnail
            album.save()
            return redirect('view_album',eventcode_key = eventcode_key,album_id = album_id)

        elif "change_approval_status" in request.POST:
            album_pictures = EventPhoto.objects.filter(photo_album = album)
            if request.POST['approval_status'] == 'No':
                album.album_approved = False
                for pic in album_pictures:
                    pic.photo_approved = False
                    pic.save()
            else:
                album.album_approved = True
                for pic in album_pictures:
                    pic.photo_approved = True
                    pic.save()
            album.save()
            return redirect('view_album',eventcode_key = eventcode_key,album_id = album_id)
            
        else:
            album_pictures = EventPhoto.objects.filter(photo_album = album).order_by('-photo_approved') 
            try:
                images = request.FILES.getlist('images')
                length = EventPhoto.objects.filter().count()
                for img in images:
                    length += 1
                    EventPhoto.objects.create(
                        photo_name = f"album_name_{length}",
                        photo_poster = request.user,
                        photo_album = album,
                        photo_eventcode = event,
                        photo = img,
                        photo_approved = True
                        )
                return redirect('view_album',eventcode_key = eventcode_key,album_id = album_id)
            except ValueError as e:
                print(e)
                return render(request,'invites/view_album.html',{'event':event,'album':album,'error':'Invalid Data','album_pictures':album_pictures}) 
@login_required
def update_album_content(request,eventcode_key, album_id):
    
    album = EventPhotoAlbum.objects.get(id = album_id)
    album_pictures = EventPhoto.objects.filter(photo_album = album)

    if request.method == 'POST':
        if 'approve_photos' in request.POST:
            approved_photos = request.POST.getlist('approved_pictures',[])
            for pic in album_pictures:
                if str(pic.id) not in approved_photos:
                    pic.photo_approved = False
                    pic.save()
                else:
                    pic.photo_approved = True
                    pic.save()

        elif 'delete_photos' in request.POST:
            delete_pictures = request.POST.getlist('delete_pictures',[])
            for pic in album_pictures:
                if str(pic.id) in delete_pictures:
                    pic.delete()
        return redirect('view_album',eventcode_key = eventcode_key,album_id = album_id)      

@login_required
def view_image(request,eventcode_key, photo_id):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)
    photo = EventPhoto.objects.get(id = photo_id)
    album =  photo.photo_album

    if request.method == 'GET':
        form = EventPhotoFormforOwner(instance = photo)
        return render(request,'invites/view_image.html',{'event':event,'form':form,'photo':photo,'album':album})
    
    else:
        try:
            form = EventPhotoFormforOwner(request.POST,instance = photo)
            form.save()
            return redirect('view_image',eventcode_key = eventcode_key,photo_id=photo_id)
        except ValueError:
            return render(request,'invites/view_image.html',{'form':EventPhotoFormforOwner(),'error':'Invalid Data'})
@login_required
def delete_uploaded_images(request,eventcode_key):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)
    if request.method == 'POST':
        if 'delete_individual_photos_by_me_option' in request.POST:
            individual_photos_by_me = EventPhoto.objects.filter(photo_album__isnull = True,photo_poster = request.user,photo_eventcode = event)
            delete_individual_photos_by_me = request.POST.getlist('delete_individual_photos_by_me',[])
            for pic in individual_photos_by_me:
                if str(pic.id) in delete_individual_photos_by_me:
                    pic.delete()
        
        elif 'delete_individual_photos_by_others_option' in request.POST:
            individual_photos_by_others = EventPhoto.objects.filter( ~Q(photo_poster = request.user),photo_album__isnull = True,photo_eventcode = event)
            delete_individual_photos_by_others = request.POST.getlist('delete_individual_photos_by_others',[])
            print('here323')
            for pic in individual_photos_by_others:
                if str(pic.id) in delete_individual_photos_by_others:
                    pic.delete()

    
    return redirect('gallery',eventcode_key = eventcode_key)

############# Wishes ##########################
def wishcenter(request,eventcode_key):
    event = Event.objects.get(user = request.user, eventcode = eventcode_key)
    all_wishes = Wish.objects.filter(wish_eventcode = event)

    if request.method == 'GET':
        return render(request,'invites/wish_center.html',{'event':event,'all_wishes':all_wishes})








########## TWILIO #################

@csrf_exempt
#@ensure_csrf_cookie
#method_decorator(csrf_protect)
def whatsapp(request):
    if request.method == "POST":
        json_data = request.get_json()
        print(json_data)
        #print(json_data)
        wttype = json_data["type"]
        if wttype == "message":
            message = json_data["message"]
            conversation = json_data["conversation"]
            _type = message["type"]

            payload = {
                    "to_number": conversation,
                    "type": "text",
                    "message": "Gotcha"
            }
            headers = {
            'x-maytapi-key': '92bde335-a4dd-4724-9729-187e49391276',
            'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
            print(response.text.encode('utf8'))

   