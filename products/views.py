from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from tenants.decorators import tenant_permission_required
from django.utils.decorators import method_decorator
from .models import Product

class ProductListView(LoginRequiredMixin, View):
    def get(self, request):
        products = Product.objects.all().order_by('-created_at')
        return render(request, 'products/list.html', {'products': products})

class CreateProductView(LoginRequiredMixin, View):
    @method_decorator(tenant_permission_required('add_product'))
    def get(self, request):
        return render(request, 'products/create.html')
    
    @method_decorator(tenant_permission_required('add_product'))
    def post(self, request):
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        
        Product.objects.create(
            tenant=request.tenant,
            name=name,
            description=description,
            price=price,
            image=image
        )
        return redirect('product_list')
