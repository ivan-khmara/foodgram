from django.contrib import admin
from django.urls import include, path
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/auth/', include('djoser.urls.authtoken')),
    path('admin/', admin.site.urls),
    path('api/', include('djoser.urls')),
    path('api/', include('app.urls')),
]
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)