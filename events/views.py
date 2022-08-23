from django.shortcuts import render,redirect
from django.conf import settings
User = settings.AUTH_USER_MODEL
from .models import Event, Invitee, EventDate, Schedule,EventPhoto, EventPhotoAlbum,Wish
from accounts.models import Account, Friend
from invites.models import Invitation
from django.conf import settings
from django.db.models import Count,Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import datetime



def friendship_calculator(invitation_from,friend):

    friends = Friend.objects.filter(user = invitation_from, friend = friend)
    if len(friends) == 0:
        Friend.objects.create(user = invitation_from, friend = friend, friendship_strength = 1)
    else:
        friend_relation = friends[0]
        friend_relation.friendship_strength = friend_relation.friendship_strength + 1
        friend_relation.save()



@login_required
def eventhomepage(request,eventcode_key):
    event = Event.objects.filter(eventcode = eventcode_key)[0]
    schedule_option = event.scheduling_option
    gallery_option = event.gallery_option
    wishes_option = event.wishes_option
    ## THEME COLOUR ##
    theme = event.theme
    theme = " /static/events/assets/css/theme-color/"+theme
    viewing_my_website = False
    if event.information_on_venue:
        information_on_venue = event.information_on_venue
    else:
        information_on_venue = False

    if schedule_option:
        ## SCHEDULE STUFF ##
        information_on_schedule = event.information_on_schedule
        schedule_dict = {}
        eventdates = EventDate.objects.filter(day_eventcode = event)
    
        event_first_day_date = eventdates[0].day_date.strftime('%d-%b, %y')
        event_first_day_day_name = eventdates[0].day_dayname
        event_first_day_items = Schedule.objects.filter(item_eventcode = event,item_date = eventdates[0])
        for eventdate in eventdates[1:]:
            schedule_dict[eventdate.day_date.strftime('%d-%b, %y')] = [eventdate.day_dayname,Schedule.objects.filter(item_eventcode = event,item_date = eventdate)]
    else:
        information_on_schedule = event_first_day_date = event_first_day_day_name = event_first_day_items = schedule_dict = False

    
    ## RSVP ##
    if request.user.is_authenticated == False:
        visitor = False 
        rsvp_option = False
        rsvp_status = False
    else:
        if request.user == event.user:
            visitor = True 
            rsvp_option = False
            rsvp_status = False
            viewing_my_website = True
        else:
            has_invite = Invitation.objects.filter(user = request.user, eventcode = event)
            if len(has_invite) == 0:
                visitor = True 
                rsvp_option = False
                rsvp_status = False
            else:
                invite = has_invite[0]
                if invite.rsvp_done:
                    if invite.rsvp_reject:
                        text = "No I will not be attending"  
                    else:
                        if invite.guest_count >= 2:
                            text = f"Yes I will be attending with {invite.guest_count} guests"
                        else:
                            text ="Yes I will be attending"
                    rsvp_status = f"You have RSVP'd: {text}"
                else:
                    rsvp_status = "You have not RSVP'd yet"
                visitor = True
                rsvp_option = True

    ######### WISHES STUFF ######################
    all_wishes = Wish.objects.filter(wish_eventcode = event, wish_approved = True)
    

    return render(request,'events/home.html',{
        'schedule_option':schedule_option,
        'gallery_option':gallery_option,
        'wishes_option':wishes_option,
        'information_on_schedule':information_on_schedule,
        'information_on_venue':information_on_venue,
        'event_first_day_date':event_first_day_date,
        'event_first_day_day_name':event_first_day_day_name,
        'event_first_day_items':event_first_day_items,
        'schedule_dict':schedule_dict,
        'viewing_my_website':viewing_my_website,
        'event':event,
        'rsvp_status':rsvp_status,
        'visitor':visitor,
        'rsvp_option':rsvp_option,
        'all_wishes':all_wishes,
        'theme':theme})

@login_required
def rsvp(request,eventcode_key):
    #currently handles only registered and logged in users
    if request.method == 'POST':
        event = Event.objects.filter(eventcode = eventcode_key)[0]
        if request.user.is_authenticated:
            has_invite = Invitation.objects.filter(user = request.user, eventcode = event)
            if len(has_invite) == 0:
                if request.POST['rsvp_code'] == event.rsvp_code:
                    Invitation.objects.create(
                        user = request.user,
                        eventcode = event,
                        invitation_from = event.user,
                        guest_count =  request.POST['rsvp_guest_count'],
                        remarks = request.POST['remarks'],
                        rsvp_done = True,
                        rsvp_reject = False
                        )
                    friendship_calculator(event.user,request.user)
                    messages.info(request, 'Hey, glad you can make it. See you there!')
                else:
                    messages.info(request, 'Sorry, that is not the right RSVP code for this event' )

            else:
                invite = Invitation.objects.filter(user = request.user, eventcode = event)[0]
                if request.POST['rsvp_answer'] == 'No':
                    messages.info(request, 'Sorry that you can\'t make it' )
                    invite.rsvp_reject = True
                else:
                    invite.rsvp_reject = False
                    messages.info(request, 'Hey, glad you can make it. See you there!')
                invite.rsvp_done = True
                invite.guest_count = request.POST['rsvp_guest_count']
                if request.POST['remarks']:
                    invite.remarks = request.POST['remarks']
                invite.save()
        
        return redirect('events:eventhomepage',eventcode_key = event)

