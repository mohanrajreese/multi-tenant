from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 🚀 Multi-Tenant Engine (API + Docs)
    path('', include('tenants.urls')),
]
