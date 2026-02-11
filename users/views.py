from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View

class LoginView(View):
    def get(self, request):
        return render(request, 'auth/login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user:
            # Check if user belongs to this tenant
            if request.tenant and not user.memberships.filter(tenant=request.tenant).exists():
                return render(request, 'auth/login.html', {'error': 'You do not have access to this workspace.'})
            
            login(request, user)
            return redirect('/dashboard/')
        
        return render(request, 'auth/login.html', {'error': 'Invalid credentials'})

class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect('/')
