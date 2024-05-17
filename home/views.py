from django.shortcuts import render

# not API but just rendering the front-end
def home_view(request):
    return render(request, 'home/home.html')


