from django.urls import path, include

from .views import ScrupFacebookPost


urlpatterns = [path("fb/post", ScrupFacebookPost.as_view())]
