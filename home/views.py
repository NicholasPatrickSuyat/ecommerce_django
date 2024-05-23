from django.shortcuts import render
from .models import CompanyVideo # Import the TrainingVideo model

def home_view(request):
    videos = CompanyVideo.objects.all()  # Fetch all videos from the database
    return render(request, 'home/home.html', {'company_videos': videos})

def learn_more_1(request):
    return render(request, 'home/learn1.html')

def learn_more_2(request):
    return render(request, 'home/learn2.html')

def learn_more_3(request):
    return render(request, 'home/learn3.html')

def learn_more_4(request):
    return render(request, 'home/learn4.html')