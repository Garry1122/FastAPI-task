from django.urls import path, include, re_path

urlpatterns = [
    path("jobs/", include(("app.api.urls", "app.api"))),
]
