from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass
    def __str__ (self):
        return f"{self.username}"

class Category (models.Model):
    category = models.CharField(max_length = 20)

class Listings (models.Model):
    title = models.CharField (max_length = 20)
    description = models.CharField (max_length = 500)
    startingBid = models.DecimalField(max_digits = 9,decimal_places=2)
    currentBid = models.DecimalField(max_digits = 9,decimal_places=2, default= None, blank = True, null = True)
    category = models.ForeignKey (Category, on_delete = models.CASCADE, default = None, related_name = "listings")
    isOpen = models.BooleanField(default = True)
    user = models.ForeignKey (User, on_delete = models.CASCADE, default = 0, related_name = "listings")
    image = models.ImageField(upload_to='images/', blank = True, default = None)

class Bid (models.Model):
    value = models.DecimalField(max_digits = 9,decimal_places=2)
    bidder = models.ForeignKey(User,on_delete = models.CASCADE, default = 0)
    listing = models.ForeignKey (Listings, on_delete = models.CASCADE, default = None, blank = True, related_name = "bids")
    isWinner = models.BooleanField(default = False)

class Comment (models.Model):
    comment = models.CharField(max_length = 500)
    listing = models.ForeignKey(Listings, on_delete = models.CASCADE, default = None, blank = True, related_name = "comments")
    user = models.ForeignKey (User, on_delete = models.CASCADE, default = None)

class Watchlist (models.Model):
    user = models.OneToOneField (User, on_delete= models.CASCADE, default = None, related_name = "watchlist")
    listings = models.ManyToManyField (Listings)
