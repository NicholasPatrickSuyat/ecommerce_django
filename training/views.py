from django.shortcuts import render
from .models import TrainingVideo

def training_view(request):
    videos = TrainingVideo.objects.all()
    return render(request, 'training/training.html', {'videos': videos})