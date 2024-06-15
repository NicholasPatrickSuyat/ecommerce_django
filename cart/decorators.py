from django.core.exceptions import PermissionDenied

def user_is_admin(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap