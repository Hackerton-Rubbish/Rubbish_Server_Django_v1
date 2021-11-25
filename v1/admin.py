from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User
# from .models import Group as Group_


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'username')
    list_filter = ('email', 'username')
    fieldsets = (
        (None, {"fields": ('email', 'password', 'profileImgURL')}),
        ('Personal Info', {'fields': ('username', 'date_joined')}),
    )

    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_superuser')}
    #      ),
    # )
    search_fields = ('email', 'username')
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
