# Generated by Django 4.1 on 2022-08-12 21:00

import ckeditor.fields
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('title', models.CharField(max_length=200)),
                ('eventcode', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('description', ckeditor.fields.RichTextField(blank=True)),
                ('eventtype', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('location', models.CharField(max_length=200)),
                ('contactperson', models.CharField(max_length=200)),
                ('contactpersonphone', models.CharField(max_length=12)),
                ('mark_event_as_completed', models.BooleanField(default=False)),
                ('image', models.ImageField(blank=True, upload_to='events/images/')),
                ('invitation_email_subject', models.CharField(blank=True, max_length=200)),
                ('invitation_email_content', models.TextField(blank=True)),
                ('eventstartdate', models.DateField()),
                ('eventenddate', models.DateField()),
                ('event_start_time', models.TimeField(default=datetime.time(0, 0))),
                ('event_end_time', models.TimeField(blank=True, null=True)),
                ('information_on_schedule', models.TextField(blank=True, null=True)),
                ('event_venue_iframe', models.TextField(blank=True, null=True)),
                ('event_venue_photo', models.ImageField(blank=True, null=True, upload_to='events/images/')),
                ('eventrange', models.PositiveSmallIntegerField(default=1)),
                ('information_on_venue', models.TextField(blank=True, null=True)),
                ('rsvp_option', models.BooleanField(default=True)),
                ('scheduling_option', models.BooleanField(default=True)),
                ('gallery_option', models.BooleanField(default=True)),
                ('wishes_option', models.BooleanField(default=True)),
                ('rsvp_code', models.CharField(blank=True, max_length=7)),
                ('theme', models.CharField(choices=[('bridge-theme.css', 'Bridge Theme'), ('dark-red-theme.css', 'Dark red Theme'), ('default-theme.css', 'Default Theme'), ('green-theme.css', 'Green Theme'), ('jelly-bean-theme.css', 'Jelly Bean Theme'), ('lite-blue-theme.css', 'Light Blue Theme'), ('orange-theme.css', 'Orange Theme'), ('pink-theme.css', 'Pink Theme'), ('purple-theme.css', 'Purple Theme'), ('red-theme.css', 'Red Theme')], default='default-theme.css', max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EventDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_date', models.DateField(default=datetime.date.today)),
                ('day_dayname', models.CharField(default='Day', max_length=70)),
                ('day_eventcode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
            ],
        ),
        migrations.CreateModel(
            name='Wish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wish_message', models.TextField(blank=True)),
                ('wish_photo', models.FileField(blank=True, null=True, upload_to='events/images/')),
                ('wish_byline', models.CharField(blank=True, max_length=70, null=True)),
                ('wish_created_date', models.DateTimeField(auto_now_add=True)),
                ('wish_approved', models.BooleanField(default=False)),
                ('wish_eventcode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('wish_poster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(default='Item', max_length=70)),
                ('item_start_time', models.TimeField(default=datetime.time(0, 0))),
                ('item_end_time', models.TimeField(null=True)),
                ('item_optional_detail', models.TextField(null=True)),
                ('item_icon_image', models.ImageField(blank=True, upload_to='events/images/')),
                ('item_date', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.eventdate')),
                ('item_eventcode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
            ],
        ),
        migrations.CreateModel(
            name='Invitee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invitee_name', models.CharField(max_length=70)),
                ('invitee_email', models.EmailField(max_length=70)),
                ('invitee_phone', models.CharField(max_length=12)),
                ('invitee_email_sent', models.BooleanField(default=False)),
                ('invitee_whatsapp_sent', models.BooleanField(default=False)),
                ('invitee_rsvp', models.BooleanField(default=False)),
                ('invitee_guest_count', models.DecimalField(decimal_places=0, max_digits=1)),
                ('eventcode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('invitee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitation_for_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EventPhotoAlbum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('album_name', models.CharField(default='Album', max_length=70)),
                ('album_approved', models.BooleanField(default=False)),
                ('album_created_date', models.DateTimeField(auto_now_add=True)),
                ('album_thumbnail', models.FileField(blank=True, null=True, upload_to='events/images/')),
                ('album_eventcode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('album_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EventPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo_name', models.CharField(blank=True, max_length=70)),
                ('photo', models.FileField(upload_to='events/images/')),
                ('photo_approved', models.BooleanField(default=False)),
                ('photo_created_date', models.DateTimeField(auto_now_add=True)),
                ('photo_name_display', models.BooleanField(default=False)),
                ('photo_carousel_picture', models.BooleanField(default=False)),
                ('photo_album', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.eventphotoalbum')),
                ('photo_eventcode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.event')),
                ('photo_poster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
