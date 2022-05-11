from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^supportSystem/', include('supportSystem.urls', namespace='supportSystem')),
    url(r'^admin/', admin.site.urls),
]