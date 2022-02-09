from django.contrib import admin

from .models import Follow, User

admin.site.register(Follow)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email',)
