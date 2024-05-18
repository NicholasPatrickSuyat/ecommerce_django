from django.shortcuts import render

# not API but just rendering the front-end
def training_view(request):
    return render(request, 'training/training.html')


