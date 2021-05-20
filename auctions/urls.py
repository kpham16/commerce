from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name = "post"),
    path("<str:title>/<int:listId>", views.page, name = "page"),
    path("close/<str:title>/<int:listId>", views.close, name = "close"),
    path("bid/<str:title>/<int:listId>", views.placeBid, name = "place_bid"),
    path("comment/<str:title>/<int:listId>", views.comment, name = "comment"),
    path("categories", views.categories, name = "categories"),
    path("categories/search/<str:category>", views.search, name = "search"),
    path("add/<str:title>/<int:listId>", views.add, name = "add"),
    path("watchlist", views.watchlist, name = "watchlist"),
    path ("remove/<str:title>/<int:listId>", views.remove, name = "remove")
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
