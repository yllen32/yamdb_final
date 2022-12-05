from django.contrib import admin


from .models import User, Categorie, Genre, Title, Comment, Review


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'email')
    list_editable = ('role', 'email')
    exclude = ('groups', 'user_permissions', 'is_staff')
    search_fields = ('username', 'email')
    readonly_fields = ('last_login', 'date_joined', 'password',)


@admin.register(Title, Genre, Categorie, Review, Comment)
class TitlePropertiesAdmin(admin.ModelAdmin):
    pass
