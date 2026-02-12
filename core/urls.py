from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth Routes
    path('auth/', include('users.urls')),
    
    # Project Apps
    path('products/', include('products.urls')),
    
    # 🚀 Multi-Tenant Engine (Dashboard + API + Docs)
    path('', include('tenants.urls')),
]
