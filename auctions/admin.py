from django.contrib import admin
from .models import Listings, User

# Register your models here.

class ListingsAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "startingBid", "category", "isOpen")

class UserAdmin (admin.ModelAdmin):
    list_display = ("username", "email")

admin.site.register(Listings, ListingsAdmin)
admin.site.register(User, UserAdmin)