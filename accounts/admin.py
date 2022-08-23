from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import Account,Friend
from invites.forms import CustomUserCreationForm,CustomUserChangeForm


class AccountAdmin(UserAdmin):

    add_form = CustomUserCreationForm  
    form = CustomUserChangeForm  
    model = Account 

    list_display = ('email','username','date_joined','last_login','is_admin','is_staff')
    search_fields = ('email','username')
    readonly_fields = ('id','date_joined','last_login')
    filter_horizontal = ()
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (  
        (None, {'fields': ('email','username', 'password','phone_number','profile_image')}),  
        ('Permissions', {'fields': ('is_staff', 'is_active')}),  
    )  

    add_fieldsets = (  
        (None, {  
            'classes': ('wide',),  
            'fields': ('email','username', 'password1', 'password2', 'is_staff', 'is_active','profile_image','phone_number')}  
        ),  
    ) 


admin.site.register(Account,AccountAdmin)
admin.site.register(Friend)



