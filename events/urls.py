from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.home_temp, name='home_temp'),
    path('<str:eventcode_key>/', views.eventhomepage,name='eventhomepage'),
    path('<str:eventcode_key>/rsvp', views.rsvp,name='rsvp'),
    path('<str:eventcode_key>/gallery', views.gallery,name='gallery'),
    path('<str:eventcode_key>/album_view/<int:album_id>', views.album_view,name='album_view'),
    path('<str:eventcode_key>/wish_post', views.wish_post,name='wish_post'),
    
]