@login_required
def gallery(request,eventcode_key):
    event = Event.objects.filter(eventcode = eventcode_key)[0]
    invite = Invitation.objects.filter(user = request.user, eventcode = event)
    if len(invite) == 0 and event.user != request.user:
        return render(request,'events/not_invited.html') 
    if not event.gallery_option:
        return render(request,'events/not_invited.html') 
    
    if request.method == 'GET':
        all_albums = EventPhotoAlbum.objects.filter(album_eventcode = event).annotate(number_of_photos=Count('eventphoto'))
        all_albums_by_owner = all_albums.filter(album_owner = event.user, album_approved = True)
        all_albums_others = all_albums.filter(~Q(album_owner = event.user), album_approved = True)
        photos_by_owner = EventPhoto.objects.filter(photo_eventcode = event, photo_poster = event.user, photo_approved = True, photo_album__isnull=True)
        photos_by_others = EventPhoto.objects.filter(~Q(photo_poster = event.user), photo_eventcode = event, photo_approved = True, photo_album__isnull=True)

        albums_posted_count = len(all_albums_by_owner) + len(all_albums_others)
        photos_posted_count = len(EventPhoto.objects.filter(photo_eventcode = event,photo_approved = True))
        invitees_total_attended = sum([i.guest_count for i in Invitation.objects.filter(eventcode = event,invitation_from = event.user,rsvp_reject = False)])
        wishes_count = len(Wish.objects.filter(wish_eventcode = event,wish_approved = True))
        carousel_pictures = EventPhoto.objects.filter(photo_eventcode = event, photo_carousel_picture = True)
        album_upload_form_image = list(carousel_pictures)[0]
        photo_upload_form_image = list(carousel_pictures)[-1]
        return render(
            request,'events/gallery_home.html',
            {'event':event,
            'carousel_pictures':carousel_pictures,
            'albums_posted_count':albums_posted_count,
            'photos_posted_count':photos_posted_count,
            'invitees_total_attended':invitees_total_attended,
            'wishes_count':wishes_count,
            'all_albums_by_owner':all_albums_by_owner,
            'all_albums_others':all_albums_others,
            'photos_by_owner':photos_by_owner,
            'photos_by_others':photos_by_others,
            'album_upload_form_image':album_upload_form_image,
            'photo_upload_form_image':photo_upload_form_image
            })

    else:
        if 'guest_album_upload' in request.POST:
            images = request.FILES.getlist('images')
            album_thumbnail = request.FILES.getlist('album_thumbnail')[0]
            album_name = request.POST['album_name']
            new_album = EventPhotoAlbum.objects.create(album_name = album_name, album_eventcode = event, album_owner = request.user, album_approved = False, album_thumbnail = album_thumbnail)
            length = EventPhoto.objects.filter().count()

            for img in images:
                length += 1
                EventPhoto.objects.create(
                    photo_name = f"{album_name}_{length}",
                    photo_poster = request.user,
                    photo_album = new_album,
                    photo_eventcode = event,
                    photo = img,
                    photo_approved = False
                    )
            messages.info(request, 'Your file(s) has been uploaded succesfully! Please do upload more if you have any')
            return redirect('events:gallery',eventcode_key = event) 

        elif 'guest_photo_upload' in request.POST:
            photo = request.FILES.getlist('photo_image')[0]
            photo_name = request.POST['photo_title']

            EventPhoto.objects.create(
                    photo_name = photo_name,
                    photo_poster = request.user,
                    photo_eventcode = event,
                    photo = photo,
                    photo_approved = False,
                    photo_name_display = True
                    )
            messages.info(request, 'Your file(s) has been uploaded succesfully! Please do upload more if you have any')
            return redirect('events:gallery',eventcode_key = event)
@login_required    
def home_temp(request):
    return render(request,'events/temp.html')

@login_required
def album_view(request,eventcode_key,album_id):
    event = Event.objects.filter(eventcode = eventcode_key)[0]
    if request.method == 'GET':
        album = EventPhotoAlbum.objects.get(id = album_id)
        album_pictures = EventPhoto.objects.filter(photo_album = album, photo_approved = True)
        return render(request,'events/view_album.html',{'event':event,'album':album,'album_pictures':album_pictures})
 


def wish_post(request,eventcode_key):
    if request.method == 'POST':
        event = Event.objects.filter(eventcode = eventcode_key)[0]
        wish_poster = request.user
        wish_eventcode = event
        wish_message = request.POST['message']
        wish_byline = request.POST['name']
        if request.FILES:
            wish_photo = request.FILES.getlist('wish_image')[0]
            Wish.objects.create(wish_poster = wish_poster,wish_eventcode = wish_eventcode, wish_message = wish_message,wish_byline = wish_byline, wish_photo = wish_photo)
        else:
            Wish.objects.create(wish_poster = wish_poster,wish_eventcode = wish_eventcode, wish_message = wish_message,wish_byline = wish_byline)
        messages.info(request, f'Your wish has been shared with {event.contactperson} successfullly.')
        return redirect('events:eventhomepage',eventcode_key = event)

