from django.urls import path, include
#from django.contrib import admin

urlpatterns = [
    path("api/", include("chat.urls")),
    #path("admin/", admin.site.urls),
    path("", include("chat.urls")), 
]
