from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from .models import User, Listings, Bid, Comment, Category, Watchlist

class ListingForm (forms.Form):
    itemName = forms.CharField(widget = forms.TextInput(
        attrs={'autofocus':True,'class': 'form-control', 'type':'text','name': 'itemName','placeholder':'Item Name'}))

    itemDescription = forms.CharField(widget = forms.Textarea(
        attrs={'autofocus':True,'class': 'form-control', 'type':'text','name': 'itemDescription','placeholder':'Item Description'}))

    startingBid = forms.DecimalField(widget = forms.NumberInput(
        attrs={'autofocus':True,'class': 'form-control', 'type':'number','name': 'startingBid','placeholder':'Starting Bid','value':'$'}))

    category = forms.CharField(widget = forms.TextInput(
        attrs={'autofocus':True,'class': 'form-control', 'type':'text','name': 'category','placeholder':'Category'}))

    image = forms.ImageField(required = False)

class CommentForm (forms.Form):
    comment = forms.CharField(widget = forms.Textarea(
        attrs={'autofocus':True, 'class': 'form-control','id':'commentBox', 'type':'text', 'name': 'comment', 'placeholder': 'Enter a comment'}
    ))

def getCurrent (listing):
    if listing.currentBid == None:
        current = listing.startingBid
    else:
        current = listing.currentBid
    return current

def getCategory (input):
    try:
        Category.objects.get(category = input.capitalize())
    except Category.DoesNotExist:
        newCategory = Category()
        newCategory.category = input.capitalize()
        newCategory.save()

def index(request):
    return render(request, "auctions/index.html",{
        "listings" : Listings.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def categories (request):
    return render (request, "auctions/categories.html",{
        "categories" : Category.objects.order_by('category')
    })

def post (request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        user = request.user
        if form.is_valid():
            listing = Listings()
            listing.title = form.cleaned_data['itemName']
            listing.description = form.cleaned_data['itemDescription']
            listing.startingBid = form.cleaned_data['startingBid']
            listing.currentBid = None
            getCategory (form.cleaned_data['category'])
            listing.category = Category.objects.get(category=form.cleaned_data['category'].capitalize())
            listing.isOpen = True
            listing.user = user
            if form.cleaned_data['image'] != None:
                print("here")
                listing.image = form.cleaned_data['image']
            listing.save()
            return HttpResponseRedirect(reverse("page", args=[listing.title,listing.id]))
            
    return render (request, "auctions/post.html",{
        "form": ListingForm(),
    })

def userView (request, title, listId):
    listing = Listings.objects.get(pk=listId)
    highBidder = ""
    if len(listing.bids.all()) > 0:
        highBid = listing.bids.get(value=listing.currentBid)
        highBidder += highBid.bidder.username
    else:
        highBidder += "There are no bids"
    return render (request, "auctions/userView.html",{
        "listing" : listing,
        "numBids" : len(listing.bids.all()),
        "currentBid" : listing.currentBid,
        "currentBidder" : highBidder,
        "bids" : listing.bids.all(),
        "isOpen" : listing.isOpen,
        "commentForm" : CommentForm(),
        "comments": listing.comments.all()
    })

@login_required(login_url='/login')
def placeBid (request, title, listId):

    listing = Listings.objects.get(pk=listId)
    current = getCurrent(listing)

    if request.POST["bidValue"] == '' or float(request.POST["bidValue"]) <= current:
        return render (request, "auctions/page.html", {
            "listing" : listing,
            "numBids" : len(listing.bids.all()),
            "isOpen": listing.isOpen,
            "message": "Please enter a value higher than the current bid.",
            "commentForm" : CommentForm(),
            "comments": listing.comments.all(),
            "page": True
        })
    else:
        bid = Bid()
        bid.bidder = request.user
        bid.value = request.POST["bidValue"]
        bid.listing = Listings.objects.get(pk=listId)
        bid.save()
        Listings.objects.filter(pk=listId).update(currentBid=bid.value)
        print (Listings.objects.get(pk=listId))

        return page (request, title, listId)

@login_required(login_url='/login')
def comment (request, title, listId):
    print ("i am here")
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = Comment()
        comment.comment = form.cleaned_data["comment"]
        comment.user = request.user
        comment.listing = Listings.objects.get(pk=listId)
        comment.save()

        return page (request, title, listId)

def page (request, title, listId):
    listing = Listings.objects.get(pk=listId)

    if request.user == listing.user:
        return userView (request, title, listId)

    current = getCurrent(listing)
    print (current)

    if listing.isOpen == False:
        userBids = listing.bids.filter(bidder = request.user)
        if userBids.filter(isWinner = True):
            didWin = True
        else: 
            didWin = False
        return render (request, "auctions/page.html", {
            "listing" : listing,
            "numBids" : len(listing.bids.all()),
            "currentBid" : current,
            "isOpen": listing.isOpen,
            "isWinner": didWin,
            "commentForm" : CommentForm(),
            "comments": listing.comments.all(),
            "page": True
        })
    else:
        return render (request, "auctions/page.html", {
            "listing" : listing,
            "numBids" : len(listing.bids.all()),
            "currentBid" : listing.currentBid,
            "isOpen": listing.isOpen,
            "commentForm" : CommentForm(),
            "comments": listing.comments.all(),
            "page": True
        })
            
def close (request, title, listId):
    listing = Listings.objects.filter(pk=listId)
    listing.update(isOpen = False)
    newList = Listings.objects.get(pk=listId)

    if len(newList.bids.all()) > 0:
        highBid = newList.bids.get(value=newList.currentBid)
        highBidder = highBid.bidder.username
        winBid = newList.bids.filter(value=newList.currentBid)
        winBid.update(isWinner = True)

    return page (request, title, listId)

def search (request, category):
    catObj = Category.objects.get(category = category)
    return render (request, "auctions/search.html", {
        "posts": Listings.objects.filter(category=catObj)
    })

def add (request, title, listId):
    print("here1")
    user = request.user
    listing = Listings.objects.get(pk=listId)
    try:
        watchlist = user.watchlist
        print("here2")
        watchlist.listings.add(listing)

    except Watchlist.DoesNotExist:
        print("here3yeah")
        user.watchlist = Watchlist()
        watchlist = user.watchlist
        watchlist.user = user
        watchlist.save()
        watchlist.listings.add(listing)

    return page (request, title, listId)

def watchlist (request):
    print("here4")
    user = request.user
    try:
        watchlist = user.watchlist
        return render (request, "auctions/watchlist.html",{
            "watchlist": watchlist,
            "listings": watchlist.listings.all()
        })
    except Watchlist.DoesNotExist:
        watchlist = None
        return render (request, "auctions/watchlist.html",{
            "watchlist": watchlist,
            "listings": None
    })


def remove (request, title, listId):
    user = request.user
    watchlist = user.watchlist
    watchlist.listings.exclude(pk=listId)
    return render (request, "auctions/watchlist.html",{
        "watchlist": watchlist,
        "listings": watchlist.listings.exclude(pk=listId)
    })