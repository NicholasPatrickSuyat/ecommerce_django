from django.shortcuts import render
from .models import CompanyVideo  # Import the CompanyVideo model
from products.models import Products  # Import the Products model

def home_view(request):
    videos = CompanyVideo.objects.all()  # Fetch all videos from the database
    products = Products.objects.all()  # Fetch all products from the database
    return render(request, 'home/home.html', {'company_videos': videos, 'products': products})

def learn_more_1(request):
    return render(request, 'home/learn1.html')

def learn_more_2(request):
    return render(request, 'home/learn2.html')

def learn_more_3(request):
    return render(request, 'home/learn3.html')

def learn_more_4(request):
    return render(request, 'home/learn4.html')

def about(request):
    return render(request, 'home/about.html')

def terms(request):
    return render(request, 'home/terms.html')

def privacy(request):
    return render(request, 'home/privacypolicy.html')

def patents(request):
    return render(request, 'home/patents.html')

def warranty(request):
    return render(request, 'home/warranty.html')