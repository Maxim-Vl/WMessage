from django.contrib import admin
from .models import CustomUser, Message,MessageFiles, ChatType, Chat, Chat_User
from django.contrib.auth.admin import UserAdmin

admin.site.register(Message)
admin.site.register(MessageFiles)
admin.site.register(ChatType)
admin.site.register(Chat)
admin.site.register(Chat_User)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'is_active',)
    list_filter = ('username', 'email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'first_name', 'last_name', 'email', 'image', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'image', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username',)
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)
