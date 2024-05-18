from django.shortcuts import render

# not API but just rendering the front-end
def user_view(request):
    return render(request, 'user/user.html')



