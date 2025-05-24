from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('assets/', include('assets.urls')),
    path('reports/', include('reports.urls')),
    path("dashboard/", include("core.urls", namespace="core")),
    path('', RedirectView.as_view(url='accounts/login/', permanent=False)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
