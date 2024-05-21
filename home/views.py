from django.shortcuts import render
from .models import CompanyVideo # Import the TrainingVideo model

def home_view(request):
    videos = CompanyVideo.objects.all()  # Fetch all videos from the database
    return render(request, 'home/home.html', {'company_videos': videos})