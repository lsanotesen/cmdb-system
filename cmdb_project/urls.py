from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cmdb/', include('cmdb.urls')),
    path('', RedirectView.as_view(url='/cmdb/', permanent=False)),
]
