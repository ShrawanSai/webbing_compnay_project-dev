"""webbing_company URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from invites import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
urlpatterns = [
    path('admin/', admin.site.urls),

    #Auth
    path('signup/',views.signupuser,name='signupuser'),
    path('login/',views.loginuser,name='loginuser'),
    path('logout/',views.logoutuser,name='logoutuser'),

    #Events
    path('',views.home,name='home'),
    path('allactions/',views.allactions,name='allactions'),
    path('createevent/',views.createevent,name='createevent'),
    path('event/<str:eventcode_key>',views.viewevent,name='viewevent'),
    path('event/<str:eventcode_key>/complete',views.completeevent,name='completeevent'),
    path('event/<str:eventcode_key>/delete',views.deleteevent,name='deleteevent'),
    path('event/<str:eventcode_key>/sendinvites',views.sendinvites,name='sendinvites'),
    path('event/<str:eventcode_key>/finalizeinvitees',views.finalizeinvitees,name='finalizeinvitees'),
    path('event/<str:eventcode_key>/addfriendinvites',views.addfriendinvites,name='addfriendinvites'),
    path('event/<str:eventcode_key>/viewrsvps',views.viewrsvps,name='viewrsvps'),
    path('event/<str:eventcode_key>/eventscheduler',views.eventscheduler,name='eventscheduler'),
    path('event/<str:eventcode_key>/changeeventdates',views.changeeventdates,name='changeeventdates'),
    path('event/<str:eventcode_key>/changescheduleitems',views.changescheduleitems,name='changescheduleitems'),
    path('event/<str:eventcode_key>/gallery',views.gallery,name='gallery'),
    path('event/<str:eventcode_key>/upload_pictures',views.upload_pictures,name='upload_pictures'),
    path('event/<str:eventcode_key>/upload_album',views.upload_album,name='upload_album'),
    path('event/<str:eventcode_key>/view_album/<int:album_id>',views.view_album,name='view_album'),
    path('event/<str:eventcode_key>/update_album_content/<int:album_id>',views.update_album_content,name='update_album_content'),
    path('event/<str:eventcode_key>/alter_approval_status',views.alter_approval_status,name='alter_approval_status'),
    path('event/<str:eventcode_key>/view_image/<int:photo_id>',views.view_image,name='view_image'),
    path('event/<str:eventcode_key>/delete_uploaded_images>',views.delete_uploaded_images,name='delete_uploaded_images'),
    path('event/<str:eventcode_key>/wishcenter',views.wishcenter,name='wishcenter'),

    #### TWILIO #####
    path('whatsapp',views.whatsapp,name='whatsapp'),


 
    #Invites
    path('joinevent/',views.joinevent,name='joinevent'),

    #ModelWebsite
    path('visit/', include('events.urls', namespace='event-stuff')),

    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 

]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

