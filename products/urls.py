from django.urls import path
from .views import ProductListView, CreateProductView

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('new/', CreateProductView.as_view(), name='create_product'),
]
